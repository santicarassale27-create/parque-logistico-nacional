/* ============================================
   Parque Logístico Nacional — JavaScript
   1. Menú del celular
   2. Año del pie de página
   3. Animaciones al hacer scroll
   4. Contadores animados
   5. Formulario de contacto
   ============================================ */

/* ---------- Configuración del formulario ----------
   El formulario envía los mensajes con Web3Forms (https://web3forms.com).
   Cada "access key" está asociada a UN mail: el mensaje llega a ese mail.
   Para que cada consulta llegue a la empresa correcta, se crea una key por
   cada mail en web3forms.com y se pega acá abajo.
   Mientras una key esté vacía, esa opción usa la key "general".
   Si "general" también está vacía, el formulario avisa que no está
   configurado y muestra los teléfonos (nunca finge que envió). */
var FORM_KEYS = {
  general: "",   // geligold@pln.com.uy
  geligold: "",  // geligold@pln.com.uy
  talfir: "",    // operativa@talfir.com.uy
  lamarel: "",   // lamarel@lamarel.com
  repremar: "",  // logistics@repremar.com
  rse: ""        // geligold@pln.com.uy
};

var FORM_SUBJECTS = {
  general: "Consulta general",
  geligold: "Consulta para Geligold — Depósito nacional",
  talfir: "Consulta para Talfir — Depósito aduanero",
  lamarel: "Consulta para Lamarel — Flete terrestre",
  repremar: "Consulta para Repremar — Fletes aéreos y marítimos",
  rse: "Consulta sobre Responsabilidad Social"
};

document.addEventListener("DOMContentLoaded", function () {
  initMenu();
  initYear();
  initScrollReveal();
  initCounters();
  initContactForm();
  initHistoria();
  initPlano();
});

/* ---------- 1. Menú del celular ---------- */
function initMenu() {
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (!toggle || !links) return;

  toggle.addEventListener("click", function () {
    var open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  links.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      links.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

/* ---------- 2. Año del pie de página ---------- */
function initYear() {
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();
}

/* ---------- 3. Animaciones al hacer scroll ----------
   No hace falta tocar el HTML: este código busca solo los elementos
   de la lista y los hace aparecer (suben y se hacen visibles) cuando
   entran en pantalla. Los elementos que están uno al lado del otro
   (tarjetas de una grilla) aparecen escalonados.
   Para animar algo más, agregá su selector a REVEAL_SELECTORS.
   Para que algo NO se anime, agregale la clase "no-reveal". */
var REVEAL_SELECTORS = [
  "section:not(.hero) .eyebrow",
  ".section-title",
  ".section-lead",
  ".grid > *",
  ".feature > *",
  ".timeline-item",
  ".mini-timeline > *",
  ".company-card",
  ".cta-band",
  ".quote",
  ".contact-grid > *",
  ".hist-anim"
].join(",");

function prefersReducedMotion() {
  return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function initScrollReveal() {
  // Sin soporte o con "reducir movimiento" activado, todo queda visible sin animar.
  if (!("IntersectionObserver" in window) || prefersReducedMotion()) return;

  var candidates = Array.prototype.slice.call(document.querySelectorAll(REVEAL_SELECTORS))
    .filter(function (el) {
      // Nada de la portada principal ni lo marcado con "no-reveal".
      return !el.closest(".hero") && !el.closest(".no-reveal");
    });

  // Si un elemento está adentro de otro que ya se anima, se anima solo el de afuera.
  var elements = candidates.filter(function (el) {
    return !candidates.some(function (other) { return other !== el && other.contains(el); });
  });

  elements.forEach(function (el) {
    el.classList.add("reveal");
    // Escalonado: cada hermano espera 0,1 s más que el anterior (máximo 0,4 s).
    var siblings = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
    if (el.parentElement && el.parentElement.matches(".grid, .feature, .contact-grid, .mini-timeline")) {
      el.style.transitionDelay = Math.min(siblings * 0.1, 0.4) + "s";
    }
  });

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target); // se anima una sola vez
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

  elements.forEach(function (el) { observer.observe(el); });
}

/* ---------- 4. Contadores animados ----------
   Los números de la franja de datos (.stats-strip) suben de 0 hasta su valor
   cuando aparecen en pantalla. Respeta el formato uruguayo (27.000) y
   el texto que sigue al número (m², km, ha, años). */
function initCounters() {
  var counters = document.querySelectorAll(".stats-strip strong, [data-counter]");
  if (!counters.length || !("IntersectionObserver" in window) || prefersReducedMotion()) return;

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      animateCounter(entry.target);
    });
  }, { threshold: 0.5 });

  counters.forEach(function (el) {
    var match = el.textContent.trim().match(/^(\d{1,3}(?:\.\d{3})*|\d+)(.*)$/);
    if (!match) return; // si no empieza con un número, se deja como está
    el.dataset.target = match[1].replace(/\./g, "");
    el.dataset.suffix = match[2];
    observer.observe(el);
  });
}

