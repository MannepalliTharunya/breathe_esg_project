from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizationMember(BasePermission):
    """Allows access only to members of the organization in the request context."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        org_id = request.headers.get("X-Organization-Id") or request.query_params.get("organization_id")
        if not org_id:
            return False
        return request.user.memberships.filter(
            organization_id=org_id, is_active=True
        ).exists()

    def has_object_permission(self, request, view, obj):
        org_id = getattr(obj, "organization_id", None)
        if not org_id:
            return True
        return request.user.memberships.filter(
            organization_id=org_id, is_active=True
        ).exists()


class IsOrganizationAdmin(IsOrganizationMember):
    """Restricts write operations to org admins; read is open to all members."""

    ADMIN_ROLES = ("admin", "owner")

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method in SAFE_METHODS:
            return True
        org_id = request.headers.get("X-Organization-Id") or request.query_params.get("organization_id")
        return request.user.memberships.filter(
            organization_id=org_id, role__in=self.ADMIN_ROLES, is_active=True
        ).exists()


class IsOwnerOrReadOnly(BasePermission):
    """Object-level: only the owner can write; others can read."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "created_by", None) == request.user
