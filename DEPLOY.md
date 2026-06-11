# Déploiement - SiteCPE

## Développement (SQLite local)

```bash
cp .env.example .env        # puis ajuster si besoin
python -m venv venv
source venv/bin/activate    # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Le `.env` par défaut laisse `DATABASE_URL` vide, donc Django utilise SQLite.

---

## Production (VPS Linux + PostgreSQL + gunicorn + nginx)

### 1. Préparer le serveur

```bash
sudo apt update && sudo apt install -y \
    python3-venv python3-pip \
    postgresql postgresql-contrib \
    nginx \
    libpq-dev build-essential
```

### 2. Créer la base PostgreSQL

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE cpe_db;
CREATE USER cpe_user WITH PASSWORD 'UN_MOT_DE_PASSE_FORT';
ALTER ROLE cpe_user SET client_encoding TO 'utf8';
ALTER ROLE cpe_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cpe_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE cpe_db TO cpe_user;
SQL
```

### 3. Cloner et configurer

```bash
cd /var/www
sudo git clone <votre-repo> sitecpe
cd sitecpe
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Créer `/var/www/sitecpe/.env` :

```env
DEBUG=False
SECRET_KEY=<générée avec get_random_secret_key()>
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
CSRF_TRUSTED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
DATABASE_URL=postgres://cpe_user:UN_MOT_DE_PASSE_FORT@127.0.0.1:5432/cpe_db
TIME_ZONE=Africa/Douala
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### 4. Migrations + statiques

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py compilemessages
```

### 5. Service systemd pour gunicorn

`/etc/systemd/system/sitecpe.service` :

```ini
[Unit]
Description=Gunicorn SiteCPE
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sitecpe
EnvironmentFile=/var/www/sitecpe/.env
ExecStart=/var/www/sitecpe/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/sitecpe.sock \
    sitecpe.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now sitecpe
```

### 6. Nginx (vhost minimal)

`/etc/nginx/sites-available/sitecpe` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location /static/ { alias /var/www/sitecpe/staticfiles/; }
    location /media/  { alias /var/www/sitecpe/media/; }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/sitecpe.sock;
    }

    client_max_body_size 25M;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/sitecpe /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

### 7. Vérification

```bash
DEBUG=False python manage.py check --deploy
```
