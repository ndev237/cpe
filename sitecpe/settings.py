"""
Django settings for sitecpe project.

Bascule automatique entre :
 - DEV  (DEBUG=True)  -> base SQLite locale, ALLOWED_HOSTS ouvert
 - PROD (DEBUG=False) -> PostgreSQL via DATABASE_URL, sécurité durcie

Toute la configuration sensible est lue dans le fichier .env via
`python-decouple`. Voir .env.example à la racine du projet.
"""

from pathlib import Path
import os

from django.utils.translation import gettext_lazy as _
from decouple import config, Csv
import dj_database_url

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Sécurité de base
# ---------------------------------------------------------------------------
SECRET_KEY = config(
    'SECRET_KEY',
    default='django-insecure-dev-key-change-me-in-production',
)

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,0.0.0.0',
    cast=Csv(),
)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost,http://127.0.0.1',
    cast=Csv(),
)


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mon_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise sert les fichiers statiques en production sans Nginx
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sitecpe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sitecpe.wsgi.application'


# ---------------------------------------------------------------------------
# Base de données
#   - En dev   : SQLite (fichier db.sqlite3 à la racine)
#   - En prod  : PostgreSQL via DATABASE_URL
#     ex : postgres://user:password@host:5432/cpe_db
# ---------------------------------------------------------------------------
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ---------------------------------------------------------------------------
# Validation des mots de passe
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGES = [
    ('fr', _('French')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'fr'
TIME_ZONE = config('TIME_ZONE', default='Africa/Douala')
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']


# ---------------------------------------------------------------------------
# Fichiers statiques et médias
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Compression + cache busting via WhiteNoise (utilisé en prod)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'
                   if not DEBUG
                   else 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Sécurité spécifique à la production
# ---------------------------------------------------------------------------
if not DEBUG:
    # HTTPS / cookies
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS - active après avoir confirmé que HTTPS fonctionne partout
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # En-têtes
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'
