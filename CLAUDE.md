# Instrucciones para Claude — Web del Parque Logístico Nacional

Web institucional del Parque Logístico Nacional (PLN, Grupo Geligold), Montevideo, Uruguay.
Dos personas trabajan en paralelo, cada una con su propia sesión de Claude.
Estas reglas valen para las dos sesiones: seguilas siempre.

## Tecnología

- HTML, CSS y JavaScript puros. Sin frameworks, sin build, sin npm.
- Los autores saben lo básico de HTML/CSS/JS: escribí código simple y explicá lo que hacés.
- Para ver la web alcanza con abrir `index.html` en el navegador.

## Estructura

```
index.html                  Inicio (resumen de todo el contenido)
historia.html               Historia
parque.html                 El Parque (infraestructura)
empresas.html               Empresas del grupo
proyecto.html               Proyecto Itapeby
responsabilidad-social.html Responsabilidad Social
contacto.html               Contacto + formulario
css/style.css               Todos los estilos
js/main.js                  Todo el JavaScript
img/                        Fotos (cuando las haya)
```

## Quién es dueño de qué (para no pisarse)

| Persona | Archivos |
|---|---|
| Santi | `index.html`, `empresas.html`, `proyecto.html`, `responsabilidad-social.html`, `img/`, encabezado (nav) |
| Alfonso | `historia.html` y `parque.html` (rediseños), `contacto.html`, `css/style.css`, `js/main.js`, `CLAUDE.md`, `README.md` |

- No modifiques archivos del otro sin que la persona lo pida explícitamente.
- Si una tarea necesita tocar un archivo del otro (por ejemplo, un estilo nuevo en `style.css`),
  avisalo antes y proponé el cambio en vez de hacerlo directo.

## Forma de trabajar con git

1. Antes de empezar: traer lo último de `main` (`git pull origin main`).
2. Trabajar siempre en una rama nueva con nombre descriptivo (`textos-historia`, `fotos-portada`). Nunca directo en `main`.
3. Commits chicos, con mensaje en español que diga qué cambió.
4. Al terminar: subir la rama y abrir un Pull Request para que el otro lo revise.
5. Después del push, confirmar con `git ls-remote origin` que la rama llegó a
   `santicarassale27-create/parque-logistico-nacional`.

## Diseño

- Base: fondo blanco, textos oscuros y detalles en dorado. Barra superior, portada y pie usan los tonos oscuros.
- Usá SIEMPRE las variables de `:root` en `css/style.css` (`--gold-500`, `--gray-600`, etc.). Nunca colores sueltos.
- Componentes existentes que hay que reutilizar antes de crear nuevos: `.btn`, `.card`, `.grid-2/3/4`,
  `.feature`, `.section-title`, `.section-lead`, `.eyebrow`, `.stats-strip`, `.cta-band`, `.timeline`.
- Todo tiene que verse bien en celular (390px de ancho) sin que la página se mueva para los costados.

## Página Historia

- Estilos con prefijo `hist-` al final de `css/style.css`; títulos con la tipografía Sora (`--font-display`).
- Lugares de foto provisorios: `<div class="foto">` con una etiqueta `FOTO 01…08` que dice qué foto va. Al llegar la foto, se le pone `style="background-image:url(img/...)"` y se borra la etiqueta.
- Los textos con clase `pendiente` (subrayado punteado) esperan datos reales de la empresa: no inventarlos.
- Sin foto ni frase del fundador: la familia prefiere no aparecer en la web (decisión confirmada).

## Página El Parque

