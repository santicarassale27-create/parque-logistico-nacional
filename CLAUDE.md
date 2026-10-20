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
| Santi | `index.html`, `historia.html`, `parque.html`, `empresas.html`, `proyecto.html`, `responsabilidad-social.html`, `img/` |
| Alfonso | `contacto.html`, `css/style.css`, `js/main.js`, `CLAUDE.md`, `README.md` |

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
