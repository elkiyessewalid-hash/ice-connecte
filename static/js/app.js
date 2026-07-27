/* ============================================================
   JS commun : sidebar responsive, DataTables, confirmations
   ============================================================ */
(function () {
  "use strict";

  // Échappe le HTML pour éviter toute injection (XSS) dans les contenus dynamiques.
  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---- Sidebar repliable (mobile) ----
  const sidebar = document.getElementById("sidebar");
  const toggle = document.getElementById("sidebarToggle");
  const backdrop = document.getElementById("sidebarBackdrop");

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add("open");
    if (backdrop) backdrop.classList.add("show");
  }
  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove("open");
    if (backdrop) backdrop.classList.remove("show");
  }
  if (toggle) toggle.addEventListener("click", openSidebar);
  if (backdrop) backdrop.addEventListener("click", closeSidebar);

  // ---- Initialisation DataTables (tables .datatable) ----
  if (window.jQuery && jQuery.fn.dataTable) {
    jQuery(".datatable").each(function () {
      jQuery(this).DataTable({
        pageLength: 10,
        order: [],
        language: {
          url: "https://cdn.datatables.net/plug-ins/1.13.8/i18n/fr-FR.json",
        },
      });
    });
  }

  // ---- Confirmation de suppression via SweetAlert2 ----
  // Tout formulaire portant la classe .js-confirm-delete demande confirmation.
  document.querySelectorAll("form.js-confirm-delete").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (form.dataset.confirmed === "true") return; // déjà confirmé
      event.preventDefault();
      const nom = form.dataset.nom || "cet élément";
      Swal.fire({
        title: "Confirmer la suppression ?",
        html: "Vous êtes sur le point de supprimer <strong>" + escapeHtml(nom) + "</strong>.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#dc3545",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Oui, supprimer",
        cancelButtonText: "Annuler",
      }).then(function (result) {
        if (result.isConfirmed) {
          form.dataset.confirmed = "true";
          form.submit();
        }
      });
    });
  });
})();
