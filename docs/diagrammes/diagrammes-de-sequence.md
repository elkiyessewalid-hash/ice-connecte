# Diagrammes de séquence

Scénarios principaux de l'application.

## 1. Connexion (avec protection anti-force-brute)

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant N as Navigateur
    participant V as LoginView
    participant A as django-axes
    participant DB as Base de données

    U->>N: saisit login + mot de passe
    N->>V: POST /comptes/login/
    V->>A: authenticate(request, login, mdp)
    A->>DB: vérifie le verrou (IP + login)
    alt Compte verrouillé (≥ 5 échecs)
        A-->>V: accès refusé
        V-->>N: 403 (verrouillé ~1 h)
    else Identifiants valides
        A->>DB: contrôle du mot de passe (haché)
        DB-->>A: OK
        A-->>V: utilisateur authentifié
        V-->>N: 302 redirection selon le rôle
        Note over V,N: Admin → tableau de bord<br/>Caissier → nouvelle vente<br/>Agent → historique
    else Identifiants invalides
        A->>DB: enregistre la tentative échouée
        V-->>N: 200 + message « login ou mot de passe incorrect »
    end
```

## 2. Enregistrement d'une vente

```mermaid
sequenceDiagram
    actor C as Caissier / Admin
    participant V as NouvelleVenteView
    participant F as VenteForm
    participant R as Referentiel
    participant S as SequenceCounter
    participant VE as Vente
    participant DB as Base de données

    C->>V: choisit un demandeur + saisit Prix total OU Quantité
    V->>R: get_active()
    R-->>V: référentiel actif (prix_unitaire)
    V->>F: is_valid()
    F->>F: calcule l'autre valeur (prix_unitaire du référentiel)
    Note over F: date de vente non future ; montants bornés
    F-->>V: données validées

    rect rgb(235, 244, 255)
    Note over V,DB: transaction.atomic()
    V->>VE: save()
    VE->>S: get_or_create(annee, referentiel) + select_for_update
    S->>S: dernier_numero += 1
    S-->>VE: numéro annuel
    VE->>VE: code_vente = « BG_{code_ref}/{AA} {NNNNN} »
    VE->>DB: INSERT vente (prix_unitaire + référentiel figés)
    end

    V-->>C: ticket imprimable (2 exemplaires sur une page A4)
```

## 3. Consulter / filtrer l'historique (HTMX)

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant N as Navigateur
    participant H as HistoriqueVentesView
    participant DB as Base de données

    U->>N: modifie un filtre (dates, demandeur, type, montant…)
    N->>H: GET /ventes/historique/?filtres (en-tête HX-Request)
    H->>H: analyse + validation des filtres
    H->>DB: requête filtrée + pagination (5 / page)
    DB-->>H: page de ventes
    H-->>N: fragment HTML (tableau + pagination)
    N->>N: remplace #vente-results sans recharger la page
```
