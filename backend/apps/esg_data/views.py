import io
import logging
import pandas as pd
from rest_framework import generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.core.permissions import IsOrganizationMember, IsOrganizationAdmin
from .models import MetricDefinition, ReportingPeriod, ESGDataPoint, ESGTarget, MaterialityAssessment, EmissionCategory
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
    permission_classes = [IsOrganizationMember]
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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["organization"] = self.request.organization
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

    @action(detail=False, methods=["post"], url_path="bulk-import", parser_classes=[MultiPartParser])
    def bulk_import(self, request):
        file = request.FILES.get("file")
        period_id = request.data.get("reporting_period_id")

        if not file or not period_id:
            return Response(
                {"error": {"code": "bad_request", "message": "file and reporting_period_id are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            period = ReportingPeriod.objects.get(id=period_id, organization=request.organization)
        except ReportingPeriod.DoesNotExist:
            return Response(
                {"error": {"code": "not_found", "message": "Reporting period not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file.read()))
            else:
                df = pd.read_excel(io.BytesIO(file.read()))
        except Exception as e:
            return Response(
                {"error": {"code": "parse_error", "message": f"Could not parse file: {e}"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = BulkDataImportService.import_from_dataframe(df, request.organization, period, request.user)
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
        
        from django.db.models import Sum
        scope1 = data_points.filter(metric__code="GHG_SCOPE1", status="approved").aggregate(total=Sum("numeric_value"))["total"] or 0
        scope2 = data_points.filter(metric__code="GHG_SCOPE2", status="approved").aggregate(total=Sum("numeric_value"))["total"] or 0
        scope3 = data_points.filter(metric__code="GHG_SCOPE3", status="approved").aggregate(total=Sum("numeric_value"))["total"] or 0
        
        return Response({
            "total_uploaded_records": total_uploaded,
            "suspicious_rows": suspicious_rows,
            "approved_rows": approved_rows,
            "failed_rows": failed_rows,
            "emissions_by_scope": {
                "scope1": float(scope1),
                "scope2": float(scope2),
                "scope3": float(scope3)
            }
        })

    @action(detail=False, methods=["get"], url_path="upload-history")
    def upload_history(self, request):
        from apps.audit.models import AuditLog
        from apps.audit.serializers import AuditLogSerializer
        
        org_id = self.request.headers.get("X-Organization-Id")
        logs = AuditLog.objects.filter(organization_id=org_id, action="import").order_by("-created_at")
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = AuditLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = AuditLogSerializer(logs, many=True)
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
        years_data = {}
        for item in trend:
            date_val = item["reporting_period__start_date"]
            year = str(date_val.year) if hasattr(date_val, "year") else str(date_val)[:4]
            code = item["metric__code"]
            total = float(item["total"] or 0)
            
            if year not in years_data:
                years_data[year] = {"year": year, "scope1": 0.0, "scope2": 0.0, "scope3": 0.0}
                
            if code == "GHG_SCOPE1":
                years_data[year]["scope1"] = total
            elif code == "GHG_SCOPE2":
                years_data[year]["scope2"] = total
            elif code == "GHG_SCOPE3":
                years_data[year]["scope3"] = total
                
        formatted_trend = sorted(list(years_data.values()), key=lambda x: x["year"])
        
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
            
        from django.db.models import Sum
        scope1 = data_points.filter(metric__code="GHG_SCOPE1").aggregate(total=Sum("numeric_value"))["total"] or 0
        scope2 = data_points.filter(metric__code="GHG_SCOPE2").aggregate(total=Sum("numeric_value"))["total"] or 0
        scope3 = data_points.filter(metric__code="GHG_SCOPE3").aggregate(total=Sum("numeric_value"))["total"] or 0
        
        total_emissions = scope1 + scope2 + scope3
        
        return Response({
            "scope1": float(scope1),
            "scope2": float(scope2),
            "scope3": float(scope3),
            "total_emissions": float(total_emissions),
            "unit": "tCO2e"
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
