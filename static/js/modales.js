/**
 * Modales nativos <dialog>: apertura con data-modal-open="<id>", cierre con
 * data-modal-close y click en backdrop. La tecla Escape la maneja el navegador.
 */
document.addEventListener("click", (event) => {
  const abrir = event.target.closest("[data-modal-open]");
  if (abrir) {
    const dialog = document.getElementById(abrir.dataset.modalOpen);
    if (dialog && typeof dialog.showModal === "function") dialog.showModal();
  }

  const cerrar = event.target.closest("[data-modal-close]");
  if (cerrar) {
    const dialog = cerrar.closest("dialog");
    if (dialog) dialog.close();
  }
});

document.addEventListener("click", (event) => {
  if (typeof HTMLDialogElement === "undefined") return;
  const dialog = event.target;
  if (!(dialog instanceof HTMLDialogElement) || !dialog.open || event.target !== dialog) return;

  const rect = dialog.getBoundingClientRect();
  const fuera =
    event.clientX < rect.left ||
    event.clientX > rect.right ||
    event.clientY < rect.top ||
    event.clientY > rect.bottom;

  if (fuera) dialog.close();
});