- Estilos con prefijo `pq-` en `css/style.css`; reutiliza de Historia `.foto`, `.hist-anim`, `.hist-cifras` y `.hist-next`.
- Sin textos chicos arriba de los títulos (decisión del equipo; solo se usan en la línea de tiempo de Historia).
- Sin íconos arriba de los títulos del mosaico de seguridad (decisión del equipo).
- **Plano 3D de Itapeby 3170:** lo genera `herramientas/generar-plano.py` (no editar el SVG a mano).
  Para cambiar depósitos, empresas o estados: editar la lista `DEPOSITOS` del script y correr
  `python3 herramientas/generar-plano.py`. Estados: `operando`, `confirmada`, `negociacion`, `libre`.
  Cada depósito tiene `camiones` (cuántos camiones dibujar en sus portones). Los portones, ventanas,
  claraboyas, autos, árboles y el cerco se dibujan solos. Sin leyenda debajo del plano (decisión del equipo).
  Regla de carteles (para que ninguna línea cruce un texto): cada cartel va a la derecha de su punto; los de abajo,
  cuanto más a la derecha más arriba; los de arriba, cuanto más a la derecha más abajo. Sin plaza en el plano.
  Estados confirmados: Fármaco Uruguayo y Gador operando; Droguería Uruguay confirmada; un laboratorio en negociación; 2 locales a definir.
  El plano está incompleto: falta el plano completo del predio que va a pasar la empresa.
- **Mapa de ubicación:** SVG dibujado a mano dentro de `parque.html` (no es Google Maps). Muestra solo el Parque y
  sus distancias al Puerto (12 km), Aeropuerto (10 km) y Zona Franca (11 km), con los km dentro de cada cartel.
  Sin otras sedes ni leyenda (decisión del equipo). Cada punto es un `<g class="pin">` con `transform="translate(x,y)"`;
  los textos van del lado contrario a las rutas para que no se crucen.
- Lo que opera cada empresa (aduanero, contenedores, fletes) se explica en Empresas, no en esta página.
  Acá queda solo una fila sobre el depósito del Parque.
- Fotos de la página: FOTO 01 vista aérea, 02 pasillos del depósito, 03 oficinas, 04 showroom.

## Comportamientos automáticos de `js/main.js` (no hace falta tocar el HTML)

- **Animaciones al hacer scroll:** se aplican solas a títulos, tarjetas, grillas, `.feature`, línea de tiempo, etc.
  Para excluir algo: agregale la clase `no-reveal`. Para sumar algo: agregá su selector a `REVEAL_SELECTORS`.
  Nada dentro de `.hero` se anima.
- **Contadores:** los `<strong>` dentro de `.stats-strip` que empiezan con un número (`27.000 m²`, `20`, `12 km`)
  cuentan desde 0. Para usarlo en otro lugar: atributo `data-counter`.
- **Formulario:** envía con Web3Forms. Las keys de cada empresa van en `FORM_KEYS`, arriba de `main.js`.
  Nunca muestres un mensaje de "enviado" si el envío no ocurrió.

## Contenido

- Español rioplatense (vos, contactanos, escribinos).
- No inventes datos (años, cifras, clientes, certificaciones). Si falta un dato, dejá un texto marcado como pendiente.
- Datos confirmados por el material de la empresa:
  - Predio de 10 ha en Montevideo; 27.000 m² cubiertos, hasta 11 m de altura; estanterías selectivas y drive-in; habilitación bromatológica; vigilancia 24 h.
  - A 12 km del Puerto, 10 km del Aeropuerto de Carrasco y 11 km de Zona Franca Montevideo.
  - Geligold S.A. — Depósito nacional — Dr. Pantaleón Pérez 4881 — 2525 87 82 — geligold@pln.com.uy
  - Talfir S.A. — Depósito aduanero (23.000 m², 7.000 cerrados; playa de contenedores; ISO tank) — Veracierto 2990 — 2504 61 82 — operativa@talfir.com.uy
  - Lamarel — Flete terrestre (20 camiones propios, cargas peligrosas) — Dr. Pantaleón Pérez 4881 — 2525 99 60 — lamarel@lamarel.com
  - Repremar Logistics — Fletes aéreos y marítimos (FCL/LCL) — Misiones 1372, 6.º piso — 2916 94 16 — logistics@repremar.com
- Pendiente de confirmar con la empresa: año de fundación (la web dice 1994, el material dice "35 años").

## Pie de página

- Es **idéntico en las 7 páginas** (marca + menú, dirección + logos de las empresas, copyright).
  Si se cambia, se cambia en todas: copiar el `<footer>` completo de una página a las demás.
- Los logos de las empresas están en `img/logos/` (sacados del PDF institucional).
