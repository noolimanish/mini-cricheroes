from pathlib import Path
from datetime import timedelta
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# Core settings
# ============================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-development-only-key"
)

DEBUG = os.getenv(
    "DEBUG",
    "False"
).lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]


# ============================================================
# Applications
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "drf_spectacular",

    "cricket",
]


# ============================================================
# Middleware
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# Database
# ============================================================

DB_ENGINE = os.getenv(
    "DB_ENGINE",
    "sqlite"
).lower()


if DB_ENGINE == "postgresql":

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }

else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================================================
# Password validation
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# Internationalization
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ============================================================
# Static files
# ============================================================

STATIC_URL = "static/"


# ============================================================
# Default primary key
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# Django REST Framework
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),
    "EXCEPTION_HANDLER": (
        "cricket.exception_handler.custom_exception_handler"
    ),
}


# ============================================================
# JWT
# ============================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}


# ============================================================
# Swagger / OpenAPI
# ============================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Mini-CricHeroes API",
    "DESCRIPTION": (
        "REST API for managing cricket matches, "
        "innings, players, teams, scoring and results."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# ============================================================
# Security settings
# ============================================================

if not DEBUG:

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"

    SECURE_REFERRER_POLICY = "same-origin"

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True
    
# ============================================================
# Logging
# ============================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "{asctime} | {levelname} | "
                "{name} | {message}"
            ),
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },

        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "standard",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        "cricket": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}