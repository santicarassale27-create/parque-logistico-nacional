"""
Genera el mapa 3D de ubicación (Montevideo en maqueta) para parque.html.

NO es parte de la web: es una herramienta para ajustar el mapa.
Cómo se usa:
  1. Editar PUNTOS (lugares, distancias, de qué lado va el cartel) o la vista (GIRO, INCLINACION).
  2. Correr:  python3 herramientas/generar-mapa.py
  3. Reemplaza el mapa dentro de parque.html (entre <!-- MAPA-3D:INICIO --> y <!-- MAPA-3D:FIN -->).

Las coordenadas son las del mapa plano de referencia (1000 x 600): x hacia el este, y hacia el sur.
"""

import math
import re
from pathlib import Path

# ---------------------------------------------------------------
# Datos (editar acá)
# ---------------------------------------------------------------
PARQUE = {"x": 548, "y": 212, "nombre": "Parque Logístico Nacional", "detalle": "Dr. Pantaleón Pérez 4881"}

# "arco": qué tan alto va el arco (proporción de la distancia). Bajarlo si el arco pisa un cartel.
PUNTOS = [
    {"x": 200, "y": 372, "nombre": "Puerto de Montevideo", "km": "12 km"},
    {"x": 900, "y": 150, "nombre": "Aeropuerto de Carrasco", "km": "10 km", "arco": 0.16},
    {"x": 770, "y": 62, "nombre": "Zona Franca Montevideo", "km": "11 km"},
]

BARRIOS = [("Ciudad Vieja", 215, 445), ("Pocitos", 430, 430), ("Prado", 210, 200),
           ("Carrasco", 860, 285), ("Unión", 470, 300)]

# Costa (de este a oeste). El resto del borde de la tierra es el borde del mapa.
COSTA = [(1000, 250), (930, 280), (860, 305), (800, 330), (740, 350), (680, 362), (620, 372), (565, 392),
         (515, 420), (470, 448), (430, 472), (398, 500), (372, 522), (352, 516), (334, 494), (305, 478),
         (262, 470), (215, 458), (170, 444), (138, 428), (132, 410), (160, 396), (198, 378), (222, 350),
         (228, 318), (214, 292), (186, 276), (146, 272), (104, 282), (70, 306), (44, 338), (22, 372), (0, 390)]
TIERRA = [(0, 0), (1000, 0)] + COSTA          # polígono de la tierra (cerrado)

AVENIDAS = [  # curvas Bézier cúbicas (aproximadas)
    [(300, 410), (420, 380), (560, 350), (900, 268)],
    [(300, 410), (380, 330), (470, 260), (545, 210)],
    [(545, 210), (640, 150), (720, 90), (820, 0)],
    [(228, 330), (300, 260), (330, 180), (340, 0)],
]

# Detalles del mapa
PARQUES = [  # áreas verdes (polígonos)
    [(178, 170), (232, 162), (252, 196), (226, 228), (186, 222)],          # Prado
    [(352, 360), (398, 352), (410, 384), (370, 396)],                      # Parque Batlle
    [(292, 452), (330, 448), (336, 466), (300, 470)],                      # Parque Rodó
]
HIPODROMO = (452, 112)        # Hipódromo de Maroñas (cerca del Parque)
PISTA = [(858, 180), (960, 128)]   # pista del aeropuerto (de punta a punta)
BARCOS = [(112, 322, 20), (168, 300, -15), (520, 540, 5), (820, 470, -20)]   # x, y, ángulo
MUELLES = [((178, 386), 145), ((196, 372), 140), ((212, 356), 135)]           # punto en la costa y dirección

# Vista
GIRO = math.radians(-14)      # rotación del mapa
INCLINACION = 0.56            # 1 = visto desde arriba; menos = más "acostado"
ESCALA = 1.0
ALTO_TIERRA = 12              # cuánto sobresale la tierra del agua
ESPESOR_MAQUETA = 26          # espesor del tablero

