# Gestion des ventes de blocs de glace 🧊

Application web professionnelle (Django + PostgreSQL + Bootstrap 5) pour gérer les
**utilisateurs**, le **référentiel** produit, les **demandeurs** et les **ventes** de blocs
de glace — contexte ONP (Office National des Pêches, Maroc).

## Fonctionnalités

- **Authentification sécurisée** (mots de passe hachés) avec **redirection selon le rôle**.
- **Rôles & permissions** : Admin, Agent, Caissier (accès conditionné par des mixins).
- **Gestion des utilisateurs** (CRUD, Admin uniquement).
- **Référentiel** : CRUD, upload de logo, règle « un seul référentiel actif ».
- **Demandeurs** : personnes physiques & morales (CRUD, activation/désactivation, recherche).
- **Ventes** : saisie avec calcul automatique, **code de vente** `BG_<réf>/<AA> <NNNNN>`,
  sélection du demandeur par modale, **ticket imprimable**.
- **Historique** : DataTables (recherche, tri, pagination), filtres, exports **Excel** & **PDF**, impression.
- **Tableau de bord** : cartes d'agrégats + ventes récentes + graphique Chart.js.
- Interface responsive (Bootstrap 5, FontAwesome, SweetAlert2).

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
| Dashboard                 |  ✅   |  ✅   |    ✅    |
| Gestion Utilisateurs      |  ✅   |  ❌   |    ❌    |
| Référentiel               |  ✅   |  ❌   |    ❌    |
| Demandeurs (CRUD)         |  ✅   |  🔍*  |    ❌    |
| Nouvelle Vente            |  ✅   |  ✅   |    ✅    |
| Historique des ventes     |  ✅   |  ✅   |    ✅    |

*🔍 L'agent peut rechercher des demandeurs (via la modale de vente) sans les gérer.*

## Architecture

```
config/            Paramètres du projet (settings basés sur .env, urls, wsgi)
apps/
  accounts/        Utilisateur custom + authentification + CRUD utilisateurs
  referentiel/     Référentiel produit (un seul actif)
  demandeurs/      Demandeurs physiques & moraux (héritage multi-table)
  ventes/          Ventes : code, calcul, ticket, historique, exports
  core/            Tableau de bord + contexte partagé + commande de seed
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
  séquence à 5 chiffres incrémentée par année (compteur verrouillé, sûr en concurrence).
- **Calcul de la vente** : l'utilisateur saisit le **Prix Total**, la **Quantité** est
  calculée automatiquement (`Prix Total / Prix Unitaire`).
- **Demandeurs** : héritage multi-table (base `Demandeur` + `DemandeurPhysique`/`DemandeurMorale`)
  pour une clé étrangère unique et propre depuis `Vente`.
