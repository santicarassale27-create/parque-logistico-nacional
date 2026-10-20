# Notas del proyecto — Parque Logístico Nacional

Estado del trabajo al 20/10/2026. Pensado para que cualquiera de los dos (o alguien nuevo)
pueda retomar el proyecto sin tener que releer todo el historial de commits.

## Objetivo

Sitio web institucional e **informativo** (no es un e-commerce ni vende productos) para el
**Parque Logístico Nacional** (PLN), liderado por **Geligold S.A.**, en Montevideo. Es un
proyecto serio pensado para presentarle a una empresa importante, así que se construyó de
forma incremental: cada cambio de diseño se revisa antes de sumar el siguiente.

El sitio cuenta: la historia del Parque, su infraestructura, las cuatro empresas que operan
dentro de él, el Proyecto Itapeby (declarado de Interés Municipal) y las iniciativas de
responsabilidad social con el Municipio F y el barrio.

## Qué hicimos hasta ahora

- **Sitio completo en HTML/CSS/JS puro**, sin frameworks ni build: 7 páginas (Inicio,
  Historia, El Parque, Empresas, Proyecto Itapeby, Responsabilidad Social, Contacto).
- **Contenido** extraído de los PDFs/docx institucionales que mandó la empresa (historia
  1994–2026, ficha técnica del Parque, datos de las 4 empresas, Proyecto Itapeby, concurso de
  dibujo, Escuela de Conducción de Autoelevadores, donaciones).
- **Identidad visual** definida a partir de mirar la competencia (Costa Oriental y Grupo RAS):
  fondo blanco, textos oscuros, acentos en **dorado** (no rojo, para no parecerse a Costa
  Oriental). Nav blanco en todo el sitio. Tipografías Sora (títulos) y Work Sans (texto).
- **Inicio:** hero a pantalla completa con foto (placeholder genérico por ahora) y, a medida
  que se baja, un resumen de cada sección del sitio (historia, infraestructura, empresas,
  proyecto, RSE) — estilo "scroll reveal" como Costa Oriental.
- **Historia:** línea de tiempo **horizontal** con scroll lateral (año arriba, punto en la
  línea, tarjeta con texto y cuadrante para foto), según referencia visual que pasó Fabiana.
- **Formulario de contacto real** (Web3Forms, sin backend) con animaciones de aparición al
  scrollear y contadores animados en las franjas de números — trabajo de Alfonso.
- **Repo en GitHub** (`santicarassale27-create/parque-logistico-nacional`), con flujo de
  ramas + Pull Request entre Santi y Alfonso. Reglas completas en [`CLAUDE.md`](CLAUDE.md).

## Archivos importantes

| Archivo | Contenido | A cargo de |
|---|---|---|
| `index.html` | Inicio (resumen de todo) | Santi |
| `historia.html` | Historia / línea de tiempo | Santi |
| `parque.html` | Infraestructura del Parque | Santi |
| `empresas.html` | Geligold, Talfir, Lamarel, Repremar | Santi |
| `proyecto.html` | Proyecto Itapeby 3170 | Santi |
| `responsabilidad-social.html` | RSE | Santi |
| `contacto.html` | Formulario de contacto | Alfonso |
| `css/style.css` | Todos los estilos (variables de color en `:root`) | Alfonso |
| `js/main.js` | Menú, animaciones, contadores, formulario | Alfonso |
| `img/` | Fotos (hoy solo hay un placeholder genérico) | Santi |
| `CLAUDE.md` | Reglas de trabajo para las sesiones de Claude | Alfonso |
| `README.md` | Resumen del proyecto para cualquiera que lo abra | Alfonso |

## Decisiones que tomamos

- **Paleta:** blanco + navy + dorado. Se probaron varias opciones de color de acento (rojo,
  dorado, azul petróleo, verde esmeralda, terracota) y se eligió dorado por ser distinto al
  rojo de Costa Oriental y coherente con el nombre "Geligold".
- **Nav blanco** en vez de navy oscuro, para que combine con el hero de foto completa (se
  corrigió después de un primer intento con nav oscuro).
- **Sin backend:** el formulario usa Web3Forms (gratis) en vez de un servidor propio.
- **Reparto de archivos** entre Santi y Alfonso para poder trabajar en paralelo sin pisarse
  (tabla completa en `CLAUDE.md`).
- **Fotos:** mientras no haya material real, se usan placeholders genéricos bien marcados
  ("Foto genérica — a reemplazar por foto real del Parque"), nunca contenido inventado como
  si fuera definitivo.
- **Año de fundación sin confirmar:** la web dice 1994 (dato del PDF institucional), pero
  otro material de la empresa dice "35 años de trayectoria" — son años distintos, hay que
  preguntarle a la empresa cuál es el correcto antes de publicar.

## Qué falta hacer

- [ ] Fotos y video reales del Parque (reemplazar todos los placeholders, especialmente el
      hero de Inicio y el cuadrante de cada hito de la línea de tiempo).
- [ ] Confirmar con la empresa el año de fundación (1994 vs. "35 años").
- [ ] Crear las Access Keys de Web3Forms para cada empresa y cargarlas en `FORM_KEYS`
      (`js/main.js`) — hoy el formulario avisa que no está habilitado.
- [ ] Mapa de Google Maps en la página de Contacto.
- [ ] Revisar textos finales con la empresa antes de publicar (nada de lo escrito es
      definitivo hasta que ellos lo confirmen).
- [ ] Definir dominio y publicación final (se está probando en Netlify).
