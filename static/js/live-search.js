/**
 * Live search genérico: debounce de ~300 ms, fetch, reemplazo del contenedor
 * y actualización de la URL con history.replaceState.
 * Se configura con data-live-search="<id del contenedor>" y, opcionalmente,
 * data-url="<endpoint>". Por defecto consulta la ruta actual.
 */
document.addEventListener("DOMContentLoaded", () => {
  const ESPERA = 300;

  document.querySelectorAll("[data-live-search]").forEach((input) => {
    const contenedorId = input.dataset.liveSearch;
    const urlBase = input.dataset.url || window.location.pathname;
    let temporizador;

    input.addEventListener("input", () => {
      window.clearTimeout(temporizador);
      temporizador = window.setTimeout(() => buscar(input, contenedorId, urlBase), ESPERA);
    });
  });

  async function buscar(input, contenedorId, urlBase) {
    const contenedor = document.getElementById(contenedorId);
    if (!contenedor) return;

    // Conserva filtros ya aplicados (por ejemplo, el estado activo/inactivo).
    const origen = new URL(urlBase, window.location.origin);
    const parametros =
      origen.pathname === window.location.pathname
        ? new URLSearchParams(window.location.search)
        : new URLSearchParams(origen.search);
    parametros.delete("page");
    parametros.set("q", input.value.trim());
    const url = `${origen.pathname}?${parametros.toString()}`;

    try {
      const respuesta = await fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status}`);
      contenedor.innerHTML = await respuesta.text();
      history.replaceState(null, "", url);
    } catch (error) {
      contenedor.innerHTML =
        '<p class="text-sm text-red-800">No se pudo cargar la búsqueda. Intentá de nuevo.</p>';
      console.error("Live search:", error);
    }
  }

  // Event delegation: los clicks sobre resultados sobreviven al re-render.
  document.addEventListener("click", (event) => {
    const resultado = event.target.closest("[data-resultado]");
    if (!resultado) return;
    document.dispatchEvent(
      new CustomEvent("live-search:seleccion", {
        detail: { id: resultado.dataset.resultado },
      })
    );
  });
});
