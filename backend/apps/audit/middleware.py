"""
Middleware that writes an AuditLog entry for every mutating API request.
"""
import json
import logging
from apps.core.utils import get_client_ip

logger = logging.getLogger(__name__)

AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SKIP_PATHS = {"/api/schema/", "/metrics", "/health/", "/admin/"}


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method in AUDIT_METHODS and not any(
            request.path.startswith(p) for p in SKIP_PATHS
        ):
            self._write_log(request, response)

        return response

    def _write_log(self, request, response):
        from .models import AuditLog

        try:
            user = getattr(request, "user", None)
            org = getattr(request, "_cached_organization", None)

            AuditLog.objects.create(
                user_id=user.id if user and user.is_authenticated else None,
                user_email=user.email if user and user.is_authenticated else "",
                organization_id=org.id if org else None,
                action=self._infer_action(request.method, request.path),
                resource_type=self._extract_resource_type(request.path),
                resource_id=self._extract_resource_id(request.path),
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                request_method=request.method,
                request_path=request.path[:500],
                status_code=response.status_code,
            )
        except Exception:
            logger.exception("Failed to write audit log")

    @staticmethod
    def _infer_action(method: str, path: str) -> str:
        if "approve" in path:
            return "approve"
        if "reject" in path:
            return "reject"
        if "export" in path:
            return "export"
        if "import" in path:
            return "import"
        return {"POST": "create", "PUT": "update", "PATCH": "update", "DELETE": "delete"}.get(method, "update")

    @staticmethod
    def _extract_resource_type(path: str) -> str:
        parts = [p for p in path.split("/") if p and p not in ("api", "v1")]
        return parts[0] if parts else "unknown"

    @staticmethod
    def _extract_resource_id(path: str) -> str:
        parts = [p for p in path.split("/") if p and p not in ("api", "v1")]
        return parts[1] if len(parts) > 1 else ""
