"""Mixins et utilitaires partagés par les vues de liste (pagination HTMX, filtres)."""


class HtmxListMixin:
    """
    Pour les ListView filtrées : renvoie uniquement le fragment (tableau +
    pagination) quand la requête vient de HTMX, sinon la page complète.
    La vue doit définir ``partial_template_name`` et ``template_name``.
    """

    partial_template_name = None

    def get_template_names(self):
        if self.request.headers.get("HX-Request") and self.partial_template_name:
            return [self.partial_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Fenêtre de pagination (évite une barre interminable sur de gros volumes).
        paginator, page_obj = ctx.get("paginator"), ctx.get("page_obj")
        if paginator and page_obj and paginator.num_pages > 1:
            ctx["page_range"] = paginator.get_elided_page_range(
                page_obj.number, on_each_side=1, on_ends=1
            )
        return ctx


def filtre_etat(qs, request, champ="is_active"):
    """Applique le filtre État (?etat=actif|inactif) à un queryset."""
    etat = request.GET.get("etat", "").strip()
    if etat == "actif":
        return qs.filter(**{champ: True})
    if etat == "inactif":
        return qs.filter(**{champ: False})
    return qs
