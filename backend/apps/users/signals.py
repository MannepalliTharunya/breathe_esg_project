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


@receiver(post_save, sender=User)
def add_user_to_organizations(sender, instance, created, **kwargs):
    """
    Auto-add every new user to all active organizations as ADMIN.
    This ensures users who register after seeding can immediately
    access org-scoped data (metrics, periods, ESG data points, etc.)
    without needing a manual membership invite.
    """
    if not created:
        return
    try:
        from apps.organizations.models import Organization, OrganizationMembership
        orgs = Organization.objects.filter(is_active=True)
        for org in orgs:
            OrganizationMembership.objects.get_or_create(
                user=instance,
                organization=org,
                defaults={
                    "role": OrganizationMembership.Role.ADMIN,
                    "is_active": True,
                },
            )
    except Exception:
        # Never block registration due to membership errors
        pass
