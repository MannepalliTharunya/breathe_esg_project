"""
User lifecycle signals.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserPreferences


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Ensure every new user gets a preferences record."""
    if created:
        UserPreferences.objects.get_or_create(user=instance)
