# 📋 Compte rendu de projet — Gestion des ventes de blocs de glace

**Type :** Application web de gestion commerciale
**Contexte :** ONP — Office National des Pêches (Maroc)
**Technologies :** Django 5.2 · PostgreSQL / SQLite · Bootstrap 5 · JavaScript
**Date :** Juillet 2026

---

## 1. Objectif du projet

Concevoir une application web **professionnelle et sécurisée** permettant de gérer
l'ensemble du cycle de vente de blocs de glace :

- la gestion des **utilisateurs** et de leurs droits ;
- le **référentiel** produit (prix unitaire de référence) ;
- les **demandeurs** (acheteurs / vendeurs, personnes physiques et morales) ;
- l'enregistrement et le suivi des **ventes**, avec impression de tickets ;
- un **tableau de bord** de pilotage.

---

## 2. Périmètre fonctionnel livré

### 2.1 Authentification & rôles
- Connexion sécurisée (mots de passe **hachés** par Django).
- **Trois rôles** avec redirection automatique après connexion :
  - **Admin** : accès complet (utilisateurs, référentiel, demandeurs, ventes, dashboard) ;
  - **Agent** : enregistrement des ventes, recherche de demandeurs, historique ;
  - **Caissier** : enregistrement des ventes, consultation, impression de tickets.
- Protection de **toutes les routes** + contrôle d'accès par rôle (mixins).

### 2.2 Gestion des utilisateurs (Admin)
- CRUD complet : Login, Mot de passe, Nom, Prénom, Rôle.
- Impossibilité pour un administrateur de supprimer son propre compte.

### 2.3 Référentiel
- CRUD complet avec **logo** (upload d'image).
- Règle métier stricte : **un seul référentiel actif** à la fois.
- Le prix unitaire du référentiel actif alimente automatiquement les ventes.

### 2.4 Demandeurs
- Deux catégories : **personne physique** (CIN, Nom, Prénom) et **personne morale**
  (Raison sociale + représentant).
- Statut **Acheteur / Vendeur**, activation / désactivation.
- **Recherche** instantanée (par code ou nom) utilisée dans la saisie de vente.

### 2.5 Ventes
- Écran « Nouvelle vente » avec :
  - **Code vente** généré automatiquement : `BG_<code réf>/<AA> <NNNNN>`
    (ex. `BG_8234/26 00001`), séquence à 5 chiffres incrémentée par année ;
  - sélection du demandeur par **fenêtre modale** avec recherche (double-clic) ;
  - **prix unitaire** chargé automatiquement (lecture seule) ;
  - saisie du **prix total**, la **quantité (Kg)** est calculée automatiquement
    (`Quantité = Prix Total ÷ Prix Unitaire`) ;
  - date de vente pré-remplie au jour courant.
- À l'enregistrement : **pop-up d'un ticket imprimable** (logo référentiel, logo ONP,
  code, demandeur, prix, quantité, date).

### 2.6 Historique & exports
- Tableau interactif (**DataTables** : recherche, tri, pagination).
- Filtres : date, demandeur, type, code vente.
- **Exports Excel et PDF**, impression.

### 2.7 Tableau de bord
- Cartes de synthèse : total ventes, quantité totale, chiffre d'affaires, nombre de demandeurs.
- Liste des ventes récentes.
- **Graphique** du chiffre d'affaires (Chart.js).

---

## 3. Architecture technique

```
config/          Paramètres du projet (configuration via .env, urls, wsgi)
apps/
  accounts/      Utilisateur personnalisé + authentification + CRUD utilisateurs
  referentiel/   Référentiel produit (règle « un seul actif »)
  demandeurs/    Demandeurs physiques & moraux (héritage multi-table)
  ventes/        Ventes : génération de code, calculs, ticket, historique, exports
  core/          Tableau de bord + contexte partagé + commande de peuplement
templates/       Gabarits (base commune + un dossier par module)
static/          CSS / JavaScript applicatifs + logo
media/           Logos de référentiels téléversés
```

**Principes appliqués (bonnes pratiques Django) :**
- Vues en **Class-Based Views** protégées par des **mixins** de rôle.
- Logique métier isolée dans des services (`services.py`, `exports.py`), hors des vues.
- **Modèle utilisateur personnalisé** (`AUTH_USER_MODEL`).
- Séparation nette : modèles / vues / URLs / formulaires / templates / services.
- Configuration **par variables d'environnement** (aucun secret en dur).
- Code entièrement commenté, en français.

**Modèles principaux :** `User`, `Referentiel`, `Demandeur` (→ `DemandeurPhysique`,
`DemandeurMorale`), `Vente`, `SequenceCounter`.

---

## 4. Sécurité

- Mots de passe hachés ; **protection CSRF** sur tous les formulaires.
- Toutes les routes protégées par authentification + **permissions par rôle**.
- Secrets (`SECRET_KEY`, base de données) via `.env` — **jamais versionnés**.
- En production (`DEBUG=False`) : redirection HTTPS, cookies sécurisés, HSTS,
  protection anti-sniffing et anti-clickjacking activés automatiquement.
- Journalisation configurée.

---

## 5. Choix de conception notables

| Sujet | Décision |
|-------|----------|
| Code de vente | `BG_<code réf>/<AA> <NNNNN>`, séquence par année (compteur verrouillé, sûr en concurrence). |
| Calcul de vente | Saisie du **Prix Total** → **Quantité** calculée automatiquement. |
| Demandeurs | Héritage multi-table : clé étrangère unique et propre depuis `Vente`. |
| Base de données | PostgreSQL par défaut, **repli SQLite automatique** pour un démarrage immédiat. |
| Ticket | Pop-up HTML imprimable (fidélité maximale, sans dépendance native fragile). |

---

## 6. Tests & validation

- **21 tests automatisés** (authentification, permissions, génération de code, calculs,
  règle « un seul actif », recherche, exports) — **tous au vert**.
- **Test de bout en bout** sur serveur en fonctionnement : **43 vérifications** couvrant
  chaque rôle, chaque écran et chaque règle métier — **0 anomalie**.
- Audit de déploiement `python manage.py check --deploy` : **aucun problème** en configuration
  de production.

**Exemples validés :** vente `900 DH ÷ 4,50 DH/Kg = 200 Kg`, code `BG_8234/26 00001`
puis `00002` sans doublon, suppression d'un demandeur rattaché à une vente **bloquée**.

---

## 7. Livrables

- Code source complet et exécutable (aucun code fictif / TODO).
- `requirements.txt`, `.env.example`.
- `README.md` (présentation + installation rapide).
- `GUIDE_INSTALLATION.md` (installation détaillée sur un nouvel ordinateur).
- Commande `seed_demo` (jeu de données de démonstration).
- Suite de tests automatisés.

---

## 8. Pistes d'évolution

- Reçu PDF du ticket côté serveur (en plus de l'impression navigateur).
- Statistiques avancées (par ville, par demandeur, par période).
- Gestion de stock et seuils d'alerte.
- Authentification à deux facteurs et journal d'audit des actions.
- API REST pour une éventuelle application mobile.

---

*Projet réalisé en respectant une architecture propre, modulaire et prête pour la production.*
