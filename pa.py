import json, os
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'tsiakhe_secure_key_2026'

DB_FILE, VENTAS_FILE, GASTOS_FILE = 'productos.json', 'ventas.json', 'gastos.json'

def cargar_json(f, d):
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file: 
            try: return json.load(file)
            except: return d
    return d

PRODUCTOS = cargar_json(DB_FILE, {"copia": 2.00, "ciber": 10.00})
HISTORIAL = cargar_json(VENTAS_FILE, [])
GASTOS = cargar_json(GASTOS_FILE, [])

def guardar(f, d):
    with open(f, 'w', encoding='utf-8') as file: json.dump(d, file, indent=4, ensure_ascii=False)

USER_AUTH, PASS_AUTH = "TSIAKHE", "T20260038"

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>TSIAKHE POS - Professional</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.3.0/exceljs.min.js"></script>
    <style>
        :root { --p: #2c3e50; --accent: #3498db; --success: #27ae60; --danger: #e74c3c; --bg: #f4f7f6; --warning: #f1c40f; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; overflow: hidden; display: flex; flex-direction: column; height: 100vh; }
        header { background: var(--p); color: white; padding: 0 30px; height: 65px; display: flex; justify-content: space-between; align-items: center; z-index: 100; flex-shrink: 0; }
        nav button { background: none; border: none; color: #bdc3c7; font-weight: 600; padding: 0 20px; height: 65px; cursor: pointer; }
        nav button.active { color: white; border-bottom: 4px solid var(--accent); background: rgba(255,255,255,0.1); }
        .main-wrapper { display: flex; flex: 1; overflow: hidden; }
        .pos-section { flex: 2; padding: 25px; display: flex; flex-direction: column; gap: 20px; overflow: hidden; }
        .slider-publicidad { color: white; padding: 20px 30px; border-radius: 15px; display: flex; align-items: center; gap: 25px; box-shadow: 0 8px 20px rgba(0,0,0,0.1); min-height: 110px; background: var(--p); transition: 0.8s; }
        .input-bar { display: flex; background: white; padding: 15px 20px; border-radius: 12px; gap: 15px; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .search-container { position: relative; flex: 2; }
        .input-bar input { width: 100%; padding: 14px; border: 2px solid #edf2f7; border-radius: 8px; font-size: 16px; outline: none; box-sizing: border-box; }
        .cart-container { flex: 1; background: white; border-radius: 15px; padding: 20px; overflow-y: auto; border: 1px solid #e1e8ed; }
        .checkout-section { width: 350px; background: white; border-left: 1px solid #e1e8ed; padding: 30px; display: flex; flex-direction: column; gap: 10px; }
        .total-box { text-align: center; padding: 25px; background: #ebf5fb; border-radius: 15px; border: 2px solid #d4e6f1; }
        .total-val { font-size: 52px; font-weight: 800; color: var(--p); }
        .admin-view { display: none; padding: 35px; background: white; margin: 25px; border-radius: 20px; flex: 1; overflow-y: auto; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
        .card { padding: 25px; border-radius: 15px; text-align: center; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 15px; border-bottom: 1px solid #eee; text-align: left; }
        .venta-card { background: #fff; padding: 18px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #eee; border-left: 6px solid var(--accent); }
        .pay-input { width: 100%; padding: 12px; border: 2px solid #eee; border-radius: 8px; font-size: 18px; text-align: center; font-weight: bold; outline: none; }
        .pay-input:focus { border-color: var(--accent); }
        .change-box { background: #fdf2e9; border: 1px solid #fad7a0; padding: 10px; border-radius: 8px; text-align: center; color: #e67e22; font-weight: bold; }
        footer { background: #fff; padding: 10px 30px; border-top: 1px solid #e1e8ed; display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #7f8c8d; flex-shrink: 0; }
    </style>
</head>
<body>
    <header>
        <div style="font-size: 22px; font-weight: 800;"><i class="fas fa-microchip"></i> TSIAKHE POS</div>
        <nav>
            <button onclick="tab('pos')" id="n-pos" class="active">VENTAS</button>
            <button onclick="tab('adm')" id="n-adm">INVENTARIO</button>
            <button onclick="tab('rep')" id="n-rep">REPORTES</button>
            <button onclick="window.location.href='/logout'" style="color:var(--danger); font-weight:800;">SALIR</button>
        </nav>
    </header>

    <div id="v-pos" class="main-wrapper">
        <div class="pos-section">
            <div id="slider" class="slider-publicidad">
                <div class="slider-icon"><i id="s-icon" class="fas fa-tv" style="font-size:40px;"></i></div>
                <div class="slider-content"><h3 id="s-title" style="margin:0;">TSIAKHE</h3><p id="s-desc" style="margin:5px 0 0 0;">Servicios Digitales</p></div>
            </div>
            <div class="input-bar">
                <div class="search-container">
                    <input type="text" id="p" placeholder="Producto o búsqueda..." autofocus autocomplete="off">
                    <div id="s" style="position:absolute; width:100%; background:white; z-index:1000; display:none; border-radius:8px; box-shadow:0 8px 25px rgba(0,0,0,0.1); max-height:250px; overflow-y:auto;"></div>
                </div>
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-weight:bold; color:var(--p); white-space:nowrap;">Cant:</span>
                    <input type="number" id="c" value="1" min="1" style="width:90px; text-align:center; font-weight:800; padding:14px; border:2px solid #edf2f7; border-radius:8px;">
                </div>
                <button onclick="add()" style="background:var(--accent); color:white; border:none; height:50px; width:55px; border-radius:10px; cursor:pointer; font-size:22px;"><i class="fas fa-plus"></i></button>
            </div>
            <div class="cart-container" id="items"></div>
        </div>
        <div class="checkout-section">
            <div class="total-box"><div id="tL" class="total-val">$0.00</div></div>
            <div style="margin: 10px 0; display: flex; flex-direction: column; gap: 8px;">
                <label style="font-size: 12px; font-weight: bold; color: var(--p);">PAGO CON:</label>
                <input type="number" id="efectivoRecibido" class="pay-input" placeholder="$0.00" oninput="calcCambio()">
                <div id="cambioDisplay" class="change-box">CAMBIO: $0.00</div>
            </div>
            <button onclick="sell()" style="width:100%; padding:18px; border-radius:12px; border:none; font-size:18px; font-weight:700; cursor:pointer; background:var(--success); color:white;">COBRAR (F2)</button>
            <button onclick="registrarSalida()" style="background:white; color:var(--danger); border:2px solid var(--danger); padding:12px; border-radius:10px; font-weight:bold; cursor:pointer; margin-top:5px;">GASTO</button>
            <button onclick="vaciarCarrito()" style="background:none; border:none; color:#95a5a6; cursor:pointer; font-weight:bold; margin-top:10px; text-decoration:underline;">VACIAR CARRITO</button>
        </div>
    </div>

    <div id="v-adm" class="admin-view">
        <h2 style="color:var(--p);"><i class="fas fa-boxes"></i> Inventario</h2>
        <div style="display:flex; gap:10px; margin-bottom:25px; background:#f9f9f9; padding:20px; border-radius:15px;">
            <input type="text" id="nN" placeholder="Nombre" style="flex:2; padding:12px; border-radius:8px; border:1px solid #ddd;">
            <input type="number" id="nP" placeholder="Precio $" style="flex:1; padding:12px; border-radius:8px; border:1px solid #ddd;">
            <button onclick="sP()" style="background:var(--accent); color:white; padding:0 30px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">AÑADIR</button>
        </div>
        <input type="text" id="invBus" oninput="filtrarInv()" placeholder="🔍 Buscar en inventario..." style="width:100%; padding:15px; border-radius:10px; border:2px solid var(--accent); margin-bottom:20px; outline:none;">
        <table>
            <thead><tr><th>Producto</th><th>Precio</th><th>Acción</th></tr></thead>
            <tbody id="lA"></tbody>
        </table>
    </div>

    <div id="v-rep" class="admin-view">
        <div style="margin-bottom: 20px; background: #f1f8ff; padding: 15px; border-radius: 12px; display: flex; align-items: center; gap: 15px;">
            <span style="font-weight: bold; color: var(--p);">📅 Ver historial de:</span>
            <input type="date" id="fechaBusqueda" onchange="cargarRep()" style="padding: 10px; border: 1px solid #ccc; border-radius: 8px;">
            <button onclick="cargarRep()" style="background: var(--p); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">Actualizar</button>
        </div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:20px; margin-bottom:25px;">
            <div class="card" style="background:#2c3e50;"><h4>Turno (Caja)</h4><p id="r-tur" style="font-size:24px; font-weight:bold;">$0.00</p></div>
            <div class="card" style="background:#27ae60;"><h4>Venta Seleccionada</h4><p id="r-dia" style="font-size:24px; font-weight:bold;">$0.00</p></div>
            <div class="card" style="background:#e74c3c;"><h4>Gastos</h4><p id="r-gas" style="font-size:24px; font-weight:bold;">$0.00</p></div>
            <div class="card" style="background:#f1c40f; color:#2c3e50;"><h4>Diferencia</h4><p id="r-dif" style="font-size:24px; font-weight:bold;">$0.00</p></div>
        </div>
        <div style="display:flex; gap:10px; margin-bottom:25px; align-items:center;">
            <button onclick="arqueoCaja()" style="background:var(--warning); color:#2c3e50; border:none; padding:12px 25px; border-radius:10px; font-weight:bold; cursor:pointer;"><i class="fas fa-calculator"></i> ARQUEO</button>
            <button onclick="cerrarTurno()" style="background:var(--danger); color:white; border:none; padding:12px 25px; border-radius:10px; font-weight:bold; cursor:pointer;">CERRAR CORTE</button>
            <button onclick="exportarExcel()" style="background:var(--success); color:white; border:none; padding:12px 25px; border-radius:10px; font-weight:bold; cursor:pointer;"><i class="fas fa-file-excel"></i> EXCEL</button>
        </div>
        <div id="lH"></div>
    </div>

    <footer>
        <div><i class="fas fa-terminal"></i> Terminal Activa: <b>01</b> | Usuario: <b>TSIAKHE</b></div>
        <div><i class="far fa-calendar-alt"></i> <span id="footer-date"></span></div>
        <div>TSIAKHE Professional POS &copy; 2026</div>
    </footer>

    <script>
        let cart = [], cache = {}, gV = [], gG = [], difArc = 0;
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function bip() {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.frequency.value = 880; gain.gain.value = 0.1;
            osc.start(); 
            setTimeout(() => { osc.stop(); osc.disconnect(); }, 100);
        }
        const slides = [
            { t: "Recargas Multimarca", d: "Telcel, Movistar, Bait y más.", i: "fa-mobile-retro", g: "linear-gradient(135deg, #c62828, #1565c0)" },
            { t: "Pago de Servicios", d: "Paga tu recibo de CFE y Agua aquí.", i: "fa-bolt-lightning", g: "linear-gradient(135deg, #1b5e20, #43a047)" },
            { t: "Copias e Impresiones", d: "Calidad láser b/n y color.", i: "fa-print", g: "linear-gradient(135deg, #0d47a1, #1e88e5)" }
        ];
        let cS = 0;
        function rotSlider() {
            const s = slides[cS]; const el = document.getElementById('slider');
            if(!el) return;
            el.style.opacity = '0.4';
            setTimeout(() => {
                document.getElementById('s-title').innerText = s.t;
                document.getElementById('s-desc').innerText = s.d;
                document.getElementById('s-icon').className = `fas ${s.i}`;
                el.style.background = s.g; el.style.opacity = '1';
                cS = (cS + 1) % slides.length;
            }, 400);
        }
        setInterval(rotSlider, 5000);
        function tab(t) {
            ['pos', 'adm', 'rep'].forEach(x => {
                document.getElementById('v-'+x).style.display = (x===t) ? (x==='pos'?'flex':'block') : 'none';
                document.getElementById('n-'+x).className = (x===t) ? 'active' : '';
            });
            if(t==='rep') cargarRep();
            if(t==='adm') loadA();
        }
        function loadA() {
            fetch('/list_p').then(r => r.json()).then(d => {
                cache = d;
                const b = document.getElementById('lA'); b.innerHTML = '';
                Object.entries(d).sort().forEach(([n, p]) => {
                    b.innerHTML += `<tr><td style="text-transform:uppercase; font-weight:700;">${n}</td><td>$${parseFloat(p).toFixed(2)}</td><td><button onclick="delP('${n}')" style="color:red; background:none; border:none; cursor:pointer;"><i class="fas fa-trash"></i></button></td></tr>`;
                });
            });
        }
        function sP() {
            const n = document.getElementById('nN').value; const p = document.getElementById('nP').value;
            if(!n || !p) return;
            fetch('/add_p', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({n, p:parseFloat(p)})}).then(() => { loadA(); document.getElementById('nN').value=''; document.getElementById('nP').value=''; });
        }
        function delP(n) { if(confirm("¿Eliminar?")) fetch('/del_p', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({n})}).then(() => loadA()); }
        function filtrarInv() {
            const q = document.getElementById('invBus').value.toLowerCase();
            document.querySelectorAll('#lA tr').forEach(f => f.style.display = f.innerText.toLowerCase().includes(q) ? '' : 'none');
        }
        document.getElementById('p').oninput = function() {
            const v = this.value.toLowerCase().trim(); const sB = document.getElementById('s'); sB.innerHTML = '';
            if(!v) { sB.style.display='none'; return; }
            const ms = Object.entries(cache).filter(([n]) => n.includes(v));
            ms.forEach(([n, p]) => {
                const d = document.createElement('div'); d.style.padding='15px'; d.style.cursor='pointer'; d.style.borderBottom='1px solid #f0f0f0';
                d.innerHTML=`<div style="display:flex; justify-content:space-between;"><b>${n.toUpperCase()}</b><span>$${p.toFixed(2)}</span></div>`;
                d.onclick=()=>{ 
                    document.getElementById('p').value=n; 
                    sB.style.display='none'; 
                    document.getElementById('c').focus(); 
                    document.getElementById('c').select();
                };
                sB.appendChild(d);
            });
            sB.style.display = ms.length ? 'block' : 'none';
        };
        document.getElementById('p').onkeydown = (e) => { 
            if(e.key==='Enter') { 
                e.preventDefault();
                document.getElementById('c').focus(); 
                document.getElementById('c').select();
            } 
        };
        document.getElementById('c').onkeydown = (e) => { 
            if(e.key==='Enter') add(); 
        };
        function add() {
            const n = document.getElementById('p').value.toLowerCase().trim();
            const c = parseFloat(document.getElementById('c').value) || 1;
            const p = cache[n];
            if(p !== undefined) {
                bip();
                cart.push({n: n.toUpperCase(), c, p, s: p*c});
                renderCart();
                document.getElementById('p').value = ''; 
                document.getElementById('c').value = '1';
                document.getElementById('p').focus();
            }
        }
        function renderCart() {
            const b = document.getElementById('items'); const tL = document.getElementById('tL');
            b.innerHTML = ''; let t = 0;
            cart.forEach((i) => {
                t += i.s;
                b.innerHTML = `<div style="display:flex; justify-content:space-between; padding:15px; border-bottom:1px solid #eee;"><span><b>${i.c}x</b> ${i.n}</span><b>$${i.s.toFixed(2)}</b></div>` + b.innerHTML;
            });
            tL.innerText = `$${t.toFixed(2)}`;
            calcCambio();
        }
        function calcCambio() {
            const total = cart.reduce((a,b)=>a+b.s,0);
            const pago = parseFloat(document.getElementById('efectivoRecibido').value) || 0;
            const cambio = pago > total ? pago - total : 0;
            document.getElementById('cambioDisplay').innerText = `CAMBIO: $${cambio.toFixed(2)}`;
            document.getElementById('cambioDisplay').style.color = pago >= total && total > 0 ? 'var(--success)' : '#e67e22';
        }
        function sell() {
            if(!cart.length) return;
            const total = cart.reduce((a,b)=>a+b.s,0);
            const pago = parseFloat(document.getElementById('efectivoRecibido').value) || 0;
            if (pago < total) { alert("El pago es menor al total."); document.getElementById('efectivoRecibido').focus(); return; }
            bip();
            fetch('/reg_venta', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({total, items:[...cart], fecha: new Date().toLocaleString()})})
            .then(() => { cart=[]; document.getElementById('efectivoRecibido').value = ''; renderCart(); });
        }
        function registrarSalida() {
            const d = prompt("Concepto:"); const m = parseFloat(prompt("Monto:"));
            if(!d || isNaN(m)) return;
            fetch('/reg_gasto', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({desc: d, monto: m, fecha: new Date().toLocaleString()})}).then(() => { alert("Gasto registrado"); cargarRep(); });
        }
        function arqueoCaja() {
            const ef = parseFloat(prompt("Efectivo total en caja:"));
            if(isNaN(ef)) return;
            const tTur = parseFloat(document.getElementById('r-tur').innerText.replace('$',''));
            difArc = ef - tTur;
            fetch('/reg_venta', {
                method:'POST', 
                headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({
                    total: 0, 
                    items: [{n: "EFECTIVO INGRESADO: $" + ef.toFixed(2), c: 1, p: ef, s: 0}], 
                    fecha: new Date().toLocaleString(),
                    tipo: 'arqueo',
                    diferencia: difArc,
                    efectivo_real: ef
                })
            }).then(() => { cargarRep(); alert("Arqueo guardado. Diferencia: $" + difArc.toFixed(2)); });
        }
        function cargarRep() {
            const inputDate = document.getElementById('fechaBusqueda').value; 
            if (!inputDate) {
                const now = new Date();
                const offset = now.getTimezoneOffset() * 60000;
                document.getElementById('fechaBusqueda').value = (new Date(now - offset)).toISOString().slice(0, 10);
            }
            const selectedDate = document.getElementById('fechaBusqueda').value;
            const [ySel, mSel, dSel] = selectedDate.split('-').map(Number);
            Promise.all([fetch('/list_h').then(r=>r.json()), fetch('/list_g').then(r=>r.json())]).then(([ventas, gastos]) => {
                gV = ventas; gG = gastos;
                const bH = document.getElementById('lH'); bH.innerHTML = '';
                let tTur = 0, tDia = 0, tGas = 0, ultimaDif = 0;
                ventas.forEach(v => {
                    if(v.estado === 'abierto') tTur += v.t;
                    if(v.tipo === 'arqueo' && v.estado === 'abierto') ultimaDif = v.diferencia || 0;
                    const [dVen, mVen, yVen] = v.f.split(',')[0].split('/').map(Number);
                    if(dVen === dSel && mVen === mSel && yVen === ySel) {
                        if(v.tipo !== 'arqueo') tDia += v.t;
                        const icon = v.tipo === 'arqueo' ? 'fa-calculator' : 'fa-shopping-cart';
                        const color = v.tipo === 'arqueo' ? 'var(--warning)' : 'var(--success)';
                        bH.innerHTML = `<div class="venta-card" style="border-left-color:${color}"><div style="display:flex; justify-content:space-between;"><b><i class="fas ${icon}"></i> ${v.f}</b><b style="color:${color};">${v.tipo==='arqueo' ? 'ARQUEO (Dif: $'+v.diferencia.toFixed(2)+')' : '+$'+v.t.toFixed(2)}</b></div><div style="font-size:13px; color:#666;">${(v.items || []).map(i=>i.n).join(', ')}</div></div>` + bH.innerHTML;
                    }
                });
                gastos.forEach(g => {
                    if(g.estado === 'abierto') tTur -= g.monto;
                    const [dGas, mGas, yGas] = g.f.split(',')[0].split('/').map(Number);
                    if(dGas === dSel && mGas === mSel && yGas === ySel) {
                        tGas += g.monto;
                        bH.innerHTML = `<div class="venta-card" style="border-left-color:var(--danger);"><div style="display:flex; justify-content:space-between;"><b><i class="fas fa-minus-circle"></i> ${g.f}</b><b style="color:var(--danger);">-$${g.monto.toFixed(2)}</b></div><div style="font-size:13px; color:#666;">${g.desc}</div></div>` + bH.innerHTML;
                    }
                });
                document.getElementById('r-tur').innerText = `$${tTur.toFixed(2)}`;
                document.getElementById('r-dia').innerText = `$${tDia.toFixed(2)}`;
                document.getElementById('r-gas').innerText = `$${tGas.toFixed(2)}`;
                document.getElementById('r-dif').innerText = `$${ultimaDif.toFixed(2)}`;
            });
        }
        async function exportarExcel() {
            try {
                if (typeof ExcelJS === 'undefined') { alert("Error: Librería no cargada."); return; }
                const inputDate = document.getElementById('fechaBusqueda').value;
                if(!inputDate) return;
                const [ySel, mSel, dSel] = inputDate.split('-').map(Number);
                const wb = new ExcelJS.Workbook();
                const ws = wb.addWorksheet('Corte de Caja');
                ws.columns = [
                    {header:'Fecha/Hora', key:'f', width:25}, 
                    {header:'Tipo', key:'t', width:15}, 
                    {header:'Producto/Concepto', key:'d', width:45}, 
                    {header:'Precio Unit.', key:'p', width:15},
                    {header:'Cant.', key:'c', width:10},
                    {header:'Subtotal', key:'m', width:15}
                ];
                ws.getRow(1).font = { bold: true };
                let granTotal = 0;
                gV.forEach(v => {
                    const [dVen, mVen, yVen] = v.f.split(',')[0].split('/').map(Number);
                    if(dVen === dSel && mVen === mSel && yVen === ySel) {
                        if(v.tipo === 'arqueo') {
                            let det = (v.items && v.items.length > 0) ? v.items[0].n : "ARQUEO";
                            const dif = v.diferencia || 0;
                            const row = ws.addRow({f: v.f, t: 'ARQUEO', d: det, p: 0, c: 1, m: dif});
                            row.getCell(6).font = { color: { argb: dif >= 0 ? 'FF27AE60' : 'FFE74C3C' }, bold: true };
                            granTotal += dif;
                        } else {
                            v.items.forEach(item => { 
                                ws.addRow({f: v.f, t: 'VENTA', d: item.n, p: item.p, c: item.c, m: item.s}); 
                                granTotal += item.s;
                            });
                        }
                    }
                });
                gG.forEach(g => {
                    const [dGas, mGas, yGas] = g.f.split(',')[0].split('/').map(Number);
                    if(dGas === dSel && mGas === mSel && yGas === ySel) {
                        const row = ws.addRow({f:g.f, t:'GASTO', d:g.desc, p: g.monto, c: 1, m: -g.monto});
                        row.getCell(6).font = { color: { argb: 'FFFF0000' } };
                        granTotal -= g.monto;
                    }
                });
                
                ws.addRow([]);
                const totalRow = ws.addRow({d: 'TOTAL DEL DÍA (BALANCE)', m: granTotal});
                totalRow.font = { bold: true, size: 12 };
                totalRow.getCell(6).fill = { type: 'pattern', pattern:'solid', fgColor:{argb:'FFF1C40F'} };

                const buffer = await wb.xlsx.writeBuffer();
                const blob = new Blob([buffer], {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = `Reporte_${inputDate}.xlsx`;
                link.click();
            } catch (err) { alert("Error al generar Excel: " + err.message); }
        }
        function cerrarTurno() { if(confirm("¿Cerrar corte?")) fetch('/cerrar_turno', {method:'POST'}).then(() => { difArc=0; cargarRep(); }); }
        function vaciarCarrito() { cart=[]; renderCart(); }
        window.onload = () => { 
            loadA(); rotSlider(); 
            document.getElementById('footer-date').innerText = new Date().toLocaleDateString();
        };
        window.onkeydown = (e) => { if(e.key === 'F2') sell(); };
    </script>
</body>
</html>
"""

# [Rutas de Flask idénticas al original...]
@app.route('/')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['user'] == USER_AUTH and request.form['pass'] == PASS_AUTH:
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso - TSIAKHE</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; height: 100vh; display: flex; align-items: center; justify-content: center; background: #2c3e50; }
        .login-card { background: white; padding: 50px; border-radius: 24px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 100%; max-width: 400px; text-align: center; }
        .logo-area { margin-bottom: 30px; }
        .logo-area i { font-size: 50px; color: #3498db; margin-bottom: 15px; }
        .logo-area h2 { margin: 0; color: #2c3e50; font-weight: 800; letter-spacing: 2px; }
        .logo-area p { color: #7f8c8d; font-size: 14px; margin-top: 5px; }
        .input-group { margin-bottom: 20px; position: relative; text-align: left; }
        .input-group label { display: block; margin-bottom: 8px; font-size: 12px; font-weight: bold; color: #2c3e50; text-transform: uppercase; }
        .input-group i { position: absolute; left: 15px; top: 38px; color: #bdc3c7; }
        .input-group input { width: 100%; padding: 12px 12px 12px 40px; border: 2px solid #edf2f7; border-radius: 12px; outline: none; box-sizing: border-box; font-size: 16px; transition: 0.3s; }
        .input-group input:focus { border-color: #3498db; }
        button { width: 100%; padding: 15px; border-radius: 12px; border: none; background: #3498db; color: white; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3); }
        button:hover { background: #2980b9; transform: translateY(-2px); }
        .footer-note { margin-top: 30px; font-size: 12px; color: #bdc3c7; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo-area">
            <i class="fas fa-microchip"></i>
            <h2>TSIAKHE</h2>
            <p>SISTEMA DE GESTIÓN POS</p>
        </div>
        <form method="POST">
            <div class="input-group">
                <label>Usuario</label>
                <i class="fas fa-user"></i>
                <input type="text" name="user" placeholder="Ingresa tu usuario" required autofocus>
            </div>
            <div class="input-group">
                <label>Contraseña</label>
                <i class="fas fa-lock"></i>
                <input type="password" name="pass" placeholder="••••••••" required>
            </div>
            <button type="submit">ACCEDER AL SISTEMA</button>
        </form>
        <div class="footer-note">© 2026 TSIAKHE - Versión 3.0</div>
    </div>
</body>
</html>
""")

@app.route('/logout')
def logout(): session.pop('logged_in', None); return redirect(url_for('login'))

@app.route('/list_p')
def list_p(): return jsonify(PRODUCTOS)
@app.route('/list_h')
def list_h(): return jsonify(HISTORIAL)
@app.route('/list_g')
def list_g(): return jsonify(GASTOS)

@app.route('/reg_venta', methods=['POST'])
def reg_venta():
    d = request.json
    HISTORIAL.append({
        "f": d['fecha'], "t": d['total'], "items": d['items'], "estado": "abierto", 
        "tipo": d.get('tipo', 'venta'), "diferencia": d.get('diferencia', 0), "efectivo_real": d.get('efectivo_real', 0)
    })
    guardar(VENTAS_FILE, HISTORIAL); return jsonify(success=True)

@app.route('/reg_gasto', methods=['POST'])
def reg_gasto():
    d = request.json
    GASTOS.append({"f": d['fecha'], "desc": d['desc'], "monto": d['monto'], "estado": "abierto"})
    guardar(GASTOS_FILE, GASTOS); return jsonify(success=True)

@app.route('/add_p', methods=['POST'])
def add_p():
    d = request.json
    PRODUCTOS[d['n'].lower().strip()] = float(d['p'])
    guardar(DB_FILE, PRODUCTOS); return jsonify(success=True)

@app.route('/del_p', methods=['POST'])
def del_p():
    n = request.json.get('n', '').lower().strip()
    if n in PRODUCTOS: del PRODUCTOS[n]; guardar(DB_FILE, PRODUCTOS)
    return jsonify(success=True)

@app.route('/cerrar_turno', methods=['POST'])
def cerrar_turno():
    for v in HISTORIAL: v['estado'] = 'cerrado'
    for g in GASTOS: g['estado'] = 'cerrado'
    guardar(VENTAS_FILE, HISTORIAL); guardar(GASTOS_FILE, GASTOS)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)