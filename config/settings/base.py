"""
Django settings for help_desk_api project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


env = environ.Env()
env.read_env()

APP_ENV = env("APP_ENV")

DEBUG = env.bool("DEBUG", default=False)

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Server secrets
VCAP_SERVICES = env.json("VCAP_SERVICES", {})

# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "multiselectfield",
]

SERVICE_APPS = [
    "halo",
    "help_desk_api",
    "user",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + SERVICE_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

if "postgres" in VCAP_SERVICES:
    DATABASE_URL = VCAP_SERVICES["postgres"][0]["credentials"]["uri"]
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

DATABASES = {"default": env.db()}

# Redis
if "redis" in VCAP_SERVICES:
    credentials = VCAP_SERVICES["redis"][0]["credentials"]
    REDIS_URL = "rediss://:{}@{}:{}/0?ssl_cert_reqs=required".format(
        credentials["password"],
        credentials["host"],
        credentials["port"],
    )
else:
    REDIS_URL = os.environ.get("REDIS_URL", "")

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "help_desk_api.auth.ZenpyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Help desk interface
HELP_DESK_INTERFACE = env("HELP_DESK_INTERFACE", default="")
HELP_DESK_CREDS = env.dict("HELP_DESK_CREDS", default={})

AUTH_USER_MODEL = "user.User"

HALO_SUBDOMAIN = env("HALO_SUBDOMAIN")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
    }
}

REQUIRE_ZENDESK = env("REQUIRE_ZENDESK", default=False)
