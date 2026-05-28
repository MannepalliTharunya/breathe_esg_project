from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("admin", "analyst")


class IsViewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsAdminOrAnalyst(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ("admin", "analyst")


class IsTenantMember(BasePermission):
    """Ensures the user belongs to the organization in context."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Superadmins bypass tenant check
        if request.user.is_staff:
            return True
        # Organization must be resolved (from header or user.organization)
        return request.organization is not None

    def has_object_permission(self, request, view, obj):
        org = getattr(obj, "organization", None)
        if org is None:
            return True
        return org == request.organization


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
