"""
Lightweight middleware that attaches the authenticated user's organization
context to the request object for downstream use.
"""
import logging
from django.utils.functional import SimpleLazyObject

logger = logging.getLogger(__name__)


def _get_user_organization(request):
    """Resolve the active organization from the X-Organization-Id header."""
    from apps.organizations.models import OrganizationMembership

    if not hasattr(request, "_cached_organization"):
        org_id = request.headers.get("X-Organization-Id")
        user = getattr(request, "user", None)

        if org_id and user and user.is_authenticated:
            try:
                membership = OrganizationMembership.objects.select_related("organization").get(
                    user=user,
                    organization_id=org_id,
                    is_active=True,
                )
                request._cached_organization = membership.organization
                request._cached_membership = membership
            except OrganizationMembership.DoesNotExist:
                request._cached_organization = None
                request._cached_membership = None
        else:
            request._cached_organization = None
            request._cached_membership = None

    return request._cached_organization


class JWTAuthenticationMiddleware:
    """
    Attaches `request.organization` and `request.membership` as lazy objects
    so views can access them without extra DB queries when not needed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = SimpleLazyObject(lambda: _get_user_organization(request))
        response = self.get_response(request)
        return response
