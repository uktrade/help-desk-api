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
from django_log_formatter_asim import ASIMFormatter
from dbt_copilot_python.database import database_url_from_env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


env = environ.Env()
env.read_env()

APP_ENV = env("APP_ENV")

DEBUG = env.bool("DEBUG", default=False)

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

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
    "drf_spectacular",
    "elasticapm.contrib.django",
]

SERVICE_APPS = [
    "halo",
    "help_desk_api",
    "user",
    "healthcheck",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + SERVICE_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "help_desk_api/management/templates",
        ],
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

DATABASE_URL = database_url_from_env("DATABASE_CREDENTIALS")

DATABASES = {"default": env.db()}

# Redis
REDIS_URL = env("REDIS_URL")

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
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

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
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",  # /PS-IGNORE
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Help Desk Service",  # /PS-IGNORE
    "DESCRIPTION": """
    Acts as a proxy server for Zendesk API requests,
    translates Zendesk API requests into Halo API requests,
    and translates Halo API responses into Zendesk API responses.
    """,  # /PS-IGNORE
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_AUTHENTICATION": [],
}

AUTH_USER_MODEL = "user.User"

HALO_SUBDOMAIN = env("HALO_SUBDOMAIN")

USER_DATA_CACHE = "userdata"
TICKET_DATA_CACHE = "ticketdata"
UPLOAD_DATA_CACHE = "uploaddata"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
    },
    USER_DATA_CACHE: {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": f"middleware_{USER_DATA_CACHE}_cache_table",
        "TIMEOUT": 86_400,  # seconds; == 24 hours
    },
    TICKET_DATA_CACHE: {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": f"middleware_{TICKET_DATA_CACHE}_cache_table",
        "TIMEOUT": 432_000,  # seconds; == 5 days
    },
    UPLOAD_DATA_CACHE: {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": f"middleware_{UPLOAD_DATA_CACHE}_cache_table",
        "TIMEOUT": 432_000,  # seconds; == 5 days
    },
}

REQUIRE_ZENDESK = env("REQUIRE_ZENDESK", default=False)

'''
OPENAPI_CONFIG = {
    "title": "Help Desk Service",
    "description": """
    Acts as a proxy server for Zendesk API requests,
    translates Zendesk API requests into Halo API requests,
    and translates Halo API responses into Zendesk API responses.
    """,  # /PS-IGNORE
}
'''

CLAM_AV_USERNAME = env("CLAM_AV_USERNAME", default="")
CLAM_AV_PASSWORD = env("CLAM_AV_PASSWORD", default="")
CLAM_AV_URL = env("CLAM_AV_URL", default="")
CLAM_AV_HOST = env("CLAM_AV_HOST", default="")

# Enable HSTS
# To disable in a local development environment,
# set the SET_HSTS_HEADERS environment variable to a value that Python will evaulate as False, e.g.
# export SET_HSTS_HEADERS=''

# Set security related headers
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # /PS-IGNORE

SET_HSTS_HEADERS = env.bool("SET_HSTS_HEADERS", default=True)
if SET_HSTS_HEADERS:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True

ELASTIC_APM = {
    "SERVICE_NAME": "help-desk-service",
    "SECRET_TOKEN": env.str("ELASTIC_APM_SECRET_TOKEN"),
    "SERVER_URL": "https://apm.elk.uktrade.digital",
    "ENVIRONMENT": APP_ENV,
    "SERVER_TIMEOUT": env.str("ELASTIC_APM_SERVER_TIMEOUT"),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "asim_formatter": {
            "()": ASIMFormatter,
        },
        "simple": {
            "style": "{",
            "format": "{asctime} {levelname} {message}",
        },
    },
    "handlers": {
        "asim": {
            "class": "logging.StreamHandler",
            "formatter": "asim_formatter",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["asim"],
            "level": "INFO",
            "propagate": False,
        }
    },
}
