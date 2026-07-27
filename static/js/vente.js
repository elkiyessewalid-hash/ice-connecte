/* ============================================================
   Saisie de vente : calcul live, sélection du demandeur, ticket
   ============================================================ */
(function () {
  "use strict";

  // Échappe le HTML pour éviter toute injection (XSS) lors des rendus innerHTML.
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  const form = document.getElementById("venteForm");
  if (!form) return;

  // Tolère un séparateur décimal virgule (locale FR) en plus du point.
  const prixUnitaire = parseFloat((form.dataset.prixUnitaire || "0").replace(",", "."));
  const searchUrl = form.dataset.searchUrl;

  const prixTotalInput = document.getElementById("id_prix_total");
  const quantiteInput = document.getElementById("id_quantite");
  const saisieInput = document.getElementById("id_saisie");
  const demandeurHidden = document.getElementById("id_demandeur");
  const demandeurDisplay = document.getElementById("demandeurDisplay");

  // ---- Calcul live bidirectionnel ----
  // Qté (Kg) = Prix total / Prix unitaire  ·  Prix total (DH) = Qté × Prix unitaire.
  // Affecter .value par programme ne déclenche pas l'évènement "input" : pas de boucle.
  function depuisPrixTotal() {
    if (saisieInput) saisieInput.value = "total";
    const total = parseFloat(prixTotalInput.value);
    if (!prixUnitaire || isNaN(total) || total <= 0) {
      quantiteInput.value = "";
      return;
    }
    quantiteInput.value = (total / prixUnitaire).toFixed(3);
  }
  function depuisQuantite() {
    if (saisieInput) saisieInput.value = "quantite";
    const qte = parseFloat(quantiteInput.value);
    if (!prixUnitaire || isNaN(qte) || qte <= 0) {
      prixTotalInput.value = "";
      return;
    }
    prixTotalInput.value = (qte * prixUnitaire).toFixed(2);
  }
  if (prixTotalInput && quantiteInput) {
    prixTotalInput.addEventListener("input", depuisPrixTotal);
    quantiteInput.addEventListener("input", depuisQuantite);
    if (prixTotalInput.value) depuisPrixTotal(); // champ éventuellement pré-rempli
  }

  // ---- Recherche de demandeurs (modale) ----
  const searchInput = document.getElementById("demandeurSearch");
  const resultsBox = document.getElementById("demandeurResults");
  let debounce = null;

  function chargerDemandeurs(q) {
    fetch(searchUrl + "?q=" + encodeURIComponent(q), {
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then((r) => r.json())
      .then((data) => afficherResultats(data.results || []))
      .catch(() => {
        resultsBox.innerHTML =
          '<div class="text-danger small p-2">Erreur de chargement.</div>';
      });
  }

  function afficherResultats(items) {
    resultsBox.innerHTML = "";
    if (!items.length) {
      resultsBox.innerHTML =
        '<div class="text-muted small p-2">Aucun demandeur actif trouvé.</div>';
      return;
    }
    items.forEach((d) => {
      const el = document.createElement("button");
      el.type = "button";
      el.className = "list-group-item list-group-item-action";
      el.innerHTML =
        '<div class="d-flex justify-content-between">' +
        '<span><strong>' + esc(d.code) + "</strong> — " + esc(d.libelle) + "</span>" +
        '<span class="badge bg-light text-dark">' + esc(d.categorie) + " · " + esc(d.statut) + "</span>" +
        "</div>";
      // Clic simple = sélection (plus rapide qu'un double-clic).
      el.addEventListener("click", function () {
        selectionnerDemandeur(d);
      });
      resultsBox.appendChild(el);
    });
  }

  function selectionnerDemandeur(d) {
    if (demandeurHidden) demandeurHidden.value = d.id;
    if (demandeurDisplay) demandeurDisplay.value = d.code + " — " + d.libelle;
    const modalEl = document.getElementById("demandeurModal");
    const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
    modal.hide();
  }

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      clearTimeout(debounce);
      const q = searchInput.value.trim();
      debounce = setTimeout(() => chargerDemandeurs(q), 250);
    });
    // Charge la liste complète des demandeurs actifs à l'ouverture de la modale.
    const modalEl = document.getElementById("demandeurModal");
    if (modalEl) {
      modalEl.addEventListener("shown.bs.modal", function () {
        searchInput.focus();
        if (!resultsBox.children.length) chargerDemandeurs("");
      });
    }
  }

  // ---- Ouverture automatique du ticket après enregistrement ----
  const ticketModalEl = document.getElementById("ticketModal");
  if (ticketModalEl && ticketModalEl.dataset.autoshow === "true") {
    new bootstrap.Modal(ticketModalEl).show();
  }
})();
