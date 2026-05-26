from rest_framework import viewsets, permissions
from apps.core.permissions import IsOrganizationMember
from .models import Framework, FrameworkRequirement, OrganizationFramework
from .serializers import FrameworkSerializer, FrameworkRequirementSerializer, OrganizationFrameworkSerializer


class FrameworkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Framework.objects.filter(is_active=True)
    serializer_class = FrameworkSerializer
    permission_classes = [permissions.IsAuthenticated]


class FrameworkRequirementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FrameworkRequirementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = FrameworkRequirement.objects.select_related("framework")
        framework_id = self.request.query_params.get("framework_id")
        if framework_id:
            qs = qs.filter(framework_id=framework_id)
        return qs


class OrganizationFrameworkViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationFrameworkSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Organization-Id")
        return OrganizationFramework.objects.filter(organization_id=org_id).select_related("framework")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)
