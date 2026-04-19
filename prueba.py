import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# ─────────────────────────────────────────
#  COLORES Y FUENTES
# ─────────────────────────────────────────
BG         = "#0f0f0f"
PANEL      = "#1a1a1a"
ACCENT     = "#00ff88"
ACCENT2    = "#00ccff"
TEXT       = "#f0f0f0"
MUTED      = "#888888"
DANGER     = "#ff4444"
BORDER     = "#2a2a2a"

FONT_TITLE = ("Courier New", 22, "bold")
FONT_HEAD  = ("Courier New", 12, "bold")
FONT_BODY  = ("Courier New", 11)
FONT_SMALL = ("Courier New", 9)

# ─────────────────────────────────────────
#  DATOS
# ─────────────────────────────────────────
NOMBRE_ARCHIVO = "inventario.json"
inventarios   = []
precios       = []
cantidades    = []
ventas_del_dia = 0

def cargar_datos():
    global inventarios, precios, cantidades, ventas_del_dia
    if os.path.exists(NOMBRE_ARCHIVO):
        with open(NOMBRE_ARCHIVO, "r") as f:
            d = json.load(f)
            inventarios    = d.get("nombres", [])
            precios        = d.get("precios", [])
            cantidades     = d.get("cantidades", [])
            ventas_del_dia = d.get("ventas_del_dia", 0)

def guardar_datos():
    with open(NOMBRE_ARCHIVO, "w") as f:
        json.dump({
            "nombres":       inventarios,
            "precios":       precios,
            "cantidades":    cantidades,
            "ventas_del_dia": ventas_del_dia
        }, f, indent=4)

cargar_datos()

# ─────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────
root = tk.Tk()
root.title("CMA-JM · Sistema de Inventario")
root.geometry("1000x680")
root.configure(bg=BG)
root.resizable(False, False)

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def entry_style(parent, **kw):
    e = tk.Entry(parent, bg=PANEL, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=FONT_BODY,
                 highlightthickness=1, highlightcolor=ACCENT,
                 highlightbackground=BORDER, **kw)
    return e

def btn(parent, text, cmd, color=ACCENT, fg=BG, **kw):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=fg, activebackground=color,
                  font=FONT_HEAD, relief="flat", cursor="hand2",
                  padx=14, pady=6, **kw)
    def on_enter(e): b.config(bg=TEXT)
    def on_leave(e): b.config(bg=color)
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    return b

def label(parent, text, font=FONT_BODY, color=TEXT, **kw):
    return tk.Label(parent, text=text, bg=parent["bg"] if "bg" not in kw else kw.pop("bg"),
                    fg=color, font=font, **kw)

def flash(widget, msg, color=ACCENT):
    widget.config(text=msg, fg=color)
    root.after(3000, lambda: widget.config(text=""))

# ─────────────────────────────────────────
#  CABECERA
# ─────────────────────────────────────────
header = tk.Frame(root, bg=PANEL, height=70)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(header, text="▶  CMA-JM", bg=PANEL, fg=ACCENT,
         font=("Courier New", 20, "bold")).pack(side="left", padx=24, pady=18)
tk.Label(header, text="SISTEMA DE INVENTARIO", bg=PANEL, fg=MUTED,
         font=FONT_SMALL).pack(side="left", pady=22)

ventas_label_header = tk.Label(header, text="", bg=PANEL, fg=ACCENT2, font=FONT_HEAD)
ventas_label_header.pack(side="right", padx=24)

def actualizar_ventas_header():
    ventas_label_header.config(text=f"💰  Ventas del día: ${ventas_del_dia:.2f}")

actualizar_ventas_header()

# ─────────────────────────────────────────
#  CONTENEDOR PRINCIPAL  (sidebar + tabla)
# ─────────────────────────────────────────
main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=0)

# ── SIDEBAR ──────────────────────────────
sidebar = tk.Frame(main, bg=PANEL, width=280)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

label(sidebar, "ACCIONES", font=FONT_SMALL, color=MUTED, bg=PANEL).pack(anchor="w", padx=20, pady=(20,4))
tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20)

# ── campos agregar ──
label(sidebar, "Producto", font=FONT_SMALL, color=MUTED, bg=PANEL).pack(anchor="w", padx=20, pady=(16,2))
e_nombre = entry_style(sidebar, width=26)
e_nombre.pack(padx=20)

label(sidebar, "Precio ($)", font=FONT_SMALL, color=MUTED, bg=PANEL).pack(anchor="w", padx=20, pady=(10,2))
e_precio = entry_style(sidebar, width=26)
e_precio.pack(padx=20)

label(sidebar, "Cantidad", font=FONT_SMALL, color=MUTED, bg=PANEL).pack(anchor="w", padx=20, pady=(10,2))
e_cantidad = entry_style(sidebar, width=26)
e_cantidad.pack(padx=20)

status_agregar = label(sidebar, "", font=FONT_SMALL, color=ACCENT, bg=PANEL)
status_agregar.pack(pady=(6,0))

def agregar():
    global inventarios, precios, cantidades
    nombre = e_nombre.get().lower().strip()
    if not nombre:
        flash(status_agregar, "⚠ Nombre vacío", DANGER); return
    if nombre in inventarios:
        indice = inventarios.index(nombre)
        try:
            cant = int(e_cantidad.get())
            cantidades[indice] += cant
            guardar_datos(); refrescar_tabla()
            flash(status_agregar, f"✅ Stock +{cant}")
        except ValueError:
            flash(status_agregar, "⚠ Cantidad inválida", DANGER)
        return
    try:
        precio = float(e_precio.get())
        cant   = int(e_cantidad.get())
    except ValueError:
        flash(status_agregar, "⚠ Precio/Cantidad inválidos", DANGER); return
    inventarios.append(nombre)
    precios.append(precio)
    cantidades.append(cant)
    guardar_datos(); refrescar_tabla()
    flash(status_agregar, f"✅ '{nombre.title()}' agregado")
    e_nombre.delete(0, "end"); e_precio.delete(0, "end"); e_cantidad.delete(0, "end")

