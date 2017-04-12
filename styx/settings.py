"""
Django settings for styx project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from decouple import config
from decouple import Csv
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast = bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast = Csv())


# Application definition

INSTALLED_APPS = [
    'app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'leaflet'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'styx.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'app.context_processors.get_bdd_settings',
                'app.context_processors.get_menu'
            ],
        },
    },
]

WSGI_APPLICATION = 'styx.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default' : {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER' : config('DB_USER'),
        'PASSWORD' : config('DB_PASSWORD'),
        'HOST' : config('DB_HOST'),
        'PORT' : ''
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = None

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

LEAFLET_CONFIG = {
    'DEFAULT_CENTER' : (43.20, 2.32),
    'DEFAULT_ZOOM' : 12,
    'MIN_ZOOM' : 9,
    'MAX_ZOOM' : 20,
}

# Je déclare mes options personnelles.
T_DONN_BDD_STR = {
    'AV_EP' : 'En projet',
    'AV_SOLDE' : 'Soldé',
    'AV_CP_ACC' : 'Accordé',
    'AV_CP_EA' : 'En attente',
    'AV_CP_REF' : 'Refusé',
    'AV_CP_SO' : 'Sans objet',
    'PPA_PRT' : 'Pourcentage de réalisation des travaux',
    'TVERS_ACOMPT' : 'Acompte',
    'TVERS_AF' : 'Avance forfaitaire',
    'TVERS_SOLDE' : 'Solde',
    'TAV_ARR_VALIDE' : 'Validé',
}

T_DONN_BDD_INT = {
    'PGRE_PK' : config('PGRE_PK', cast = int),
    'DDTM_PK' : config('DDTM_PK', cast = int)
}


ADMINS = [(config('ADMIN_FULLNAME'), config('ADMIN_EMAIL'))]
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'mail_dumps')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast = int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast = bool)
EMAIL_SUBJECT_PREFIX = '[STYX 2.0]'
SERVER_EMAIL = 'styx.smmar@localhost'
