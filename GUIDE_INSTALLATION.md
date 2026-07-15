# 🧊 Guide d'installation — Gestion des ventes de blocs de glace

Ce guide explique comment installer et lancer l'application **sur un nouvel ordinateur**,
étape par étape, à partir de zéro.

---

## 1. Prérequis à installer

| Logiciel | Version | Lien |
|----------|---------|------|
| **Python** | 3.12 ou plus | https://www.python.org/downloads/ |
| **Git** | dernière | https://git-scm.com/downloads |
| **PostgreSQL** *(optionnel)* | 13+ | https://www.postgresql.org/download/ |

> ℹ️ **PostgreSQL est optionnel** : sans configuration de base de données, l'application
> utilise automatiquement **SQLite** (un simple fichier `db.sqlite3`), ce qui suffit pour
> tester ou faire une démonstration.

⚠️ Sous Windows, lors de l'installation de Python, **cochez « Add Python to PATH »**.

Vérifiez l'installation dans un terminal :

```bash
python --version      # doit afficher Python 3.12.x
git --version
```

---

## 2. Récupérer le projet

```bash
# Cloner la branche zakaria du dépôt
git clone -b zakaria https://github.com/elkiyessewalid-hash/ice-connecte.git
cd ice-connecte
```

> Si le projet est dans un sous-dossier `gestion-glace/`, faites `cd gestion-glace` avant la suite.

---

## 3. Créer l'environnement virtuel Python

**Windows (PowerShell) :**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS :**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Le terminal doit maintenant afficher `(.venv)` au début de la ligne.

---

## 4. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Configurer l'application (`.env`)

Copiez le modèle fourni :

```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```

Ouvrez `.env` et adaptez au minimum :

```ini
SECRET_KEY=collez-ici-une-cle-secrete
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Générer une clé secrète solide :

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> Laissez `DATABASE_URL` commentée pour utiliser SQLite (recommandé pour un premier test).

---

## 6. Préparer la base de données

```bash
python manage.py migrate
```

Puis, au choix :

**Option A — jeu de données de démonstration prêt à l'emploi (recommandé pour tester) :**
```bash
python manage.py seed_demo
```
Cela crée un référentiel actif, deux demandeurs et **trois comptes** :

| Login | Mot de passe | Rôle |
|-------|-------------|------|
| `admin` | `Admin2026!` | Admin |
| `agent` | `Agent2026!` | Agent |
| `caissier` | `Caissier2026!` | Caissier |

**Option B — créer uniquement un administrateur :**
```bash
python manage.py createsuperuser
```
(pensez ensuite à définir son rôle sur **Admin** dans `/admin`).

---

## 7. Lancer l'application

```bash
python manage.py runserver
```

Ouvrez votre navigateur sur **http://127.0.0.1:8000/** et connectez-vous.

Pour arrêter le serveur : `Ctrl + C`.

---

## 8. (Optionnel) Utiliser PostgreSQL

1. Créez la base et l'utilisateur :
   ```sql
   CREATE DATABASE gestion_glace;
   CREATE USER gestion_user WITH PASSWORD 'motdepasse';
   GRANT ALL PRIVILEGES ON DATABASE gestion_glace TO gestion_user;
   ```
2. Dans `.env`, décommentez et adaptez :
   ```ini
   DATABASE_URL=postgres://gestion_user:motdepasse@localhost:5432/gestion_glace
   ```
3. Relancez `python manage.py migrate` puis `seed_demo`.

---

## 9. Résolution des problèmes courants

| Problème | Solution |
|----------|----------|
| `python n'est pas reconnu` | Python n'est pas dans le PATH → réinstallez en cochant « Add to PATH ». |
| `.\.venv\Scripts\Activate.ps1 ... interdit` | PowerShell : lancez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` puis réessayez. |
| Redirection HTTPS / page inaccessible | `DEBUG` est à `False` dans `.env` → passez-le à `True` en développement. |
| `no such table` | Vous avez oublié `python manage.py migrate`. |
| Le port 8000 est occupé | Lancez `python manage.py runserver 8001` et ouvrez le port 8001. |
| `psycopg2` / connexion Postgres échoue | Vérifiez que PostgreSQL est démarré et que `DATABASE_URL` est correcte, ou retirez-la pour repasser en SQLite. |

---

## 10. Mise en production (résumé)

- `DEBUG=False`, `SECRET_KEY` fort, `ALLOWED_HOSTS` = votre domaine.
- `DATABASE_URL` vers PostgreSQL.
- `python manage.py collectstatic` (fichiers servis par WhiteNoise).
- Servir via `gunicorn config.wsgi` derrière un reverse-proxy HTTPS (Nginx).
- Contrôler : `python manage.py check --deploy`.