btn(sidebar, "＋  AGREGAR / ACTUALIZAR", agregar).pack(padx=20, pady=10, fill="x")
tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20)

# ── vender ──
label(sidebar, "Vender producto", font=FONT_SMALL, color=MUTED, bg=PANEL).pack(anchor="w", padx=20, pady=(14,2))
e_vender = entry_style(sidebar, width=26)
e_vender.pack(padx=20)

status_vender = label(sidebar, "", font=FONT_SMALL, color=ACCENT, bg=PANEL)
status_vender.pack(pady=(4,0))

def vender():
    global ventas_del_dia
    nombre = e_vender.get().lower().strip()
    for i, prod in enumerate(inventarios):
        if prod and prod.lower() == nombre:
            if cantidades[i] > 0:
                cantidades[i] -= 1
                ventas_del_dia += precios[i]
                guardar_datos(); refrescar_tabla(); actualizar_ventas_header()
                flash(status_vender, f"💰 Vendido ${precios[i]:.2f}")
            else:
                flash(status_vender, "🚫 Sin stock", DANGER)
            e_vender.delete(0, "end"); return
    flash(status_vender, "❌ No existe", DANGER)

btn(sidebar, "⟳  VENDER", vender, color=ACCENT2).pack(padx=20, pady=8, fill="x")
tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=20)

# ── eliminar ──
label(sidebar, "Eliminar producto", font=FONT_SMALL, color=MUTED, bg=PANEL).pack(anchor="w", padx=20, pady=(14,2))
e_eliminar = entry_style(sidebar, width=26)
e_eliminar.pack(padx=20)

status_eliminar = label(sidebar, "", font=FONT_SMALL, color=ACCENT, bg=PANEL)
status_eliminar.pack(pady=(4,0))

def eliminar():
    nombre = e_eliminar.get().lower().strip()
    for i, prod in enumerate(inventarios):
        if prod and prod.lower() == nombre:
            if messagebox.askyesno("Confirmar", f"¿Eliminar '{prod.title()}'?"):
                inventarios.pop(i); precios.pop(i); cantidades.pop(i)
                guardar_datos(); refrescar_tabla()
                flash(status_eliminar, "✅ Eliminado")
            e_eliminar.delete(0, "end"); return
    flash(status_eliminar, "❌ No existe", DANGER)

btn(sidebar, "✕  ELIMINAR", eliminar, color=DANGER, fg=TEXT).pack(padx=20, pady=8, fill="x")

# ─────────────────────────────────────────
#  TABLA DE INVENTARIO
# ─────────────────────────────────────────
right = tk.Frame(main, bg=BG)
right.pack(side="left", fill="both", expand=True, padx=20, pady=20)

label(right, "INVENTARIO", font=FONT_HEAD, color=MUTED, bg=BG).pack(anchor="w")
tk.Frame(right, bg=ACCENT, height=2).pack(fill="x", pady=(2,10))

style = ttk.Style()
style.theme_use("clam")
style.configure("Inv.Treeview",
    background=PANEL, foreground=TEXT,
    fieldbackground=PANEL, rowheight=32,
    font=FONT_BODY, borderwidth=0)
style.configure("Inv.Treeview.Heading",
    background=BG, foreground=ACCENT,
    font=FONT_HEAD, relief="flat")
style.map("Inv.Treeview",
    background=[("selected", "#1e3a2f")],
    foreground=[("selected", ACCENT)])

cols = ("#", "Producto", "Precio", "Stock", "Estado")
tabla = ttk.Treeview(right, columns=cols, show="headings",
                     style="Inv.Treeview", selectmode="browse")

for col in cols:
    tabla.heading(col, text=col)

tabla.column("#",        width=40,  anchor="center")
tabla.column("Producto", width=260, anchor="w")
tabla.column("Precio",   width=100, anchor="center")
tabla.column("Stock",    width=80,  anchor="center")
tabla.column("Estado",   width=120, anchor="center")

scroll = ttk.Scrollbar(right, orient="vertical", command=tabla.yview)
tabla.configure(yscrollcommand=scroll.set)
tabla.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")

def refrescar_tabla():
    for row in tabla.get_children():
        tabla.delete(row)
    for i, (prod, precio, cant) in enumerate(zip(inventarios, precios, cantidades), 1):
        if prod:
            estado = "✅ En stock" if cant > 0 else "🚫 Agotado"
            tag    = "agotado" if cant == 0 else ("bajo" if cant <= 3 else "ok")
            tabla.insert("", "end", values=(i, prod.title(), f"${precio:.2f}", cant, estado), tags=(tag,))
    tabla.tag_configure("ok",      background=PANEL)
    tabla.tag_configure("bajo",    background="#2a1f00")
    tabla.tag_configure("agotado", background="#2a0000")

refrescar_tabla()

# ─────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────
footer = tk.Frame(root, bg=BORDER, height=28)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)
tk.Label(footer, text="CMA-JM © 2025  ·  Python + Tkinter",
         bg=BORDER, fg=MUTED, font=FONT_SMALL).pack(side="right", padx=16, pady=6)

root.mainloop()