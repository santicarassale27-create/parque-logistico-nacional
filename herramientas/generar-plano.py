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
# camiones: cuántos camiones dibujar estacionados en sus portones (0 = ninguno)
# etiqueta: dónde va el cartel (cx, cy en el dibujo final, 1260x720).
# Regla: poner el cartel a la DERECHA del depósito (cx mayor que el punto de la línea)
# para que la línea entre al círculo por la izquierda y no cruce el texto.
# ---------------------------------------------------------------
DEPOSITOS = [
    {"n": 5, "nombre": "Local disponible", "estado": "libre",
     "x": 175, "y": 35, "ancho": 120, "fondo": 85, "alto": 34, "camiones": 0, "etiqueta": (380, 190)},
    {"n": 6, "nombre": "Local disponible", "estado": "libre",
     "x": 325, "y": 35, "ancho": 120, "fondo": 85, "alto": 34, "camiones": 0, "etiqueta": (480, 110)},
    {"n": 3, "nombre": "Droguería Uruguay S.A.", "estado": "confirmada",
     "x": 485, "y": 20, "ancho": 90, "fondo": 165, "alto": 56, "camiones": 2, "etiqueta": (640, 650)},
    {"n": 2, "nombre": "Laboratorio Gador S.A.", "estado": "operando",
     "x": 615, "y": 20, "ancho": 80, "fondo": 120, "alto": 56, "camiones": 1, "etiqueta": (680, 36)},
    {"n": 4, "nombre": "Laboratorio farmacéutico", "estado": "negociacion",
     "x": 725, "y": 20, "ancho": 80, "fondo": 150, "alto": 50, "camiones": 0, "etiqueta": (970, 36)},
    {"n": 1, "nombre": "Fármaco Uruguayo S.A.", "estado": "operando",
     "x": 835, "y": 20, "ancho": 100, "fondo": 170, "alto": 62, "camiones": 2, "etiqueta": (1000, 158)},
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


def caja(x, y, w, d, h, z0=0):
    """Devuelve los polígonos de las 3 caras visibles de un bloque (techo, frente, lado)."""
    x1, y1 = x + w, y + d
    techo = pts(p(x, y, h), p(x1, y, h), p(x1, y1, h), p(x, y1, h))
    frente = pts(p(x, y1, z0), p(x1, y1, z0), p(x1, y1, h), p(x, y1, h))   # cara hacia la calle
    lado = pts(p(x, y, z0), p(x, y1, z0), p(x, y1, h), p(x, y, h))          # cara izquierda
    return techo, frente, lado


def bloque(clase, x, y, w, d, h, z0=0):
    techo, frente, lado = caja(x, y, w, d, h, z0)
    return (f'<g class="{clase}"><polygon class="c-lado" points="{lado}"/>'
            f'<polygon class="c-frente" points="{frente}"/><polygon class="c-techo" points="{techo}"/></g>')


def detalles_deposito(dep):
    """Portones en el frente, ventanas en el costado y claraboyas en el techo."""
    x, y, w, d, h = dep["x"], dep["y"], dep["ancho"], dep["fondo"], dep["alto"]
    x1, y1 = x + w, y + d
    out = []
    # Portones de carga (cara de adelante)
    n = max(1, int(w // 26))
    paso = w / n
    alto_porton = min(22, h * 0.45)
    for i in range(n):
        cx = x + paso * (i + 0.5)
        out.append(f'<polygon class="porton" points="{pts(p(cx-6.5,y1,0), p(cx+6.5,y1,0), p(cx+6.5,y1,alto_porton), p(cx-6.5,y1,alto_porton))}"/>')
    # Franja de ventanas (cara izquierda)
    out.append(f'<polygon class="ventanas" points="{pts(p(x,y+10,h-15), p(x,y1-10,h-15), p(x,y1-10,h-8), p(x,y+10,h-8))}"/>')
    # Claraboyas en el techo
    for f in (0.3, 0.7):
        cx = x + w * f
        out.append(f'<polygon class="claraboya" points="{pts(p(cx-4,y+12,h), p(cx+4,y+12,h), p(cx+4,y1-12,h), p(cx-4,y1-12,h))}"/>')
    return "".join(out)


def camion(cx, y_porton):
    """Camión estacionado de culata contra un portón: caja blanca + cabina."""
    sombra = pts(p(cx-10, y_porton+3, 0), p(cx+11, y_porton+3, 0), p(cx+11, y_porton+50, 0), p(cx-10, y_porton+50, 0))
    return (f'<g class="camion"><polygon class="sombra" points="{sombra}"/>'
            + bloque("camion-caja", cx-7.5, y_porton+2, 15, 34, 19, 3)
            + bloque("camion-cabina", cx-7.5, y_porton+37, 15, 11, 16, 1)
            + f'<polygon class="camion-vidrio" points="{pts(p(cx-6,y_porton+48,9), p(cx+6,y_porton+48,9), p(cx+6,y_porton+48,14), p(cx-6,y_porton+48,14))}"/>'
            + '</g>')


def auto(cx, cy, color):
    return (f'<g class="auto auto--{color}">'
            + bloque("auto-cuerpo", cx-6, cy-10, 12, 20, 6)
            + bloque("auto-techo", cx-4.5, cy-5, 9, 10, 11, 6) + '</g>')


def arbol(x, y, r=10):
    a, b = p(x, y, 0)
    return (f'<ellipse class="iso-arbol-sombra" cx="{a+6}" cy="{b+3}" rx="{r+1}" ry="{r/2}"/>'
            f'<circle class="iso-arbol" cx="{a}" cy="{b-r+1}" r="{r}"/>'
            f'<circle class="iso-arbol-luz" cx="{a-r*0.35}" cy="{b-r*1.3+1}" r="{r*0.35}"/>')


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
    borde = lambda x: 205 + 0.055 * x          # línea de adelante del predio
    # Plataforma del predio (con espesor)
    sitio = [(0, 0), (1000, 0), (1000, 260), (0, 205)]
    out.append(f'<polygon class="iso-base-lado" points="{pts(p(0,205,0), p(1000,260,0), p(1000,260,-14), p(0,205,-14))}"/>')
    out.append(f'<polygon class="iso-base-lado2" points="{pts(p(0,0,0), p(0,205,0), p(0,205,-14), p(0,0,-14))}"/>')
    out.append(f'<polygon class="iso-base" points="{poligono_suelo(sitio)}"/>')
    # Cancha, calle interna, plaza y patio de maniobras
    out.append(f'<polygon class="iso-verde" points="{poligono_suelo([(0,0),(120,0),(120,borde(120)),(0,205)])}"/>')
    out.append(f'<polygon class="iso-cancha" points="{poligono_suelo([(18,28),(104,28),(104,185),(18,185)])}"/>')
    out.append(f'<polyline class="iso-cancha-linea" points="{poligono_suelo([(18,106),(104,106)])}"/>')
    out.append(f'<polygon class="iso-cancha-linea" points="{poligono_suelo([(18,28),(104,28),(104,185),(18,185)])}"/>')
    out.append(f'<polygon class="iso-cancha-linea" points="{poligono_suelo([(42,28),(80,28),(80,48),(42,48)])}"/>')
    out.append(f'<polygon class="iso-cancha-linea" points="{poligono_suelo([(42,165),(80,165),(80,185),(42,185)])}"/>')
    out.append(f'<polygon class="iso-calle" points="{poligono_suelo([(128,0),(150,0),(150,borde(150)),(128,borde(128))])}"/>')
    out.append(f'<polyline class="iso-calle-linea" points="{poligono_suelo([(139,4),(139,borde(139)-4)])}"/>')
    out.append(f'<polygon class="iso-patio" points="{poligono_suelo([(470,8),(1000,8),(1000,borde(1000)),(470,borde(470))])}"/>')
    out.append(f'<polygon class="iso-verde" points="{poligono_suelo([(870,232),(1000,232),(1000,borde(1000)),(870,borde(870))])}"/>')
    # Estacionamiento de autos frente a los locales libres
    out.append(f'<polygon class="iso-patio" points="{poligono_suelo([(165,124),(455,124),(455,156),(165,156)])}"/>')
    for i in range(14):
        x = 170 + i * 20.5
        out.append(f'<polyline class="iso-estac" points="{poligono_suelo([(x,128),(x,150)])}"/>')
    # Elementos con volumen: se dibujan de atrás hacia adelante
    objetos = []
    colores = ["blanco", "azul", "gris", "dorado", "blanco", "azul"]
    for i, slot in enumerate([0, 1, 3, 4, 6, 8, 9]):
        cx = 180 + slot * 20.5
        objetos.append((140 - cx, auto(cx, 140, colores[i % len(colores)])))
    for dep in DEPOSITOS:
        x, y, w, d = dep["x"], dep["y"], dep["ancho"], dep["fondo"]
        techo, frente, lado = caja(x, y, w, d, dep["alto"])
        extra = "" if dep["estado"] == "libre" else detalles_deposito(dep)
        svg = (f'<g class="lote lote--{dep["estado"]}" data-lote="{dep["n"]}" tabindex="0" aria-label="{dep["n"]}. {dep["nombre"]}">'
               f'<polygon class="cara-lado" points="{lado}"/><polygon class="cara-frente" points="{frente}"/>'
               f'<polygon class="cara-techo" points="{techo}"/>{extra}</g>')
        objetos.append(((y + d / 2) - (x + w / 2), svg))
        # Camiones en los primeros portones
        n = max(1, int(w // 26)); paso = w / n
        for i in range(dep.get("camiones", 0)):
            cx = x + paso * (i + 0.5)
            objetos.append(((y + d + 22) - cx, camion(cx, y + d)))
    # Árboles: fila sobre el frente, junto a la cancha y en la plaza
    for tx in range(172, 462, 40):
        objetos.append(((borde(tx) - 14) - tx, arbol(tx, borde(tx) - 14)))
    for ty in (30, 80, 130):
        objetos.append((ty - 115, arbol(115, ty, 8)))
    for tx in (895, 935, 975):
        objetos.append(((borde(tx) - 12) - tx, arbol(tx, borde(tx) - 12, 9)))
    for _, svg in sorted(objetos, key=lambda o: o[0]):
        out.append(svg)
    # Cerco en el frente del predio
    out.append(f'<polygon class="iso-cerco" points="{pts(p(0,205,0), p(1000,260,0), p(1000,260,6), p(0,205,6))}"/>')
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
