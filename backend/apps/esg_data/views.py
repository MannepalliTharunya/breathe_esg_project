import io
import logging
import pandas as pd
from django.http import HttpResponse
from rest_framework import generics, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.core.permissions import IsOrganizationMember, IsOrganizationAdmin
from .models import (
    MetricDefinition,
    ReportingPeriod,
    ESGDataPoint,
    ESGTarget,
    MaterialityAssessment,
    EmissionCategory,
    DataUpload,
)
from .master_serializers import DataUploadSerializer
from .serializers import (
    MetricDefinitionSerializer,
    ReportingPeriodSerializer,
    ESGDataPointReadSerializer,
    ESGDataPointWriteSerializer,
    DataPointStatusUpdateSerializer,
    ESGTargetSerializer,
    MaterialityAssessmentSerializer,
    EmissionCategorySerializer,
)
from .services import DataPointWorkflowService, ESGAggregationService, BulkDataImportService
from .filters import ESGDataPointFilter

logger = logging.getLogger(__name__)


class MetricDefinitionViewSet(ModelViewSet):
    queryset = MetricDefinition.objects.all()
    serializer_class = MetricDefinitionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "data_type", "is_required"]
    search_fields = ["code", "name", "description"]
    ordering_fields = ["category", "code", "name"]
    ordering = ["category", "code"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.IsAuthenticated()]
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsOrganizationAdmin()]
        return [IsOrganizationMember()]


class ReportingPeriodViewSet(ModelViewSet):
    serializer_class = ReportingPeriodSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Organization-Id")
        return ReportingPeriod.objects.filter(organization_id=org_id).order_by("-start_date")

    def perform_create(self, serializer):
        org_id = self.request.headers.get("X-Organization-Id")
        serializer.save(organization_id=org_id)


