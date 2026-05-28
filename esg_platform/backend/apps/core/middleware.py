"""
TenantIsolationMiddleware — attaches the active organization to every request.
Views use request.organization to scope all queries.
"""
import logging
from django.utils.functional import SimpleLazyObject

logger = logging.getLogger(__name__)


def _resolve_organization(request):
    if not hasattr(request, "_cached_org"):
        from apps.organizations.models import Organization
        user = getattr(request, "user", None)

        if not (user and user.is_authenticated):
            request._cached_org = None
            return None

        # 1. Try explicit header first
        org_id = request.headers.get("X-Organization-Id")
        if org_id:
            try:
                request._cached_org = Organization.objects.get(
                    id=org_id,
                    members__user=user,
                    members__is_active=True,
                )
                return request._cached_org
            except Organization.DoesNotExist:
                pass

        # 2. Fall back to user's own organization field
        if hasattr(user, "organization") and user.organization_id:
            request._cached_org = user.organization
            return request._cached_org

        request._cached_org = None
    return request._cached_org


class TenantIsolationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = SimpleLazyObject(lambda: _resolve_organization(request))
        return self.get_response(request)
