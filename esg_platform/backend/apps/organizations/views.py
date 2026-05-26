from rest_framework import viewsets, permissions
from apps.core.permissions import IsTenantMember, IsAdmin
from .models import Organization, Facility, Department
from .serializers import OrganizationSerializer, FacilitySerializer, DepartmentSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Organization.objects.all()
        return Organization.objects.filter(users=user, is_active=True)


class FacilityViewSet(viewsets.ModelViewSet):
    serializer_class = FacilitySerializer
    permission_classes = [IsTenantMember]
    filterset_fields = ["facility_type", "country", "is_active"]
    search_fields = ["name", "code", "city"]

    def get_queryset(self):
        return Facility.objects.filter(organization=self.request.organization).select_related("organization")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsTenantMember]
    filterset_fields = ["facility", "is_active"]
    search_fields = ["name", "code"]

    def get_queryset(self):
        return Department.objects.filter(organization=self.request.organization).select_related("facility")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)
