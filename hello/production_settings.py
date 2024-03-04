"""
Django settings for hello project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


SECURE_HSTS_SECONDS = 31536000  # 1 year in seconds
SECURE_SSL_REDIRECT = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# When deploying to Azure App Service, add you <name>.azurewebsites.net
# domain to ALLOWED_HOSTS; you get an error message if you forget. When you add
# a specific host, you must also add 'localhost' and/or '127.0.0.1' for local
# debugging (which are enabled by default when ALLOWED_HOSTS is empty.)
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "eventcheck-in.com/",
    "eventcheck-in.com",
    "www.eventcheck-in.com/",
    "https://www.eventcheck-in.com/",
]

# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "hello",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hello.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "hello/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hello.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "guardia2_destiny",
        "USER": "guardia2_ben",
        "PASSWORD": "S)[],mtE0!8V",
        "HOST": "localhost",  # use localhost for on server testing and 192.250.227.60 for computer testing
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET time_zone='-08:00';",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_TZ = True  # use this to make the time zone work


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

# The location where the collectstatic command collects static files from apps.
# A dedicated static file server is typically used in production to serve files
# from this location, rather than relying on the app server to serve those files
# from various locations in the app. Doing so results in better overall performance.

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = "/home/guardia2/public_html/static_collected"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)


# Email settings
EMAIL_HOST = "mail.eventcheck-in.com"
EMAIL_PORT = 2525
# 'guardia2@mocha3039.mochahost.com'  # Replace with your email address
EMAIL_HOST_USER = "ritcareerfair@eventcheck-in.com"
# Replace with your email password
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_STARTTLS = True
DEFAULT_FROM_EMAIL = "ritcareerfair@eventcheck-in.com"
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_LOG_LEVEL = "DEBUG"
# WALLETPASS = {
#    'CERT_PATH': '',
#    'KEY_PATH': '',
# (None if isn't protected)
# MUST be in bytes-like
# }
