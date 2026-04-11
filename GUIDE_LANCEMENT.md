# Guide de Lancement MediSecure 🏥

Ce guide vous aidera à configurer et à lancer la plateforme MediSecure sur votre machine locale.

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- [Docker](https://www.docker.com/products/docker-desktop) et Docker Compose
- [Python 3.12+](https://www.python.org/downloads/) (pour le mode local)
- [uv](https://github.com/astral-sh/uv) (gestionnaire de paquets Python ultra-rapide utilisé dans ce projet)
- [pnpm](https://pnpm.io/) (gestionnaire de paquets Node.js recommandé)
- [Node.js 24+](https://nodejs.org/) (pour la compilation du frontend)

---

## 🐳 Méthode 1 : Docker (Recommandé)

C'est la méthode la plus simple car elle configure automatiquement la base de données PostgreSQL, Redis pour Celery, et Mailpit pour les emails.

### 1. Construction des images

```powershell
docker compose -f docker-compose.local.yml build
```

*Note : Si vous avez `just` installé, vous pouvez utiliser `just build`.*

### 2. Lancement des services

```powershell
docker compose -f docker-compose.local.yml up
```

*Ou `just up`.*

L'application sera accessible sur :

- **Web** : [http://localhost:8000](http://localhost:8000)
- **Mailpit (Emails)** : [http://localhost:8025](http://localhost:8025)

### 3. Initialisation (Migrations et Superutilisateur)

Dans un nouveau terminal :

```powershell
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
```

---

## 💻 Méthode 2 : Installation Locale (Sans Docker)

Utilisez cette méthode si vous préférez travailler directement sur votre OS. Vous devrez avoir une instance PostgreSQL et Redis qui tournent localement.

### 1. Préparation de l'environnement (Windows)

Ouvrez votre terminal (PowerShell ou CMD) à la racine du projet et activez l'environnement :

```powershell
.\.venv\Scripts\Activate
```

*Note : Si vous utilisez `uv`, vous pouvez aussi simplement préfixer vos commandes par `uv run`.*

### 2. Installation des dépendances

```powershell
# Dépendances Python
uv sync

# Dépendances Frontend
pnpm install
```

### 3. Base de données et Services (Docker Recommandé)

Même pour une exécution locale, vous aurez besoin d'une base de données. Le plus simple est de lancer uniquement la base de données et redis via Docker :

```powershell
docker compose -f docker-compose.local.yml up -d postgres redis mailpit
```

### 4. Lancement des serveurs

Une fois l'environnement activé (`.\.venv\Scripts\Activate`) :

- **Terminal 1 : Django**

  ```powershell
  python manage.py migrate
  python manage.py runserver
  ```
- **Terminal 2 : Webpack (Frontend)**

  ```powershell
  pnpm run dev
  ```
- **Terminal 3 : Celery (Tâches de fond)**

  ```powershell
  uv run celery -A config.celery_app worker -l info
  ```

---

## 🛠️ Commandes Utiles

### Tests

```powershell
# Exécuter tous les tests
uv run pytest

# Vérifier la couverture des tests
uv run coverage run -m pytest
uv run coverage report
```

### Qualité du Code (Linting)

```powershell
uv run ruff check .
uv run mypy medisecure
```

### Reset de la base de données (Docker)

```powershell
docker compose -f docker-compose.local.yml down -v
```

*(Attention : cela supprime toutes les données !)*
