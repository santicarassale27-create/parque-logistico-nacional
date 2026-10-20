"""
Genera el plano 3D (isométrico) del predio de Itapeby 3170 para parque.html.

NO es parte de la web: es una herramienta para cuando cambien los depósitos.
Cómo se usa:
  1. Editar la lista DEPOSITOS (y ESPACIOS si hace falta) de abajo.
  2. Correr:  python3 herramientas/generar-plano.py
  3. El programa reemplaza el plano dentro de parque.html (entre los
     comentarios <!-- PLANO-3D:INICIO --> y <!-- PLANO-3D:FIN -->).

Coordenadas: el predio mide 1000 (largo, x) por 260 (ancho, y) "unidades".
x crece hacia la derecha del plano; y crece hacia la calle (adelante).
"""

import re
from pathlib import Path

# ---------------------------------------------------------------
# Datos (editar acá)
# estado: operando | confirmada | negociacion | libre
# x, y, ancho, fondo, alto: posición y tamaño del depósito
# etiqueta: dónde va el cartel (cx, cy en el dibujo final, 1260x720).
# Regla: poner el cartel a la DERECHA del depósito (cx mayor que el punto de la línea)
# para que la línea entre al círculo por la izquierda y no cruce el texto.
# ---------------------------------------------------------------
DEPOSITOS = [
    {"n": 5, "nombre": "Local disponible", "estado": "libre",
     "x": 175, "y": 35, "ancho": 120, "fondo": 85, "alto": 34, "etiqueta": (380, 190)},
    {"n": 6, "nombre": "Local disponible", "estado": "libre",
     "x": 325, "y": 35, "ancho": 120, "fondo": 85, "alto": 34, "etiqueta": (480, 110)},
    {"n": 3, "nombre": "Droguería Uruguay S.A.", "estado": "confirmada",
     "x": 485, "y": 20, "ancho": 90, "fondo": 195, "alto": 56, "etiqueta": (640, 650)},
    {"n": 2, "nombre": "Laboratorio Gador S.A.", "estado": "operando",
     "x": 615, "y": 20, "ancho": 80, "fondo": 120, "alto": 56, "etiqueta": (680, 36)},
    {"n": 4, "nombre": "Laboratorio farmacéutico", "estado": "negociacion",
     "x": 725, "y": 20, "ancho": 80, "fondo": 150, "alto": 50, "etiqueta": (970, 36)},
    {"n": 1, "nombre": "Fármaco Uruguayo S.A.", "estado": "operando",
     "x": 835, "y": 20, "ancho": 100, "fondo": 185, "alto": 62, "etiqueta": (1000, 158)},
]

ESTADOS = {
    "operando": "Operando",
    "confirmada": "Confirmada",
    "negociacion": "En negociación",
    "libre": "A definir",
}

# Espacios públicos con cartel propio
ESPACIOS = [
    {"id": "cancha", "nombre": "Cancha de fútbol", "detalle": "Para los niños del barrio",
     "punto": (60, 110), "etiqueta": (300, 622)},
    {"id": "plaza", "nombre": "Plaza pública", "detalle": "Abierta a la comunidad",
     "punto": (935, 238), "etiqueta": (1000, 600)},
]

# ---------------------------------------------------------------
# Proyección isométrica: (x, y, z) del predio -> (X, Y) en pantalla
# ---------------------------------------------------------------
OX, OY, KX, KY = 120, 500, 0.72, 0.36


def p(x, y, z=0):
    return (round(OX + (x + y) * KX, 1), round(OY + (y - x) * KY - z, 1))


def pts(*coords):
    return " ".join(f"{a},{b}" for a, b in coords)


def caja(x, y, w, d, h):
    """Devuelve los polígonos de las 3 caras visibles de un bloque."""
    x1, y1 = x + w, y + d
    techo = pts(p(x, y, h), p(x1, y, h), p(x1, y1, h), p(x, y1, h))
    frente = pts(p(x, y1, 0), p(x1, y1, 0), p(x1, y1, h), p(x, y1, h))   # cara hacia la calle
    lado = pts(p(x, y, 0), p(x, y1, 0), p(x, y1, h), p(x, y, h))          # cara izquierda
    return techo, frente, lado


def poligono_suelo(coords, z=0):
    return pts(*(p(a, b, z) for a, b in coords))


def cartel(n, titulo, sub, clase_sub, cx, cy, ancla, data):
    """Línea con quiebre (vertical y horizontal) desde el depósito hasta el cartel."""
    ax, ay = ancla
    lado = -1 if cx > ax else 1          # de qué lado del círculo entra la línea
    fin = (cx + lado * 32, cy)
    linea = pts((ax, ay), (ax, cy), fin)
    texto_x = cx + 42
    return f'''
      <g class="cartel" {data} tabindex="0">
        <polyline class="cartel-linea" points="{linea}" pathLength="1"/>
        <circle class="cartel-punto" cx="{ax}" cy="{ay}" r="5"/>
        <circle class="cartel-foto" cx="{cx}" cy="{cy}" r="30"/>
        <text class="cartel-num" x="{cx}" y="{cy + 7}">{n}</text>
        <text class="cartel-titulo" x="{texto_x}" y="{cy - 4}">{titulo}</text>
        <text class="cartel-sub {clase_sub}" x="{texto_x}" y="{cy + 16}">{sub}</text>
      </g>'''


