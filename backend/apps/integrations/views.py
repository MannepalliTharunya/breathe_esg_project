from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.permissions import IsOrganizationAdmin
from .models import DataIntegration
from .serializers import DataIntegrationSerializer, DataIntegrationCreateSerializer


class DataIntegrationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Organization-Id")
        return DataIntegration.objects.filter(organization_id=org_id)

    def get_serializer_class(self):
        if self.action == "create":
            return DataIntegrationCreateSerializer
        return DataIntegrationSerializer

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="sync")
    def trigger_sync(self, request, pk=None):
        integration = self.get_object()
        from .tasks import run_integration_sync
        run_integration_sync.delay(str(integration.id))
        return Response({"detail": "Sync triggered."}, status=status.HTTP_202_ACCEPTED)
