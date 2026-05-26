from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.permissions import IsOrganizationAdmin, IsOrganizationMember
from .models import Organization, Facility, OrganizationMembership, Department
from .serializers import OrganizationSerializer, FacilitySerializer, MembershipSerializer, DepartmentSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.all()
        org_ids = user.memberships.filter(is_active=True).values_list("organization_id", flat=True)
        return Organization.objects.filter(id__in=org_ids, is_active=True)

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsOrganizationAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        org = serializer.save()
        # Creator becomes owner
        OrganizationMembership.objects.create(
            user=self.request.user,
            organization=org,
            role=OrganizationMembership.Role.OWNER,
        )


class FacilityViewSet(viewsets.ModelViewSet):
    serializer_class = FacilitySerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        return Facility.objects.filter(organization_id=self.kwargs["org_pk"])

    def perform_create(self, serializer):
        serializer.save(organization_id=self.kwargs["org_pk"])


class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        return OrganizationMembership.objects.filter(
            organization_id=self.kwargs["org_pk"]
        ).select_related("user")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["org_pk"] = self.kwargs["org_pk"]
        return ctx


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        return Department.objects.filter(organization_id=self.kwargs["org_pk"])

    def perform_create(self, serializer):
        serializer.save(organization_id=self.kwargs["org_pk"])
