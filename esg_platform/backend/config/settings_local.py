"""
Local dev settings — SQLite, no Redis, tasks run synchronously.
Usage: DJANGO_SETTINGS_MODULE=config.settings_local
"""
from .settings import *  # noqa

DEBUG = True
SECRET_KEY = "local-dev-secret-not-for-production"
ALLOWED_HOSTS = ["*"]

# SQLite — no MySQL needed locally
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_local.sqlite3",
    }
}

# In-memory cache — no Redis needed
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Run Celery tasks synchronously in dev
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Print emails to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Allow all CORS in dev
CORS_ALLOW_ALL_ORIGINS = True

# Simpler static files
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Override logging — no json formatter dep
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "{levelname} {asctime} {module}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}

# JWT — long-lived tokens for dev convenience
from datetime import timedelta
SIMPLE_JWT = {
    **SIMPLE_JWT,
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "SIGNING_KEY": SECRET_KEY,
}
