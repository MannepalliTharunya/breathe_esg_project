"""
Creates a default superuser if no users exist.
Safe to run on every deploy — skips if a superuser already exists.

Reads credentials from environment variables:
  DJANGO_SUPERUSER_EMAIL    (default: admin@esgplatform.com)
  DJANGO_SUPERUSER_PASSWORD (default: Admin@123456)

Run: python manage.py create_default_superuser
"""
from django.core.management.base import BaseCommand
from decouple import config


class Command(BaseCommand):
    help = "Creates a default superuser if none exists."

    def handle(self, *args, **options):
        from apps.users.models import User

        email = config("DJANGO_SUPERUSER_EMAIL", default="admin@esgplatform.com")
        password = config("DJANGO_SUPERUSER_PASSWORD", default="Admin@123456")

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("Superuser already exists — skipping.")
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            first_name="Admin",
            last_name="User",
        )
        self.stdout.write(self.style.SUCCESS(
            f"Superuser created: {email}"
        ))