function animateCounter(el) {
  var target = parseInt(el.dataset.target, 10);
  var suffix = el.dataset.suffix || "";
  var duration = 1400;
  var start = null;

  function step(timestamp) {
    if (!start) start = timestamp;
    var progress = Math.min((timestamp - start) / duration, 1);
    var eased = 1 - Math.pow(1 - progress, 3); // arranca rápido y frena al final
    el.textContent = Math.round(target * eased).toLocaleString("es-UY") + suffix;
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ---------- 5. Formulario de contacto ---------- */
function initContactForm() {
  var form = document.getElementById("contact-form");
  if (!form) return;

  var status = document.getElementById("form-status");
  var button = form.querySelector("button[type=submit]");

  function showStatus(message, type) {
    status.textContent = message;
    status.className = "form-status form-status--" + type;
    status.hidden = false;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    var data = new FormData(form);

    // Trampa para robots: un campo invisible que las personas no completan.
    if (data.get("botcheck")) return;

    var destino = data.get("area") || "general";
    var key = FORM_KEYS[destino] || FORM_KEYS.general;

    if (!key) {
      showStatus("El formulario todavía no está habilitado. Mientras tanto, escribinos o llamanos a los datos de contacto de esta página.", "error");
      return;
    }

    data.append("access_key", key);
    data.append("subject", "Web PLN — " + (FORM_SUBJECTS[destino] || "Consulta"));
    data.append("from_name", "Web Parque Logístico Nacional");

    button.disabled = true;
    var originalText = button.textContent;
    button.textContent = "Enviando…";

    fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { Accept: "application/json" },
      body: data
    })
      .then(function (res) { return res.json(); })
      .then(function (json) {
        if (json.success) {
          showStatus("¡Gracias! Recibimos tu consulta y te vamos a responder a la brevedad.", "ok");
          form.reset();
        } else {
          throw new Error(json.message);
        }
      })
      .catch(function () {
        showStatus("No pudimos enviar tu mensaje. Probá de nuevo en unos minutos o comunicate por teléfono.", "error");
      })
      .finally(function () {
        button.disabled = false;
        button.textContent = originalText;
      });
  });
}

/* ---------- 6. Página Historia ----------
   a) La columna fija muestra el año de la etapa que se está leyendo.
   b) La línea vertical se llena de dorado a medida que se baja.
   c) Comparador de fotos "antes / después". */
function initHistoria() {
  var lista = document.querySelector(".hist-chapters-list");
  if (lista) {
    var capitulos = lista.querySelectorAll(".hist-chapter");
    var rail = document.querySelector(".hist-rail-inner");
    var railYear = document.getElementById("rail-year");
    var actual = null;

    function mostrarCapitulo(cap) {
      if (cap === actual || !rail || !railYear) return;
      actual = cap;
      rail.classList.add("cambiando");
      setTimeout(function () {
        railYear.textContent = cap.dataset.year;
        rail.classList.remove("cambiando");
      }, 200);
    }

    var ticking = false;
    function actualizar() {
      ticking = false;
      var mitad = window.innerHeight * 0.5;
      var caja = lista.getBoundingClientRect();
      var progreso = (mitad - caja.top) / caja.height;
      progreso = Math.max(0, Math.min(1, progreso));
      lista.style.setProperty("--progreso", progreso.toFixed(4));

      // La etapa actual es la última cuyo comienzo ya pasó la mitad de la pantalla.
      var activo = capitulos[0];
      capitulos.forEach(function (cap) {
        var arriba = cap.getBoundingClientRect().top;
        cap.classList.toggle("leido", arriba < mitad);
        if (arriba < mitad) activo = cap;
      });
      mostrarCapitulo(activo);
    }

    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(actualizar); }
    }, { passive: true });
    window.addEventListener("resize", actualizar);
    actualizar();
  }

  document.querySelectorAll(".antes-despues").forEach(function (fig) {
    var control = fig.querySelector(".antes-despues-control");
    if (!control) return;
    control.addEventListener("input", function () {
      fig.style.setProperty("--pos", control.value + "%");
    });
  });
}

/* ---------- 7. Plano de empresas (página El Parque) ----------
   Cada local del plano y cada fila de la lista tienen el mismo
   data-lote. Al pasar el mouse, tocar o enfocar uno, se resaltan los dos. */
function initPlano() {
  var plano = document.querySelector(".pq-plano-grid");
  if (!plano) return;
  var items = plano.querySelectorAll("[data-lote]");

  function resaltar(lote) {
    items.forEach(function (el) {
      el.classList.toggle("activo", el.dataset.lote === lote);
    });
  }

  items.forEach(function (el) {
    el.addEventListener("mouseenter", function () { resaltar(el.dataset.lote); });
    el.addEventListener("focus", function () { resaltar(el.dataset.lote); });
    el.addEventListener("click", function () { resaltar(el.dataset.lote); });
  });
  plano.addEventListener("mouseleave", function () { resaltar(null); });
}

/* En celular, el mapa y el plano se deslizan dentro de su recuadro:
   arrancan centrados en el punto indicado por data-centro (0 = izquierda, 1 = derecha). */
function centrarDeslizables() {
  document.querySelectorAll("[data-centro]").forEach(function (el) {
    var sobra = el.scrollWidth - el.clientWidth;
    if (sobra > 0) {
      el.scrollLeft = el.scrollWidth * parseFloat(el.dataset.centro) - el.clientWidth / 2;
    }
  });
}
window.addEventListener("load", centrarDeslizables);
