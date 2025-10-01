"""
Django settings for libroscontables project.
"""
import os
import dj_database_url 
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Se obtiene la SECRET_KEY de una variable de entorno en producción.
SECRET_KEY = os.environ.get('SECRET_KEY', default='django-insecure-ua2#x*o%^ecx^$il1^x!r4)@%7ar^*v)g3c=r9l()1ou63ocie')

# SECURITY WARNING: don't run with debug turned on in production!
# El modo DEBUG se deshabilita automáticamente en Render.
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []

# Render proveerá el nombre del host en una variable de entorno.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'libros',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise Middleware para servir archivos estáticos:
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'libroscontables.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Apunta a tu carpeta de plantillas raíz
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.middleware.MessageMiddleware',
                                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'libroscontables.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        # Render usará la variable de entorno DATABASE_URL.
        # Si no la encuentra, usará tu configuración local.
        default='postgresql://postgres:1704@localhost/libroscontables',
        conn_max_age=600
    )
}

# Password validation
# ... (AUTH_PASSWORD_VALIDATORS se mantiene igual) ...
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
# ... (Internationalization se mantiene igual) ...
LANGUAGE_CODE = 'es-sv' # Cambiado a español de El Salvador
TIME_ZONE = 'America/El_Salvador' # Cambiado a la zona horaria de El Salvador
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Le dice a Django dónde buscar tus archivos estáticos en desarrollo.
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Le dice a Django dónde recolectar todos los archivos estáticos para producción.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# ... (DEFAULT_AUTO_FIELD se mantiene igual) ...
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'