# ---------------------------------------------------------------
# Proyección
# ---------------------------------------------------------------


def P(x, y, z=0):
    dx, dy = x - 500, y - 300
    rx = dx * math.cos(GIRO) - dy * math.sin(GIRO)
    ry = dx * math.sin(GIRO) + dy * math.cos(GIRO)
    return (round(rx * ESCALA, 1), round(ry * ESCALA * INCLINACION - z, 1))


def pts(coords):
    return " ".join(f"{a},{b}" for a, b in coords)


def poli(coords, z):
    return pts([P(x, y, z) for x, y in coords])


def bezier(c, n=40):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = c
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, cc, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * x0 + b * x1 + cc * x2 + d * x3, a * y0 + b * y1 + cc * y2 + d * y3))
    return out


def adentro(x, y, poligono):
    dentro = False
    for i in range(len(poligono)):
        (x1, y1), (x2, y2) = poligono[i], poligono[(i + 1) % len(poligono)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            dentro = not dentro
    return dentro


def dist_costa(x, y):
    return min(math.hypot(x - a, y - b) for a, b in COSTA)


def paredes(coords, z0, z1, clase):
    """Paredes laterales de un polígono extruido (de atrás hacia adelante)."""
    caras = []
    for i in range(len(coords)):
        a, b = coords[i], coords[(i + 1) % len(coords)]
        q = [P(*a, z0), P(*b, z0), P(*b, z1), P(*a, z1)]
        caras.append((sum(p[1] for p in q) / 4, f'<polygon class="{clase}" points="{pts(q)}"/>'))
    return [c for _, c in sorted(caras)]


def caja(x, y, w, d, h, z0):
    x1, y1 = x + w, y + d
    esquinas = [(x, y), (x1, y), (x1, y1), (x, y1)]
    out = paredes(esquinas, z0, z0 + h, "m3-edif-lado")
    out.append(f'<polygon class="m3-edif-techo" points="{poli(esquinas, z0 + h)}"/>')
    return "".join(out)


def anillo(cx, cy, r, z):
    return pts([P(cx + r * math.cos(t / 60 * 2 * math.pi), cy + r * math.sin(t / 60 * 2 * math.pi), z) for t in range(61)])


def arco(a, b, za, zb, factor=0.32):
    """Arco en el aire entre dos puntos (Bézier cuadrática en 3D)."""
    (x0, y0), (x1, y1) = a, b
    alto = factor * math.hypot(x1 - x0, y1 - y0)
    mx, my, mz = (x0 + x1) / 2, (y0 + y1) / 2, (za + zb) / 2 + alto
    puntos = []
    for i in range(41):
        t = i / 40
        x = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * mx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * my + t * t * y1
        z = (1 - t) ** 2 * za + 2 * t * (1 - t) * mz + t * t * zb
        puntos.append(P(x, y, z))
    return "M" + " L".join(f"{px},{py}" for px, py in puntos)


def rotado(cx, cy, w, d, ang):
    """Rectángulo centrado en (cx, cy) de ancho w y largo d, girado ang grados."""
    a = math.radians(ang)
    esquinas = []
    for ex, ey in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)):
        esquinas.append((cx + ex * math.cos(a) - ey * math.sin(a), cy + ex * math.sin(a) + ey * math.cos(a)))
    return esquinas


def barco(cx, cy, ang):
    a = math.radians(ang)
    casco = []
    for ex, ey in ((0, -22), (6, -14), (6, 18), (-6, 18), (-6, -14)):
        casco.append((cx + ex * math.cos(a) - ey * math.sin(a), cy + ex * math.sin(a) + ey * math.cos(a)))
    estela = [(cx + ex * math.cos(a) - ey * math.sin(a), cy + ex * math.sin(a) + ey * math.cos(a)) for ex, ey in ((-5, 22), (0, 60), (5, 22))]
    out = [f'<polyline class="m3-estela" points="{poli(estela, 0)}"/>']
    out += paredes(casco, 0, 4, "m3-barco-lado")
    out.append(f'<polygon class="m3-barco" points="{poli(casco, 4)}"/>')
    puente = rotado(cx + 8 * math.sin(a), cy - 8 * math.cos(a), 8, 7, ang)
    out += paredes(puente, 4, 9, "m3-barco-puente-lado")
    out.append(f'<polygon class="m3-barco-puente" points="{poli(puente, 9)}"/>')
    return "".join(out)


