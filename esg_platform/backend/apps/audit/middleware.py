"""
Writes an AuditLog entry for every mutating API request automatically.
"""
import logging
from apps.core.utils import get_client_ip

logger = logging.getLogger(__name__)
AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SKIP_PATHS = {"/api/schema/", "/api/docs/", "/admin/", "/static/", "/media/"}


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method in AUDIT_METHODS and not any(request.path.startswith(p) for p in SKIP_PATHS):
            self._write(request, response)
        return response

    def _write(self, request, response):
        from .services import AuditService
        try:
            user = getattr(request, "user", None)
            org = getattr(request, "_cached_org", None)
            AuditService.log(
                organization=org,
                user=user if user and user.is_authenticated else None,
                action=self._infer_action(request),
                resource_type=self._resource_type(request.path),
                resource_id=self._resource_id(request.path),
                ip_address=get_client_ip(request),
                after={"status_code": response.status_code, "path": request.path},
            )
        except Exception:
            logger.exception("AuditMiddleware write failed")

    @staticmethod
    def _infer_action(request):
        return {"POST": "create", "PUT": "update", "PATCH": "update", "DELETE": "delete"}.get(request.method, "unknown")

    @staticmethod
    def _resource_type(path):
        parts = [p for p in path.split("/") if p and p not in ("api",)]
        return parts[0] if parts else "unknown"

    @staticmethod
    def _resource_id(path):
        parts = [p for p in path.split("/") if p and p not in ("api",)]
        return parts[1] if len(parts) > 1 else ""
