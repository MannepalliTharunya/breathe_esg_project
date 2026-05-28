import logging
from django.http import HttpResponse
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from apps.core.permissions import IsTenantMember, IsAdminOrAnalyst
from .models import UploadBatch, RawRecord
from .serializers import UploadBatchSerializer, UploadBatchCreateSerializer, RawRecordSerializer
from .tasks import process_upload_batch
from .templates import TEMPLATES

logger = logging.getLogger(__name__)


@extend_schema(tags=["Ingestion"])
class UploadBatchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantMember, IsAdminOrAnalyst]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["source_type", "status", "facility"]
    ordering_fields = ["created_at", "total_rows", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UploadBatch.objects.none()
        return UploadBatch.objects.filter(
            organization=self.request.organization
        ).select_related("facility", "created_by").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return UploadBatchCreateSerializer
        return UploadBatchSerializer

    def get_parsers(self):
        if getattr(self, "action", None) == "create":
            return [MultiPartParser(), FormParser()]
        return super().get_parsers()

    def create(self, request, *args, **kwargs):
        serializer = UploadBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        batch = UploadBatch.objects.create(
            organization=request.organization,
            created_by=request.user,
            source_type=vd["source_type"],
            file=vd["file"],
            original_filename=vd["file"].name,
            file_size_bytes=vd["file"].size,
            facility=vd.get("facility"),
            notes=vd.get("notes", ""),
        )

        # Kick off async processing
        process_upload_batch.delay(str(batch.id))

        return Response(UploadBatchSerializer(batch).data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"], url_path="reprocess")
    def reprocess(self, request, pk=None):
        """Re-trigger ingestion for a failed batch."""
        batch = self.get_object()
        if batch.status == UploadBatch.Status.PROCESSING:
            return Response(
                {"error": {"message": "Batch is already being processed."}},
                status=status.HTTP_409_CONFLICT,
            )
        batch.status = UploadBatch.Status.PENDING
        batch.error_summary = ""
        batch.save(update_fields=["status", "error_summary"])
        process_upload_batch.delay(str(batch.id))
        return Response({"detail": "Reprocessing started."}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        """Return first 20 raw records for a batch (CSV preview)."""
        batch = self.get_object()
        records = RawRecord.objects.filter(batch=batch).order_by("row_number")[:20]
        return Response(RawRecordSerializer(records, many=True).data)


@extend_schema(tags=["Ingestion"])
class RawRecordListView(generics.ListAPIView):
    serializer_class = RawRecordSerializer
    permission_classes = [IsTenantMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["batch", "source_type", "status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return RawRecord.objects.none()
        return RawRecord.objects.filter(
            organization=self.request.organization
        ).select_related("batch").order_by("batch", "row_number")


@extend_schema(tags=["Ingestion"])
@api_view(["GET"])
@permission_classes([AllowAny])
def download_template(request, source_type: str):
    """
    Download a sample CSV template for the given source type.
    No auth required — helps new users understand the expected format.
    """
    if source_type not in TEMPLATES:
        return Response(
            {"error": {"message": f"Unknown source type: {source_type!r}. Use: sap, utility, travel"}},
            status=status.HTTP_400_BAD_REQUEST,
        )
    filename, content = TEMPLATES[source_type]
    response = HttpResponse(content, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Access-Control-Allow-Origin"] = "*"
    return response
