# Parque Logístico Nacional — Sitio web

Web institucional del **Parque Logístico Nacional** (Grupo Geligold), Montevideo, Uruguay:
historia, infraestructura, empresas del grupo (Geligold, Talfir, Lamarel y Repremar),
Proyecto Itapeby, responsabilidad social y contacto.

## Cómo verla

No necesita instalar nada: descargá el proyecto y abrí `index.html` en el navegador.

## Estructura

| Archivo | Contenido |
|---|---|
| `index.html` | Inicio: resumen de todo el sitio |
| `historia.html` | Historia de la empresa |
| `parque.html` | Infraestructura del Parque |
| `empresas.html` | Empresas que operan en el Parque |
| `proyecto.html` | Proyecto Itapeby 3170 |
| `responsabilidad-social.html` | Iniciativas con la comunidad |
| `contacto.html` | Datos de contacto y formulario |
| `css/style.css` | Estilos (colores en variables al principio del archivo) |
| `js/main.js` | Menú del celular, animaciones al hacer scroll, contadores y formulario |

## Equipo y reparto

- **Santi:** contenido y textos de las páginas, fotos.
- **Alfonso:** parte técnica (estilos, JavaScript, formulario y página de contacto).

## Cómo trabajamos

1. Antes de empezar, traer lo último de `main`.
2. Cada tarea en su propia rama.
3. Al terminar, abrir un Pull Request; el otro lo revisa y lo une a `main`.

Las reglas completas para trabajar con Claude están en [`CLAUDE.md`](CLAUDE.md).

## Formulario de contacto

Usa [Web3Forms](https://web3forms.com) (gratis, sin servidor). Para activarlo:

1. Entrar a web3forms.com, escribir el mail que va a recibir las consultas y crear la "Access Key".
   Repetir con cada mail (Geligold, Talfir, Lamarel, Repremar).
2. Pegar cada key en `FORM_KEYS`, al principio de `js/main.js`.

Mientras no haya keys, el formulario avisa que no está habilitado y muestra los teléfonos.

## Pendientes

- [ ] Fotos reales (y video con dron para la portada)
- [ ] Keys de Web3Forms para el formulario
- [ ] Confirmar año de fundación
- [ ] Mapa de Google Maps en Contacto
- [ ] Dominio y publicación (Netlify / Cloudflare Pages)
