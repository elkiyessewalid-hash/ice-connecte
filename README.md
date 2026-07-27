# Gestion des ventes de blocs de glace 🧊

Application web professionnelle (Django + PostgreSQL + Bootstrap 5 + HTMX) pour gérer les
**utilisateurs**, le **référentiel** produit, les **demandeurs** et les **ventes** de blocs
de glace — contexte ONP (Office National des Pêches, Maroc).

## Fonctionnalités

- **Authentification sécurisée** : mots de passe hachés, **affichage/masquage** (œil),
  **verrouillage anti-force-brute** (django-axes) et **redirection selon le rôle**.
- **Rôles & permissions** : Admin, Agent (lecture seule), Caissier — accès conditionné par des mixins.
- **Gestion des utilisateurs** (CRUD, Admin) : recherche (login/nom/prénom), filtres profil & état,
  fiche détail en modale, longueurs de champs contrôlées.
- **Référentiel** : CRUD + upload de logo (validé) ; **un seul référentiel actif** garanti par
  une contrainte base de données.
- **Demandeurs** : personnes physiques & morales (CRUD, activation/désactivation) ; recherche
  (code, CIN, nom, prénom, raison sociale), filtres type/statut/état, **CIN unique** entre les deux
  tables (insensible à la casse), fiche détail en modale.
- **Ventes** : saisie avec **calcul bidirectionnel** (saisir le Prix Total *ou* la Quantité),
  **code de vente** `BG_<réf>/<AA> <NNNNN>`, sélection du demandeur en modale (clic simple),
  **ticket imprimable en deux exemplaires sur une page A4**.
- **Historique** : **pagination serveur HTMX (5/page)**, filtres (dates, demandeur, type, code,
  montant min/max) avec réinitialisation, fiche ticket en modale, exports **Excel** & **PDF**
  (Admin/Caissier), impression.
- **Tableau de bord** : cartes d'agrégats + ventes récentes + graphique Chart.js.
- Interface responsive (Bootstrap 5, HTMX, FontAwesome, SweetAlert2).

## Prérequis

- Python 3.12+
- PostgreSQL 13+ (optionnel en dev : repli SQLite automatique)

## Installation

```bash
# 1. Environnement virtuel
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux/Mac

# 2. Dépendances
pip install -r requirements.txt

# 3. Configuration
cp .env.example .env              # puis éditez .env (SECRET_KEY, DEBUG, DATABASE_URL)

# 4. Base de données
python manage.py migrate

# 5. Compte administrateur
python manage.py createsuperuser  # définissez ensuite son rôle=Admin dans /admin
# — ou données de démonstration complètes :
python manage.py seed_demo

# 6. Lancement
python manage.py runserver
```

Ouvrez http://127.0.0.1:8000/

## Configuration PostgreSQL

Dans `.env` :

```
DATABASE_URL=postgres://gestion_user:motdepasse@localhost:5432/gestion_glace
```

Sans `DATABASE_URL`, l'application utilise **SQLite** (`db.sqlite3`) automatiquement.

Création de la base (exemple) :

```sql
CREATE DATABASE gestion_glace;
CREATE USER gestion_user WITH PASSWORD 'motdepasse';
GRANT ALL PRIVILEGES ON DATABASE gestion_glace TO gestion_user;
```

## Comptes de démonstration (`seed_demo`)

| Login    | Mot de passe   | Rôle     |
|----------|----------------|----------|
| admin    | Admin2026!     | Admin    |
| agent    | Agent2026!     | Agent    |
| caissier | Caissier2026!  | Caissier |

> ⚠️ À usage de développement uniquement. Ne jamais exécuter `seed_demo` en production.

## Rôles & permissions

| Écran                     | Admin | Agent | Caissier |
|---------------------------|:-----:|:-----:|:--------:|
| Tableau de bord           |  ✅   |  ✅   |    ✅    |
| Gestion Utilisateurs      |  ✅   |  ❌   |    ❌    |
| Référentiel               |  ✅   |  ❌   |    ❌    |
| Demandeurs (CRUD)         |  ✅   |  ❌   |    ❌    |
| Nouvelle Vente            |  ✅   |  ❌   |    ✅    |
| Historique des ventes     |  ✅   |  ✅   |    ✅    |
| Exports Excel / PDF       |  ✅   |  ❌   |    ✅    |

> L'**Agent** est en **lecture seule** : il consulte le tableau de bord et l'historique,
> sans créer de vente ni exporter. Le **Caissier** crée et consulte les ventes (exports inclus).

## Sécurité

- **Anti-force-brute** : `django-axes` verrouille après 5 échecs (par IP + login), réinitialisation après succès.
- **Contrôle d'accès** par rôle sur toutes les vues (mixins) ; exports réservés à l'Admin et au Caissier.
- **XSS** : échappement systématique côté serveur (auto-escape) et côté client (rendus JavaScript).
- **Injection de formule Excel** neutralisée à l'export.
- **Upload de logo** validé (taille ≤ 2 Mo, extensions autorisées ; SVG refusé).
- **Intégrité** : `date_vente` non future, CIN unique inter-tables, un seul référentiel actif (contrainte DB).
- **Production** : échec au démarrage si `SECRET_KEY`/`ALLOWED_HOSTS` restent aux valeurs de dev ;
  cookies sécurisés, HSTS et redirection HTTPS quand `DEBUG=False`.

## Architecture

```
config/            Paramètres du projet (settings basés sur .env, urls, wsgi)
apps/
  accounts/        Utilisateur custom + authentification + CRUD utilisateurs
  referentiel/     Référentiel produit (un seul actif)
  demandeurs/      Demandeurs physiques & moraux (héritage multi-table)
  ventes/          Ventes : code, calcul, ticket, historique, exports
  core/            Tableau de bord + contexte partagé + mixins de liste (HTMX) + seed
templates/         Gabarits (base, partials, un dossier par module)
static/            CSS/JS applicatifs + logo
media/             Logos de référentiels uploadés
```

La logique métier (génération de code, calculs, référentiel actif, exports) est isolée
dans des modules `services.py` / `exports.py`. Les vues sont des **Class-Based Views**
protégées par des mixins de rôle.

## Tests

```bash
python manage.py test
```

## Mise en production

- Définir `DEBUG=False`, un `SECRET_KEY` fort et `ALLOWED_HOSTS` dans `.env`.
- Configurer `DATABASE_URL` vers PostgreSQL.
- `python manage.py collectstatic` (fichiers servis par WhiteNoise).
- Servir via `gunicorn config.wsgi` derrière un reverse-proxy HTTPS.
- Vérifier : `python manage.py check --deploy`.

## Décisions de conception notables

- **Code de vente** : `BG_<code_référentiel>/<AA> <NNNNN>` (ex. `BG_8234/26 00001`),
  séquence à 5 chiffres incrémentée **par année et par référentiel** (compteur verrouillé
  `select_for_update`, écriture atomique — sûr en concurrence).
- **Calcul de la vente** : l'utilisateur saisit **soit le Prix Total, soit la Quantité** ;
  l'autre valeur est calculée automatiquement à partir du **Prix Unitaire** du référentiel actif
  (source de vérité côté serveur).
- **Demandeurs** : héritage multi-table (base `Demandeur` + `DemandeurPhysique`/`DemandeurMorale`)
  pour une clé étrangère unique et propre depuis `Vente`.
