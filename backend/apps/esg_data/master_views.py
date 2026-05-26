from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsOrganizationMember
from .models import ESGCategoryMaster, EmissionScope, CollectionMethod, DataSource, DataUpload
from .master_serializers import (
    ESGCategoryMasterSerializer,
    EmissionScopeSerializer,
    CollectionMethodSerializer,
    DataSourceSerializer,
    DataUploadSerializer,
)


class ActiveMasterViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list of active master data records."""

    permission_classes = [IsOrganizationMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return self.queryset.filter(is_active=True)


class ESGCategoryMasterViewSet(ActiveMasterViewSet):
    queryset = ESGCategoryMaster.objects.all()
    serializer_class = ESGCategoryMasterSerializer
    search_fields = ["name", "code"]
    ordering = ["code"]


class EmissionScopeViewSet(ActiveMasterViewSet):
    queryset = EmissionScope.objects.all()
    serializer_class = EmissionScopeSerializer
    search_fields = ["name", "code"]
    ordering = ["code"]


class CollectionMethodViewSet(ActiveMasterViewSet):
    queryset = CollectionMethod.objects.all()
    serializer_class = CollectionMethodSerializer
    search_fields = ["name", "code"]


class DataSourceViewSet(ActiveMasterViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    filterset_fields = ["source_type"]
    search_fields = ["name", "code"]


class DataUploadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DataUploadSerializer
    permission_classes = [IsOrganizationMember]
    ordering = ["-created_at"]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Organization-Id")
        return DataUpload.objects.filter(organization_id=org_id).select_related(
            "uploaded_by", "reporting_period"
        )
