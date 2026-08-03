# Diagramme de cas d'utilisation

Acteurs et fonctionnalités de l'application. L'**Admin** hérite des droits de l'Agent
(consultation) ; le **Caissier** peut en plus créer des ventes et exporter.

```mermaid
flowchart LR
    admin([👤 Admin]):::actor
    caissier([👤 Caissier]):::actor
    agent([👤 Agent]):::actor

    subgraph SYS["Système — Gestion des ventes de blocs de glace"]
        direction TB
        uc_login(Se connecter)
        uc_dash(Consulter le tableau de bord)
        uc_hist("Consulter l'historique des ventes")
        uc_ticket(Imprimer un ticket)
        uc_vente(Créer une vente)
        uc_export(Exporter Excel / PDF)
        uc_users(Gérer les utilisateurs)
        uc_ref(Gérer le référentiel)
        uc_dem(Gérer les demandeurs)
    end

    %% Agent : consultation seule
    agent --> uc_login
    agent --> uc_dash
    agent --> uc_hist
    agent --> uc_ticket

    %% Caissier : consultation + création + export
    caissier --> uc_login
    caissier --> uc_dash
    caissier --> uc_hist
    caissier --> uc_ticket
    caissier --> uc_vente
    caissier --> uc_export

    %% Admin : tout
    admin --> uc_login
    admin --> uc_dash
    admin --> uc_hist
    admin --> uc_ticket
    admin --> uc_vente
    admin --> uc_export
    admin --> uc_users
    admin --> uc_ref
    admin --> uc_dem

    %% Relations «include»
    uc_vente -. include .-> uc_ticket

    classDef actor fill:#e7f0ff,stroke:#2563eb,stroke-width:1px;
```

## Résumé des droits

| Cas d'utilisation | Admin | Caissier | Agent |
|-------------------|:-----:|:--------:|:-----:|
| Se connecter | ✅ | ✅ | ✅ |
| Tableau de bord | ✅ | ✅ | ✅ |
| Historique des ventes | ✅ | ✅ | ✅ |
| Imprimer un ticket | ✅ | ✅ | ✅ |
| Créer une vente | ✅ | ✅ | ❌ |
| Exporter Excel / PDF | ✅ | ✅ | ❌ |
| Gérer les utilisateurs | ✅ | ❌ | ❌ |
| Gérer le référentiel | ✅ | ❌ | ❌ |
| Gérer les demandeurs | ✅ | ❌ | ❌ |
