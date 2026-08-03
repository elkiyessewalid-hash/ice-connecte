# Diagramme de Gantt — Planning du stage

Période : **06/07/2026 → 06/08/2026** (≈ 5 semaines).

```mermaid
gantt
    title Planning du stage — Gestion des ventes de blocs de glace
    dateFormat DD/MM/YYYY
    axisFormat %d/%m

    section Découverte & analyse
    Installation & prise en main        :a1, 06/07/2026, 2d
    Étude de l'existant & des besoins   :a2, after a1, 3d

    section Correctifs & UX
    Correctifs intégrité & permissions  :b1, 13/07/2026, 3d
    UX des listes (HTMX, filtres)       :b2, after b1, 3d

    section Audit & remédiation
    Audit complet du projet             :c1, 20/07/2026, 2d
    Remédiation sécurité                :c2, after c1, 3d
    Remédiation robustesse & intégrité  :c3, after c2, 2d

    section Fonctionnalités
    Tableau de bord (KPIs, graphique)   :d1, 27/07/2026, 2d
    Historique demandeur & sélecteurs   :d2, after d1, 2d
    Jeu de données de démonstration     :d3, after d2, 1d

    section Documentation & finalisation
    Documentation (guide, README)       :e1, 03/08/2026, 1d
    Diagrammes UML & Gantt              :e2, after e1, 1d
    Tests, revue & soutenance           :e3, after e2, 2d
```

## Détail des phases

| Phase | Période | Livrables |
|-------|---------|-----------|
| Découverte & analyse | 06/07 → 10/07 | Environnement fonctionnel, cadrage des besoins |
| Correctifs & UX | 13/07 → 19/07 | Rôles/permissions, listes HTMX (pagination, filtres, recherche) |
| Audit & remédiation | 20/07 → 26/07 | Audit multi-axes + corrections (sécurité, robustesse, intégrité) |
| Fonctionnalités | 27/07 → 01/08 | Tableau de bord, historique par demandeur, sélecteurs de date, seed |
| Documentation & finalisation | 03/08 → 06/08 | Guide d'installation, README, diagrammes UML + Gantt, tests |
