"""
Analytics API — powers the analyst dashboard widgets and charts.
All queries are scoped to request.organization.
"""
import logging
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import TruncMonth, TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.core.permissions import IsTenantMember
from apps.normalization.models import NormalizedRecord
from apps.ingestion.models import UploadBatch, RawRecord

logger = logging.getLogger(__name__)


@extend_schema(tags=["Analytics"])
class DashboardSummaryView(APIView):
    """
    Main dashboard widget data.
    Returns counts for all status categories + suspicious rows.
    """
    permission_classes = [IsTenantMember]

    def get(self, request):
        org = request.organization
        qs = NormalizedRecord.objects.filter(organization=org)

        # Status breakdown
        status_counts = qs.values("status").annotate(count=Count("id"))
        status_map = {item["status"]: item["count"] for item in status_counts}

        # Batch stats
        batch_qs = UploadBatch.objects.filter(organization=org)
        batch_counts = batch_qs.values("status").annotate(count=Count("id"))
        batch_map = {item["status"]: item["count"] for item in batch_counts}

        # Total CO2e
        total_co2e = qs.filter(
            status__in=["approved", "locked"]
        ).aggregate(total=Sum("co2e_kg"))["total"] or 0

        # Scope breakdown (approved + locked only)
        scope_co2e = (
            qs.filter(status__in=["approved", "locked"])
            .values("scope")
            .annotate(co2e=Sum("co2e_kg"), count=Count("id"))
        )

        return Response({
            "records": {
                "total": qs.count(),
                "pending": status_map.get("pending", 0),
                "flagged": status_map.get("flagged", 0),
                "approved": status_map.get("approved", 0),
                "rejected": status_map.get("rejected", 0),
                "locked": status_map.get("locked", 0),
                "suspicious": qs.filter(is_suspicious=True).count(),
                "failed": RawRecord.objects.filter(
                    organization=org, status="failed"
                ).count(),
            },
            "batches": {
                "total": batch_qs.count(),
                "pending": batch_map.get("pending", 0),
                "processing": batch_map.get("processing", 0),
                "completed": batch_map.get("completed", 0),
                "failed": batch_map.get("failed", 0),
            },
            "emissions": {
                "total_co2e_kg": float(total_co2e),
                "by_scope": [
                    {
                        "scope": item["scope"],
                        "co2e_kg": float(item["co2e"] or 0),
                        "count": item["count"],
                    }
                    for item in scope_co2e
                ],
            },
        })


@extend_schema(tags=["Analytics"])
class EmissionsBySourceView(APIView):
    """Emissions breakdown by source type (SAP / Utility / Travel)."""
    permission_classes = [IsTenantMember]

    def get(self, request):
        org = request.organization
        data = (
            NormalizedRecord.objects.filter(
                organization=org,
                status__in=["approved", "locked"],
            )
            .values("source_type")
            .annotate(
                co2e_kg=Sum("co2e_kg"),
                record_count=Count("id"),
            )
            .order_by("-co2e_kg")
        )
        return Response(list(data))


@extend_schema(tags=["Analytics"])
class MonthlyTrendView(APIView):
    """Monthly emissions trend for the last 12 months."""
    permission_classes = [IsTenantMember]

    def get(self, request):
        org = request.organization
        scope = request.query_params.get("scope")

        qs = NormalizedRecord.objects.filter(
            organization=org,
            status__in=["approved", "locked"],
        )
        if scope:
            qs = qs.filter(scope=scope)

        data = (
            qs.annotate(month=TruncMonth("activity_date"))
            .values("month", "scope")
            .annotate(co2e_kg=Sum("co2e_kg"), count=Count("id"))
            .order_by("month", "scope")
        )

        return Response([
            {
                "month": item["month"].strftime("%Y-%m"),
                "scope": item["scope"],
                "co2e_kg": float(item["co2e_kg"] or 0),
                "count": item["count"],
            }
            for item in data
        ])


@extend_schema(tags=["Analytics"])
class FacilityEmissionsView(APIView):
    """Emissions breakdown by facility."""
    permission_classes = [IsTenantMember]

    def get(self, request):
        org = request.organization
        data = (
            NormalizedRecord.objects.filter(
                organization=org,
                status__in=["approved", "locked"],
                facility__isnull=False,
            )
            .values("facility__id", "facility__name")
            .annotate(co2e_kg=Sum("co2e_kg"), count=Count("id"))
            .order_by("-co2e_kg")
        )
        return Response([
            {
                "facility_id": str(item["facility__id"]),
                "facility_name": item["facility__name"],
                "co2e_kg": float(item["co2e_kg"] or 0),
                "count": item["count"],
            }
            for item in data
        ])


@extend_schema(tags=["Analytics"])
class IngestionQualityView(APIView):
    """Ingestion quality metrics — failed %, suspicious %, by source."""
    permission_classes = [IsTenantMember]

    def get(self, request):
        org = request.organization
        batches = UploadBatch.objects.filter(organization=org)

        by_source = (
            batches.values("source_type")
            .annotate(
                total_batches=Count("id"),
                total_rows=Sum("total_rows"),
                failed_rows=Sum("failed_rows"),
                suspicious_rows=Sum("suspicious_rows"),
            )
        )

        result = []
        for item in by_source:
            total = item["total_rows"] or 0
            failed = item["failed_rows"] or 0
            suspicious = item["suspicious_rows"] or 0
            result.append({
                "source_type": item["source_type"],
                "total_batches": item["total_batches"],
                "total_rows": total,
                "failed_rows": failed,
                "suspicious_rows": suspicious,
                "failed_pct": round(failed / total * 100, 1) if total else 0,
                "suspicious_pct": round(suspicious / total * 100, 1) if total else 0,
            })

        return Response(result)


@extend_schema(tags=["Analytics"])
class SuspiciousRecordsView(APIView):
    """Returns the most recent suspicious records for analyst attention."""
    permission_classes = [IsTenantMember]

    def get(self, request):
        org = request.organization
        records = (
            NormalizedRecord.objects.filter(
                organization=org,
                is_suspicious=True,
                status__in=["pending", "flagged"],
            )
            .select_related("facility", "batch")
            .order_by("-created_at")[:50]
        )

        from apps.normalization.serializers import NormalizedRecordSerializer
        return Response(NormalizedRecordSerializer(records, many=True).data)
