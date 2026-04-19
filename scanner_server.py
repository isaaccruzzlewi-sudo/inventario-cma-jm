from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

NOMBRE_ARCHIVO = "inventario.json"

# ─────────────────────────────────────────
#  DATOS
# ─────────────────────────────────────────
def cargar_datos():
    if os.path.exists(NOMBRE_ARCHIVO):
        with open(NOMBRE_ARCHIVO, "r") as f:
            return json.load(f)
    return {"nombres": [], "precios": [], "cantidades": [], "ventas_del_dia": 0}

def guardar_datos(datos):
    with open(NOMBRE_ARCHIVO, "w") as f:
        json.dump(datos, f, indent=4)

# ─────────────────────────────────────────
#  HTML DEL ESCÁNER (se abre en el iPhone)
# ─────────────────────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>CMA-JM Scanner</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

  :root {
    --bg: #0a0a0a;
    --panel: #141414;
    --border: #222;
    --accent: #00ff88;
    --accent2: #00ccff;
    --danger: #ff4455;
    --text: #f0f0f0;
    --muted: #666;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
    padding: 0 0 40px;
  }

  header {
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    padding: 18px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  header .logo {
    font-family: 'Space Mono', monospace;
    font-size: 14px;
    color: var(--accent);
    letter-spacing: 2px;
  }

  header .sub {
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 1px;
  }

  .section {
    padding: 20px;
  }

  .label {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  /* SCANNER */
  #scanner-wrap {
    position: relative;
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: #000;
    aspect-ratio: 4/3;
  }

  #scanner-wrap video,
  #scanner-wrap canvas {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover;
    position: absolute;
    top: 0; left: 0;
  }

  .scan-line {
    position: absolute;
    left: 10%; right: 10%;
    height: 2px;
    background: var(--accent);
    box-shadow: 0 0 12px var(--accent);
    animation: scanMove 2s ease-in-out infinite;
    z-index: 10;
  }

  @keyframes scanMove {
    0%, 100% { top: 20%; }
    50% { top: 80%; }
  }

  .scan-corner {
    position: absolute;
    width: 24px; height: 24px;
    border-color: var(--accent);
    border-style: solid;
    z-index: 11;
  }
  .scan-corner.tl { top: 12px; left: 12px; border-width: 2px 0 0 2px; }
  .scan-corner.tr { top: 12px; right: 12px; border-width: 2px 2px 0 0; }
  .scan-corner.bl { bottom: 12px; left: 12px; border-width: 0 0 2px 2px; }
  .scan-corner.br { bottom: 12px; right: 12px; border-width: 0 2px 2px 0; }

  /* MANUAL INPUT */
  .input-row {
    display: flex;
    gap: 8px;
    margin-top: 14px;
  }

  input[type="text"] {
    flex: 1;
    background: var(--panel);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 12px 16px;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    outline: none;
    transition: border-color 0.2s;
  }

  input[type="text"]:focus {
    border-color: var(--accent);
  }

  .btn {
    padding: 12px 20px;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: opacity 0.2s;
    letter-spacing: 1px;
  }

  .btn:active { opacity: 0.7; }
  .btn-green { background: var(--accent); color: #000; }
  .btn-blue { background: var(--accent2); color: #000; }
  .btn-red { background: var(--danger); color: #fff; }
  .btn-full { width: 100%; margin-top: 10px; padding: 14px; }

  /* CARRITO */
  #carrito-lista {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 4px;
  }

  .carrito-item {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: slideIn 0.3s ease;
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateY(-8px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .carrito-item .nombre {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: var(--text);
  }

  .carrito-item .precio {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: var(--accent);
  }

  .carrito-item .remove {
    background: none;
    border: none;
    color: var(--danger);
    font-size: 18px;
    cursor: pointer;
    padding: 0 0 0 12px;
  }

  /* TOTAL */
  .total-box {
    background: var(--panel);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .total-box .total-label {
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .total-box .total-valor {
    font-family: 'Space Mono', monospace;
    font-size: 22px;
    color: var(--accent);
  }

  /* TOAST */
  #toast {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%) translateY(80px);
    background: var(--panel);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 12px 24px;
    border-radius: 30px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    transition: transform 0.3s ease;
    z-index: 100;
    white-space: nowrap;
  }

  #toast.show { transform: translateX(-50%) translateY(0); }
  #toast.success { border-color: var(--accent); color: var(--accent); }
  #toast.error { border-color: var(--danger); color: var(--danger); }

  .divider {
    height: 1px;
    background: var(--border);
    margin: 4px 0 20px;
  }

  .empty {
    text-align: center;
    color: var(--muted);
    font-size: 13px;
    padding: 20px;
  }
</style>
</head>
<body>

<header>
  <div>
    <div class="logo">▶ CMA-JM</div>
    <div class="sub">SCANNER DE INVENTARIO</div>
  </div>
</header>

<!-- ESCÁNER -->
<div class="section">
  <div class="label">Cámara</div>
  <div id="scanner-wrap">
    <div class="scan-line"></div>
    <div class="scan-corner tl"></div>
    <div class="scan-corner tr"></div>
    <div class="scan-corner bl"></div>
    <div class="scan-corner br"></div>
  </div>

  <div class="input-row">
    <input type="text" id="manual-input" placeholder="O escribe el producto...">
    <button class="btn btn-green" onclick="agregarManual()">ADD</button>
  </div>
</div>

<div class="divider"></div>

<!-- CARRITO -->
<div class="section">
  <div class="label">Carrito</div>
  <div id="carrito-lista">
    <div class="empty">Escanea un producto para comenzar</div>
  </div>

  <div class="total-box">
    <span class="total-label">Total</span>
    <span class="total-valor" id="total">$0.00</span>
  </div>

  <button class="btn btn-green btn-full" onclick="cobrar()">✓ COBRAR</button>
  <button class="btn btn-red btn-full" onclick="cancelar()">✕ CANCELAR</button>
</div>

<div id="toast"></div>

<script>
  let carrito = [];

  // ── TOAST ──
  function toast(msg, tipo = 'success') {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = `show ${tipo}`;
    setTimeout(() => t.className = '', 2500);
  }

  // ── AGREGAR AL CARRITO ──
  async function agregarProducto(nombre) {
    if (!nombre.trim()) return;

    const res = await fetch('/buscar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre: nombre.trim().toLowerCase() })
    });

    const data = await res.json();

    if (data.ok) {
      carrito.push({ nombre: data.nombre, precio: data.precio, indice: data.indice });
      renderCarrito();
      toast(`✅ ${data.nombre} agregado`);
    } else {
      toast(`❌ ${data.error}`, 'error');
    }
  }

  function agregarManual() {
    const input = document.getElementById('manual-input');
    agregarProducto(input.value);
    input.value = '';
  }

  // ── RENDER CARRITO ──
  function renderCarrito() {
    const lista = document.getElementById('carrito-lista');
    const totalEl = document.getElementById('total');

    if (carrito.length === 0) {
      lista.innerHTML = '<div class="empty">Escanea un producto para comenzar</div>';
      totalEl.textContent = '$0.00';
      return;
    }

    lista.innerHTML = carrito.map((item, i) => `
      <div class="carrito-item">
        <span class="nombre">${item.nombre}</span>
        <span class="precio">$${item.precio.toFixed(2)}</span>
        <button class="remove" onclick="remover(${i})">×</button>
      </div>
    `).join('');

    const total = carrito.reduce((s, i) => s + i.precio, 0);
    totalEl.textContent = `$${total.toFixed(2)}`;
  }

  function remover(i) {
    carrito.splice(i, 1);
    renderCarrito();
  }

  // ── COBRAR ──
  async function cobrar() {
    if (carrito.length === 0) { toast('El carrito está vacío', 'error'); return; }

    const res = await fetch('/cobrar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ carrito })
    });

    const data = await res.json();
    if (data.ok) {
      toast(`💰 Venta de $${data.total.toFixed(2)} realizada`);
      carrito = [];
      renderCarrito();
    } else {
      toast(data.error, 'error');
    }
  }

  // ── CANCELAR ──
  function cancelar() {
    carrito = [];
    renderCarrito();
    toast('Carrito cancelado', 'error');
  }

  // ── QUAGGA ESCÁNER ──
  Quagga.init({
    inputStream: {
      name: "Live",
      type: "LiveStream",
      target: document.getElementById("scanner-wrap"),
      constraints: { facingMode: "environment" }
    },
    decoder: { readers: ["code_128_reader", "ean_reader", "ean_8_reader"] }
  }, function(err) {
    if (err) { console.error(err); return; }
    Quagga.start();
  });

  let ultimoCodigo = '';
  let ultimoTiempo = 0;

  Quagga.onDetected(function(result) {
    const codigo = result.codeResult.code;
    const ahora = Date.now();
    if (codigo === ultimoCodigo && ahora - ultimoTiempo < 2000) return;
    ultimoCodigo = codigo;
    ultimoTiempo = ahora;
    agregarProducto(codigo);
  });

  // Enter en input manual
  document.getElementById('manual-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') agregarManual();
  });
</script>
</body>
</html>
"""

# ─────────────────────────────────────────
#  RUTAS FLASK
# ─────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/buscar", methods=["POST"])
def buscar():
    datos = cargar_datos()
    nombre = request.json.get("nombre", "").lower().strip()

    for i, prod in enumerate(datos["nombres"]):
        if prod and prod.lower() == nombre:
            if datos["cantidades"][i] > 0:
                return jsonify({
                    "ok": True,
                    "nombre": prod.title(),
                    "precio": datos["precios"][i],
                    "indice": i
                })
            else:
                return jsonify({"ok": False, "error": f"Sin stock de {prod}"})

    return jsonify({"ok": False, "error": f"'{nombre}' no existe"})

@app.route("/cobrar", methods=["POST"])
def cobrar():
    datos = cargar_datos()
    carrito = request.json.get("carrito", [])

    if not carrito:
        return jsonify({"ok": False, "error": "Carrito vacío"})

    total = 0
    for item in carrito:
        i = item["indice"]
        if datos["cantidades"][i] > 0:
            datos["cantidades"][i] -= 1
            total += datos["precios"][i]
        else:
            return jsonify({"ok": False, "error": f"Sin stock de {datos['nombres'][i]}"})

    datos["ventas_del_dia"] += total
    guardar_datos(datos)

    return jsonify({"ok": True, "total": total})

# ─────────────────────────────────────────
#  ARRANCAR
# ─────────────────────────────────────────
if __name__ == "__main__":
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    print(f"\n🚀 Servidor corriendo!")
    print(f"📱 Abre esto en tu iPhone: http://{ip}:5000")
    print(f"💻 O en tu Mac: http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
