# Lancement rapide MediSecure

## Prérequis
- Docker Desktop lancé
- Être dans le dossier `medisecure/`

---

## Option A — Docker complet (recommandé)

```powershell
# 1. Construire les images (une seule fois)
docker compose -f docker-compose.local.yml build

# 2. Lancer tous les services
docker compose -f docker-compose.local.yml up

# 3. Dans un 2e terminal — migrations + superutilisateur (une seule fois)
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
```

**Accès :**
- App → http://localhost:8000
- Dashboard admin → http://localhost:8000/dashboard/
- Django admin → http://localhost:8000/admin/
- Emails (Mailpit) → http://localhost:8025

---

## Option B — Sans Docker (SQLite, mode dev rapide)

> Pas besoin de PostgreSQL ni Redis. Idéal pour voir les templates rapidement.
> Les variables d'environnement sont lues automatiquement depuis le fichier `.env`.

```powershell
# 1. Activer l'environnement virtuel
.\.venv\Scripts\Activate

# 2. Migrations (une seule fois ou après changement de modèle)
python manage.py migrate

# 4. Créer un superutilisateur admin (une seule fois)
python manage.py createsuperuser

# 5. Lancer le serveur Django (Terminal 1)
python manage.py runserver

# 6. Lancer Webpack — compile le CSS/JS (Terminal 2)
npm run dev
```

**Accès :**
- App → http://localhost:8000
- Dashboard admin → http://localhost:8000/dashboard/
- Django admin → http://localhost:8000/admin/

> Le dashboard `/dashboard/` est accessible uniquement si le compte a `is_staff=True` ou `role=ADMIN`.
> Pour donner les droits admin via shell :
> ```powershell
> python manage.py shell -c "from medisecure.users.models import User; u=User.objects.get(email='ton@email.com'); u.is_staff=True; u.role='ADMIN'; u.statut=True; u.save()"
> ```

---

## Commandes utiles

```powershell
# Relancer après un changement de modèle
python manage.py makemigrations
python manage.py migrate

# Lancer les tests
python -m pytest tests/ --create-db

# Vider et recréer la base SQLite
Remove-Item db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```
