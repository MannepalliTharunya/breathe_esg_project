"""
Production settings — security-hardened, no DEBUG.
Designed for Render.com Docker deployment.
"""
from .base import *  # noqa: F401, F403
from decouple import config

DEBUG = False

# ---------------------------------------------------------------------------
# Logging — explicit production config, no third-party formatters required.
# Uses only stdlib logging so there is zero risk of ModuleNotFoundError on
# pythonjsonlogger or any other optional package.
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
# SECURE_SSL_REDIRECT is intentionally OFF.
# Render terminates SSL at the load balancer and forwards plain HTTP internally.
# Enabling this causes infinite redirect loops on Render.
SECURE_SSL_REDIRECT = False
# Tell Django that the original request was HTTPS (Render sets this header)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ---------------------------------------------------------------------------
# S3 Storage (optional)
# ---------------------------------------------------------------------------
if config("USE_S3", default=False, cast=bool):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = "private"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

# ---------------------------------------------------------------------------
# Sentry (optional — only initialised when SENTRY_DSN is set)
# ---------------------------------------------------------------------------
SENTRY_DSN = config("SENTRY_DSN", default="")
if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration(), CeleryIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False,
            environment="production",
        )
    except ImportError:
        pass
