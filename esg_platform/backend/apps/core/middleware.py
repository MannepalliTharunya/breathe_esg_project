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
        org_id = request.headers.get("X-Organization-Id")

        if user and user.is_authenticated and org_id:
            try:
                request._cached_org = Organization.objects.get(
                    id=org_id,
                    members__user=user,
                    members__is_active=True,
                )
            except Organization.DoesNotExist:
                request._cached_org = None
        elif user and user.is_authenticated and hasattr(user, "organization"):
            request._cached_org = user.organization
        else:
            request._cached_org = None
    return request._cached_org


class TenantIsolationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = SimpleLazyObject(lambda: _resolve_organization(request))
        return self.get_response(request)