def caja_clase(x, y, w, d, h, z0, clase):
    x1, y1 = x + w, y + d
    esquinas = [(x, y), (x1, y), (x1, y1), (x, y1)]
    out = paredes(esquinas, z0, z0 + h, clase + "-lado")
    out.append(f'<polygon class="{clase}-techo" points="{poli(esquinas, z0 + h)}"/>')
    return "".join(out)


# ---------------------------------------------------------------
# Dibujo
# ---------------------------------------------------------------


def generar():
    T = ALTO_TIERRA
    o = []
    borde = [(0, 0), (1000, 0), (1000, 560), (0, 560)]

    # Tablero (maqueta) con espesor y agua arriba
    o += paredes(borde, -ESPESOR_MAQUETA, 0, "m3-tablero-lado")
    o.append(f'<polygon class="m3-agua" points="{poli(borde, 0)}" fill="url(#m3-agua-grad)"/>')
    o.append(f'<clipPath id="m3-agua-clip"><polygon points="{poli(borde, 0)}"/></clipPath>')
    # Ondas suaves en el agua
    for r in (50, 95, 140):
        o.append(f'<polyline class="m3-ola" points="{anillo(640, 520, r, 0)}" clip-path="url(#m3-agua-clip)"/>')

    # Barcos (antes de la tierra: la costa los tapa si quedan detrás)
    for bx_, by_, ang in BARCOS:
        o.append(barco(bx_, by_, ang))
    # Muelles del puerto, sobre el agua
    muelles_svg = []
    for (mx, my), ang in MUELLES:
        a = math.radians(ang)
        cx, cy = mx + 20 * math.sin(a), my - 20 * math.cos(a)
        muelle = rotado(cx, cy, 9, 44, ang)
        muelles_svg += paredes(muelle, 0, 5, "m3-muelle-lado")
        muelles_svg.append(f'<polygon class="m3-muelle" points="{poli(muelle, 5)}"/>')
    o += muelles_svg

    # Tierra en relieve
    o += paredes(TIERRA, 0, T, "m3-tierra-lado")
    o.append(f'<polygon class="m3-tierra" points="{poli(TIERRA, T)}"/>')
    o.append(f'<clipPath id="m3-tierra-clip"><polygon points="{poli(TIERRA, T)}"/></clipPath>')

    # Trama de calles (sobre la tierra)
    lineas = []
    for k in range(-20, 60):
        c = k * 26
        lineas.append(f'M{pts([P(c, 0, T), P(c - 400, 600, T)]).replace(" ", " L")}')
        lineas.append(f'M{pts([P(0, c, T), P(1000, c - 300, T)]).replace(" ", " L")}')
    o.append(f'<path class="m3-trama" d="{" ".join(lineas)}" clip-path="url(#m3-tierra-clip)"/>')

    # Avenidas
    for av in AVENIDAS:
        o.append(f'<polyline class="m3-avenida" points="{pts([P(x, y, T) for x, y in bezier(av)])}" clip-path="url(#m3-tierra-clip)"/>')

    # Parques con árboles
    for parque in PARQUES:
        o.append(f'<polygon class="m3-parque" points="{poli(parque, T)}"/>')
        xs = [a for a, _ in parque]; ys = [b for _, b in parque]
        for i in range(14):
            tx = min(xs) + (max(xs) - min(xs)) * ((i * 0.618) % 1)
            ty = min(ys) + (max(ys) - min(ys)) * ((i * 0.382 + 0.2) % 1)
            if adentro(tx, ty, parque):
                ax_, ay_ = P(tx, ty, T + 3)
                o.append(f'<circle class="m3-arbol" cx="{ax_}" cy="{ay_}" r="3.2"/>')
    # Hipódromo de Maroñas: pista oval con césped adentro
    hx_, hy_ = HIPODROMO
    def ovalo(rx, ry, z):
        return pts([P(hx_ + rx * math.cos(t / 40 * 2 * math.pi), hy_ + ry * math.sin(t / 40 * 2 * math.pi), z) for t in range(41)])
    o.append(f'<polygon class="m3-hipodromo" points="{ovalo(34, 19, T)}"/>')
    o.append(f'<polygon class="m3-parque" points="{ovalo(26, 12, T + 0.2)}"/>')
    # Pista del aeropuerto
    (ax0, ay0), (ax1, ay1) = PISTA
    largo = math.hypot(ax1 - ax0, ay1 - ay0); ang = math.degrees(math.atan2(ay1 - ay0, ax1 - ax0)) - 90
    pista = rotado((ax0 + ax1) / 2, (ay0 + ay1) / 2, 9, largo, ang)
    o.append(f'<polygon class="m3-pista" points="{poli(pista, T + 0.3)}"/>')
    o.append(f'<polyline class="m3-pista-linea" points="{poli([(ax0, ay0), (ax1, ay1)], T + 0.4)}"/>')
    # Rambla: un camino que acompaña la costa
    rambla = [(x, y - 8) for x, y in COSTA if x >= 232]
    o.append(f'<polyline class="m3-rambla" points="{poli(rambla, T + 0.2)}"/>')

    # Costa iluminada
    o.append(f'<polyline class="m3-costa-brillo" points="{poli(COSTA, T)}"/>')
    o.append(f'<polyline class="m3-costa" points="{poli(COSTA, T)}"/>')

    # Anillos de distancia alrededor del Parque
    for r in (120, 240, 360):
        o.append(f'<polyline class="m3-anillo" points="{anillo(PARQUE["x"], PARQUE["y"], r, T)}" clip-path="url(#m3-tierra-clip)"/>')

    # Edificios (más densos en el Centro, torres sobre la costa de Pocitos). Pseudoaleatorio fijo.
    semilla = 7
    def azar():
        nonlocal semilla
        semilla = (semilla * 1103515245 + 12345) % 2 ** 31
        return semilla / 2 ** 31
    objetos = []
    reservados = [(PARQUE["x"], PARQUE["y"])] + [(p["x"], p["y"]) for p in PUNTOS]
    zonas_libres = PARQUES + [[(HIPODROMO[0] - 36, HIPODROMO[1] - 22), (HIPODROMO[0] + 36, HIPODROMO[1] - 22),
                               (HIPODROMO[0] + 36, HIPODROMO[1] + 22), (HIPODROMO[0] - 36, HIPODROMO[1] + 22)]]
    for _ in range(1500):
        x, y = azar() * 1000, azar() * 600
        if not adentro(x, y, TIERRA) or dist_costa(x, y) < 12:
            continue
        if any(math.hypot(x - a, y - b) < 36 for a, b in reservados) or any(adentro(x, y, z) for z in zonas_libres):
            continue
        centro = math.hypot(x - 300, y - 400)
        if azar() > max(0.08, 1 - centro / 400):
            continue
        costa_pocitos = 360 < x < 560 and dist_costa(x, y) < 30
        if costa_pocitos:
            h = 18 + azar() * 22
        else:
            h = 3 + azar() * (16 if centro < 170 else 7)
        tam = 7 + azar() * 4
        clase = "m3-edif" + (" m3-edif--luz" if azar() < 0.09 else "") + (" m3-edif--claro" if azar() < 0.3 else "")
        objetos.append((P(x, y)[1], f'<g class="{clase}">' + caja(x - tam / 2, y - tam / 2, tam, tam, h, T) + '</g>'))
    # Zona Franca: grupo de edificios propios
    zf = PUNTOS[2]
    for i in range(9):
        ang = i / 9 * 2 * math.pi + 0.3
        r = 40 + (i % 3) * 9
        x, y = zf["x"] + r * math.cos(ang), zf["y"] + 0.7 * r * math.sin(ang)
        if adentro(x, y, TIERRA):
            objetos.append((P(x, y)[1], '<g class="m3-edif m3-edif--zf">' + caja(x - 7, y - 5, 14, 10, 9 + (i % 4) * 4, T) + '</g>'))
    # Terminal del aeropuerto
    ap = PUNTOS[1]
    objetos.append((P(ap["x"] - 40, ap["y"] + 22)[1], '<g class="m3-edif m3-edif--zf">' + caja(ap["x"] - 58, ap["y"] + 16, 30, 12, 8, T) + '</g>'))
    # Contenedores y grúas en los muelles del puerto
    colores = ["dorado", "blanco", "azul", "dorado", "azul", "blanco"]
    for k, ((mx, my), ang) in enumerate(MUELLES):
        a = math.radians(ang)
        for j in range(3):
            d = 10 + j * 11
            cx, cy = mx + d * math.sin(a), my - d * math.cos(a)
            objetos.append((P(cx, cy)[1], caja_clase(cx - 3, cy - 3, 6, 6, 4 + (j % 2) * 3, 5, f"m3-cont-{colores[(k + j) % 6]}")))
        gx, gy = mx + 38 * math.sin(a), my - 38 * math.cos(a)
        bx0, by0 = P(gx, gy, 5); bx1, by1 = P(gx, gy, 32)
        bx2, by2 = P(gx + 14 * math.sin(a), gy - 14 * math.cos(a), 32)
        objetos.append((by0, f'<polyline class="m3-grua" points="{bx0},{by0} {bx1},{by1} {bx2},{by2}"/>'))
    for _, svg in sorted(objetos, key=lambda o_: o_[0]):
        o.append(svg)

    # Barrios
    for nombre, x, y in BARRIOS:
        bx, by = P(x, y, T)
        o.append(f'<text class="m3-barrio" x="{bx}" y="{by}">{nombre}</text>')
    ax, ay = P(640, 515, 0)
    o.append(f'<text class="m3-agua-txt" x="{ax}" y="{ay}">Río de la Plata</text>')

    # Halo y base del Parque
    o.append(f'<polygon class="m3-halo" points="{anillo(PARQUE["x"], PARQUE["y"], 70, T)}" fill="url(#m3-halo-grad)"/>')
    # Ondas que salen del Parque y recorren todo el mapa (recortadas al tablero)
    o.append('<g clip-path="url(#m3-agua-clip)">')
    for i in range(3):
        o.append(f'<polygon class="m3-onda m3-onda--{i + 1}" points="{anillo(PARQUE["x"], PARQUE["y"], 24, T)}" vector-effect="non-scaling-stroke"/>')
    o.append('</g>')

    # Pines de los puntos
    ALTO_PIN = 42
    for p in PUNTOS:
        bx, by = P(p["x"], p["y"], T)
        hx, hy = P(p["x"], p["y"], T + ALTO_PIN)
        o.append(f'<polygon class="m3-pin-base" points="{anillo(p["x"], p["y"], 10, T)}"/>')
        o.append(f'<line class="m3-pin-tallo" x1="{bx}" y1="{by}" x2="{hx}" y2="{hy}"/>')
        o.append(f'<circle class="m3-pin-cabeza" cx="{hx}" cy="{hy}" r="9"/><circle class="m3-pin-ojo" cx="{hx}" cy="{hy}" r="3.5"/>')

    # Columna dorada del Parque (prisma hexagonal)
    ALTO_COL = 70
    hexa = [(PARQUE["x"] + 13 * math.cos(math.radians(60 * i + 30)), PARQUE["y"] + 13 * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    o += paredes(hexa, T, T + ALTO_COL, "m3-columna-lado")
    o.append(f'<polygon class="m3-columna-techo" points="{poli(hexa, T + ALTO_COL)}"/>')

    # Arcos desde la punta de la columna hasta cada pin
    for p in PUNTOS:
        o.append(f'<path class="mapa-ruta" pathLength="1" d="{arco((PARQUE["x"], PARQUE["y"]), (p["x"], p["y"]), T + ALTO_COL, T + ALTO_PIN, p.get("arco", 0.32))}"/>')

    # Carteles: del lado contrario al Parque para no cruzar los arcos
    px_col, _ = P(PARQUE["x"], PARQUE["y"], T)
    for p in PUNTOS:
        hx, hy = P(p["x"], p["y"], T + ALTO_PIN)
        if hx < px_col:
            ancla, tx = "end", hx - 16
        else:
            ancla, tx = "start", hx + 16
        dy = p.get("dy", 0)
        o.append(f'<text class="pin-txt" x="{tx}" y="{hy - 4 + dy}" text-anchor="{ancla}">{p["nombre"]}</text>')
        o.append(f'<text class="pin-km" x="{tx}" y="{hy + 16 + dy}" text-anchor="{ancla}">{p["km"]}</text>')
    bx, by = P(PARQUE["x"], PARQUE["y"], T)
    o.append(f'<text class="pin-txt pin-txt--grande" x="{bx + 26}" y="{by + 30}">{PARQUE["nombre"]}</text>')
    o.append(f'<text class="pin-sub" x="{bx + 26}" y="{by + 50}">{PARQUE["detalle"]}</text>')

    # Tamaño del dibujo: todo lo proyectado + margen
    todos = [P(x, y, z) for x, y in borde for z in (-ESPESOR_MAQUETA, 0)] + [P(PARQUE["x"], PARQUE["y"], T + ALTO_COL + 160)]
    xs, ys = [a for a, _ in todos], [b for _, b in todos]
    x0, y0, x1, y1 = min(xs) - 20, min(ys) - 10, max(xs) + 20, max(ys) + 20
    cuerpo = "\n          ".join(o)
    return f'''<!-- MAPA-3D:INICIO (generado por herramientas/generar-mapa.py: no editar a mano) -->
      <svg class="pq-mapa-svg m3" viewBox="{round(x0)} {round(y0)} {round(x1 - x0)} {round(y1 - y0)}" role="img" aria-labelledby="mapa-titulo">
        <title id="mapa-titulo">Mapa 3D de Montevideo con el Parque Logístico Nacional y sus distancias al Puerto, al Aeropuerto de Carrasco y a Zona Franca</title>
        <defs>
          <linearGradient id="m3-agua-grad" x1="0" y1="0" x2="0" y2="1"><stop class="stop-agua-1" offset="0"/><stop class="stop-agua-2" offset="1"/></linearGradient>
          <radialGradient id="m3-halo-grad"><stop class="stop-halo-1" offset="0"/><stop class="stop-halo-2" offset="1"/></radialGradient>
        </defs>
        <g>
          {cuerpo}
        </g>
      </svg>
      <!-- MAPA-3D:FIN -->'''


if __name__ == "__main__":
    archivo = Path(__file__).resolve().parent.parent / "parque.html"
    html = archivo.read_text(encoding="utf-8")
    nuevo, n = re.subn(r"<!-- MAPA-3D:INICIO.*?<!-- MAPA-3D:FIN -->", generar(), html, flags=re.S)
    if n != 1:
        raise SystemExit("No encontré los comentarios MAPA-3D en parque.html")
    archivo.write_text(nuevo, encoding="utf-8")
    print("Mapa 3D actualizado en parque.html")
