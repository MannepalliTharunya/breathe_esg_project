import logging
from .models import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    def log(organization, user, action: str, resource_type: str,
            resource_id: str = "", before: dict = None, after: dict = None,
            ip_address: str = None, source_system: str = "web_ui"):
        try:
            AuditLog.objects.create(
                organization=organization,
                user=user,
                user_email=user.email if user else "",
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                before_value=before or {},
                after_value=after or {},
                ip_address=ip_address,
                source_system=source_system,
            )
        except Exception as e:
            logger.error("Failed to write audit log: %s", e)
