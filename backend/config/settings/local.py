"""
Local development settings — SQLite, no Redis, no Celery broker.
Run with: DJANGO_SETTINGS_MODULE=config.settings.local
"""
from .base import *  # noqa: F401, F403

DEBUG = True
SECRET_KEY = "local-dev-secret-key-not-for-production"
ALLOWED_HOSTS = ["*"]

# ── SQLite — no MySQL needed locally ─────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# ── Disable Redis cache — use in-memory ──────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ── Celery — run tasks synchronously (no broker needed) ──────────────────────
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ── Email — print to console ─────────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── CORS — allow everything locally ──────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ── Remove production-only apps that need extra deps ─────────────────────────
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in (  # noqa: F405
    "django_prometheus",
)]

# Remove prometheus middleware
MIDDLEWARE = [m for m in MIDDLEWARE if "prometheus" not in m.lower()]  # noqa: F405

# ── Static files ──────────────────────────────────────────────────────────────
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# ── JWT — relaxed for dev ─────────────────────────────────────────────────────
from datetime import timedelta
SIMPLE_JWT = {
    **SIMPLE_JWT,  # noqa: F405
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "SIGNING_KEY": SECRET_KEY,
}

FRONTEND_URL = "http://localhost:3000"

# ── Override logging to remove json formatter dep ────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