def generar():
    out = []
    # Plataforma del predio (con espesor)
    sitio = [(0, 0), (1000, 0), (1000, 260), (0, 205)]
    out.append(f'<polygon class="iso-base-lado" points="{pts(p(0,205,0), p(1000,260,0), p(1000,260,-14), p(0,205,-14))}"/>')
    out.append(f'<polygon class="iso-base-lado2" points="{pts(p(0,0,0), p(0,205,0), p(0,205,-14), p(0,0,-14))}"/>')
    out.append(f'<polygon class="iso-base" points="{poligono_suelo(sitio)}"/>')
    # Verde de la cancha, calle interna y plaza
    out.append(f'<polygon class="iso-verde" points="{poligono_suelo([(0,0),(120,0),(120,215),(0,205)])}"/>')
    out.append(f'<polygon class="iso-cancha" points="{poligono_suelo([(18,28),(104,28),(104,185),(18,185)])}"/>')
    out.append(f'<polyline class="iso-cancha-linea" points="{poligono_suelo([(18,106),(104,106)])}"/>')
    out.append(f'<polygon class="iso-cancha-linea" points="{poligono_suelo([(18,28),(104,28),(104,185),(18,185)])}"/>')
    out.append(f'<polygon class="iso-calle" points="{poligono_suelo([(128,0),(150,0),(150,217),(128,215)])}"/>')
    out.append(f'<polygon class="iso-verde" points="{poligono_suelo([(870,222),(1000,222),(1000,260),(870,249)])}"/>')
    # Zona de maniobra frente a los depósitos
    out.append(f'<polygon class="iso-patio" points="{poligono_suelo([(470,215),(1000,215),(1000,222),(470,222)])}"/>')
    # Árboles (adelante, sobre la calle)
    for tx in range(180, 460, 46):
        a, b = p(tx, 175, 0)
        out.append(f'<ellipse class="iso-arbol-sombra" cx="{a+6}" cy="{b+3}" rx="11" ry="5"/>'
                   f'<circle class="iso-arbol" cx="{a}" cy="{b-9}" r="10"/>')
    # Depósitos: de atrás hacia adelante para que se tapen bien
    for dep in sorted(DEPOSITOS, key=lambda d: (d["y"] + d["fondo"] / 2) - (d["x"] + d["ancho"] / 2)):
        techo, frente, lado = caja(dep["x"], dep["y"], dep["ancho"], dep["fondo"], dep["alto"])
        out.append(f'''<g class="lote lote--{dep["estado"]}" data-lote="{dep["n"]}" tabindex="0" aria-label="{dep["n"]}. {dep["nombre"]}">
        <polygon class="cara-lado" points="{lado}"/><polygon class="cara-frente" points="{frente}"/><polygon class="cara-techo" points="{techo}"/></g>''')
    # Carteles
    for dep in DEPOSITOS:
        ancla = p(dep["x"] + dep["ancho"] / 2, dep["y"] + dep["fondo"] / 2, dep["alto"])
        out.append(cartel(dep["n"], dep["nombre"], ESTADOS[dep["estado"]], f'estado-txt--{dep["estado"]}',
                          *dep["etiqueta"], ancla, f'data-lote="{dep["n"]}"'))
    for esp in ESPACIOS:
        ancla = p(*esp["punto"], 0)
        out.append(cartel("●", esp["nombre"], esp["detalle"], "estado-txt--verde",
                          *esp["etiqueta"], ancla, f'data-lote="{esp["id"]}"'))
    cuerpo = "\n        ".join(out)
    return f'''<!-- PLANO-3D:INICIO (generado por herramientas/generar-plano.py: no editar a mano) -->
      <svg class="pq-iso" viewBox="0 0 1260 720" role="img" aria-labelledby="plano-titulo">
        <title id="plano-titulo">Plano en 3D del predio de Itapeby 3170 con las empresas de cada depósito</title>
        {cuerpo}
      </svg>
      <!-- PLANO-3D:FIN -->'''


if __name__ == "__main__":
    archivo = Path(__file__).resolve().parent.parent / "parque.html"
    html = archivo.read_text(encoding="utf-8")
    nuevo, n = re.subn(r"<!-- PLANO-3D:INICIO.*?<!-- PLANO-3D:FIN -->", generar(), html, flags=re.S)
    if n != 1:
        raise SystemExit("No encontré los comentarios PLANO-3D en parque.html")
    archivo.write_text(nuevo, encoding="utf-8")
    print("Plano actualizado en parque.html")