@extend_schema_view(
    list=extend_schema(summary="List ESG data points"),
    create=extend_schema(summary="Submit a new ESG data point"),
    retrieve=extend_schema(summary="Get a single data point"),
    update=extend_schema(summary="Update a data point"),
    destroy=extend_schema(summary="Delete a data point"),
)
class ESGDataPointViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ESGDataPointFilter
    ordering_fields = ["created_at", "status", "metric__category"]
    ordering = ["-created_at"]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Organization-Id")
        return (
            ESGDataPoint.objects.filter(organization_id=org_id)
            .select_related("metric", "reporting_period", "facility", "submitted_by", "reviewed_by")
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ESGDataPointWriteSerializer
        return ESGDataPointReadSerializer

    def get_permissions(self):
        if self.action in ("import_template", "bulk_import_preview"):
            return [permissions.IsAuthenticated()]
        return [IsOrganizationMember()]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["organization"] = getattr(self.request, "organization", None)
        return ctx

    @action(detail=True, methods=["post"], url_path="status")
    def update_status(self, request, pk=None):
        data_point = self.get_object()
        serializer = DataPointStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated = DataPointWorkflowService.transition(
                data_point,
                serializer.validated_data["status"],
                request.user,
                serializer.validated_data.get("review_notes", ""),
            )
        except ValueError as e:
            return Response(
                {"error": {"code": "invalid_transition", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ESGDataPointReadSerializer(updated).data)

    def _parse_upload_file(self, file):
        content = file.read()
        if file.name.lower().endswith(".csv"):
            return pd.read_csv(io.BytesIO(content))
        return pd.read_excel(io.BytesIO(content))

    def _get_reporting_period(self, request, period_id):
        try:
            return ReportingPeriod.objects.get(id=period_id, organization=request.organization)
        except ReportingPeriod.DoesNotExist:
            return None

    @action(detail=False, methods=["get"], url_path="import-template")
    def import_template(self, request):
        """Download CSV template for bulk import."""
        csv_content = (
            "metric_code,value,facility_code,data_source,collection_method,notes\n"
            "ELECTRICITY_CONSUMPTION,12500.5,hyderabad_plant,sap,erp_system,January grid usage\n"
            "DIESEL_CONSUMPTION,890.2,chennai_factory,utility_portal,utility_bill,Fleet diesel\n"
            "BUSINESS_TRAVEL_EMISSIONS,45.8,,concur,erp_system,Q1 business travel\n"
        )
        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="esg_import_template.csv"'
        return response

    @action(detail=False, methods=["post"], url_path="bulk-import/preview", parser_classes=[MultiPartParser])
    def bulk_import_preview(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": {"code": "bad_request", "message": "file is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            df = self._parse_upload_file(file)
        except Exception as e:
            return Response(
                {"error": {"code": "parse_error", "message": f"Could not parse file: {e}"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        df, original_columns = BulkDataImportService.normalize_columns(df)
        validation_errors = BulkDataImportService.validate_dataframe(df, original_columns)
        preview = (
            BulkDataImportService.preview_dataframe(df)
            if not validation_errors
            else []
        )
        return Response({
            "preview": preview,
            "row_count": len(df),
            "errors": validation_errors,
            "detected_columns": original_columns,
        })

    @action(detail=False, methods=["post"], url_path="bulk-import", parser_classes=[MultiPartParser])
    def bulk_import(self, request):
        file = request.FILES.get("file")
        period_id = request.data.get("reporting_period_id")
        source_type = request.data.get("source_type", "manual")
        preview_only = request.data.get("preview_only", "false").lower() == "true"

        if not file or not period_id:
            return Response(
                {"error": {"code": "bad_request", "message": "file and reporting_period_id are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        period = self._get_reporting_period(request, period_id)
        if not period:
            return Response(
                {"error": {"code": "not_found", "message": "Reporting period not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            df = self._parse_upload_file(file)
        except Exception as e:
            return Response(
                {"error": {"code": "parse_error", "message": f"Could not parse file: {e}"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = BulkDataImportService.import_from_dataframe(
            df,
            request.organization,
            period,
            request.user,
            file_name=file.name,
            source_type=source_type,
            commit=not preview_only,
        )
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        org_id = self.request.headers.get("X-Organization-Id")
        period_id = request.query_params.get("period_id")
        data = ESGAggregationService.get_category_summary(org_id, period_id)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="dashboard-stats")
    def dashboard_stats(self, request):
        org_id = self.request.headers.get("X-Organization-Id")
        period_id = request.query_params.get("period_id")
        data_points = ESGDataPoint.objects.filter(organization_id=org_id)
        if period_id:
            data_points = data_points.filter(reporting_period_id=period_id)

        total_uploaded = data_points.count()
        approved_rows = data_points.filter(status="approved").count()
        failed_rows = data_points.filter(status="rejected").count()
        suspicious_rows = data_points.filter(confidence_level__lt=80).count()

        approved_qs = data_points.filter(status="approved")
        emissions = ESGAggregationService.aggregate_scope_totals(approved_qs)

        return Response({
            "total_uploaded_records": total_uploaded,
            "suspicious_rows": suspicious_rows,
            "approved_rows": approved_rows,
            "failed_rows": failed_rows,
            "emissions_by_scope": emissions,
        })

    @action(detail=False, methods=["get"], url_path="upload-history")
    def upload_history(self, request):
        org_id = self.request.headers.get("X-Organization-Id")
        uploads = DataUpload.objects.filter(organization_id=org_id).select_related(
            "uploaded_by", "reporting_period"
        )

        page = self.paginate_queryset(uploads)
        if page is not None:
            serializer = DataUploadSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DataUploadSerializer(uploads, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="analytics")
    def analytics(self, request):
        org_id = self.request.headers.get("X-Organization-Id")
        period_id = request.query_params.get("period_id")
        
        from django.db.models import Sum
        
        # Category breakdown of approved data points
        from .models import ESGCategory
        category_data = {}
        for cat in ESGCategory.values:
            qs = ESGDataPoint.objects.filter(organization_id=org_id, metric__category=cat, status="approved")
            if period_id:
                qs = qs.filter(reporting_period_id=period_id)
            category_data[cat] = qs.count()
            
        # Facility breakdown
        facility_qs = ESGDataPoint.objects.filter(
            organization_id=org_id,
            status="approved",
            facility__isnull=False
        )
        if period_id:
            facility_qs = facility_qs.filter(reporting_period_id=period_id)
        facility_qs = facility_qs.values("facility__name").annotate(total=Sum("numeric_value")).order_by("-total")[:10]
        
        facility_breakdown = [
            {"facility": item["facility__name"], "value": float(item["total"] or 0)}
            for item in facility_qs
        ]
        
        # Emissions trend
        trend = ESGAggregationService.get_emissions_trend(org_id)
        scope_codes = ESGAggregationService.SCOPE_METRIC_CODES
        years_data = {}
        for item in trend:
            date_val = item["reporting_period__start_date"]
            year = str(date_val.year) if hasattr(date_val, "year") else str(date_val)[:4]
            code = item["metric__code"]
            total = float(item["total"] or 0)

            if year not in years_data:
                years_data[year] = {"year": year, "scope1": 0.0, "scope2": 0.0, "scope3": 0.0}

            for scope, codes in scope_codes.items():
                if code in codes:
                    years_data[year][scope] += total

        formatted_trend = sorted(years_data.values(), key=lambda x: x["year"])
        
        return Response({
            "category_distribution": category_data,
            "facility_breakdown": facility_breakdown,
            "emissions_trend": formatted_trend
        })

    @action(detail=False, methods=["get"], url_path="emissions-summary")
    def emissions_summary(self, request):
        org_id = self.request.headers.get("X-Organization-Id")
        period_id = request.query_params.get("period_id")
        data_points = ESGDataPoint.objects.filter(organization_id=org_id, status="approved")
        if period_id:
            data_points = data_points.filter(reporting_period_id=period_id)

        emissions = ESGAggregationService.aggregate_scope_totals(data_points)
        total_emissions = sum(emissions.values())

        return Response({
            **emissions,
            "total_emissions": total_emissions,
            "unit": "tCO2e",
        })


class ESGTargetViewSet(ModelViewSet):
    serializer_class = ESGTargetSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Organization-Id")
        return ESGTarget.objects.filter(organization_id=org_id).select_related("metric")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)


class MaterialityAssessmentViewSet(ModelViewSet):
    serializer_class = MaterialityAssessmentSerializer
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Organization-Id")
        return MaterialityAssessment.objects.filter(organization_id=org_id)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class EmissionCategoryViewSet(ModelViewSet):
    queryset = EmissionCategory.objects.all()
    serializer_class = EmissionCategorySerializer
    permission_classes = [IsOrganizationMember]
