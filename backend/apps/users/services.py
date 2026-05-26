"""
Business logic for user management — kept out of views.
"""
import logging
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

logger = logging.getLogger(__name__)

PASSWORD_RESET_CACHE_PREFIX = "pwd_reset:"
PASSWORD_RESET_TTL = 3600  # 1 hour
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


class AuthService:
    @staticmethod
    def generate_tokens(user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["role"] = user.role
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user,
        }

    @staticmethod
    def record_failed_login(user: User) -> None:
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = timezone.now() + timezone.timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            logger.warning("Account locked due to failed attempts: %s", user.email)
        user.save(update_fields=["failed_login_attempts", "locked_until"])

    @staticmethod
    def record_successful_login(user: User, ip_address: str) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_ip = ip_address
        user.save(update_fields=["failed_login_attempts", "locked_until", "last_login_ip"])

    @staticmethod
    def initiate_password_reset(email: str) -> None:
        from apps.core.utils import generate_secure_token
        from apps.notifications.tasks import send_password_reset_email

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # Don't reveal whether the email exists
            return

        token = generate_secure_token(64)
        cache_key = f"{PASSWORD_RESET_CACHE_PREFIX}{token}"
        cache.set(cache_key, str(user.id), PASSWORD_RESET_TTL)

        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        send_password_reset_email.delay(user.email, user.full_name, reset_url)
        logger.info("Password reset initiated for: %s", email)

    @staticmethod
    def confirm_password_reset(token: str, new_password: str) -> bool:
        cache_key = f"{PASSWORD_RESET_CACHE_PREFIX}{token}"
        user_id = cache.get(cache_key)
        if not user_id:
            return False

        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return False

        user.set_password(new_password)
        user.save(update_fields=["password"])
        cache.delete(cache_key)
        logger.info("Password reset completed for user: %s", user_id)
        return True


class UserService:
    @staticmethod
    def update_profile(user: User, validated_data: dict) -> User:
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def change_password(user: User, new_password: str) -> None:
        user.set_password(new_password)
        user.save(update_fields=["password"])
        logger.info("Password changed for user: %s", user.id)

    @staticmethod
    def deactivate_user(user: User, deactivated_by: User) -> None:
        user.is_active = False
        user.save(update_fields=["is_active"])
        logger.info("User %s deactivated by %s", user.id, deactivated_by.id)
