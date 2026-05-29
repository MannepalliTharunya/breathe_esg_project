FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Collect static files at build time.
# Dummy env vars prevent decouple from raising ImproperlyConfigured when the
# real secrets are not available in the build environment (Render build stage).
RUN DJANGO_SECRET_KEY=build-time-placeholder \
    DJANGO_ALLOWED_HOSTS=localhost \
    DATABASE_URL=postgres://placeholder:placeholder@localhost/placeholder \
    python manage.py collectstatic --noinput

# Create non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Render injects $PORT (defaults to 10000). Shell form required so $PORT expands at runtime.
# Startup sequence: migrate → create superuser → seed master data → serve
CMD python manage.py migrate --noinput && \
    python manage.py create_default_superuser && \
    python manage.py seed_esg_data && \
    gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
