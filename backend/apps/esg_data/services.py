"""
ESG data business logic: workflow transitions, bulk import, aggregation.
"""
import logging
from decimal import Decimal
from typing import Optional
from django.db import transaction
from django.utils import timezone
from .models import ESGDataPoint, DataStatus

logger = logging.getLogger(__name__)


class DataPointWorkflowService:
    """Manages status transitions for ESG data points."""

    VALID_TRANSITIONS = {
        DataStatus.DRAFT: [DataStatus.SUBMITTED],
        DataStatus.SUBMITTED: [DataStatus.UNDER_REVIEW, DataStatus.REJECTED],
        DataStatus.UNDER_REVIEW: [DataStatus.APPROVED, DataStatus.REJECTED],
        DataStatus.REJECTED: [DataStatus.DRAFT],
        DataStatus.APPROVED: [DataStatus.PUBLISHED],
    }

    @classmethod
    def transition(cls, data_point: ESGDataPoint, new_status: str, user, notes: str = "") -> ESGDataPoint:
        current = data_point.status
        allowed = cls.VALID_TRANSITIONS.get(current, [])

        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition from '{current}' to '{new_status}'. "
                f"Allowed: {allowed}"
            )

        with transaction.atomic():
            data_point.status = new_status
            if new_status == DataStatus.SUBMITTED:
                data_point.submitted_by = user
                data_point.submitted_at = timezone.now()
            elif new_status in (DataStatus.APPROVED, DataStatus.REJECTED):
                data_point.reviewed_by = user
                data_point.reviewed_at = timezone.now()
                data_point.review_notes = notes
            data_point.save()

        logger.info(
            "DataPoint %s transitioned %s → %s by user %s",
            data_point.id, current, new_status, user.id,
        )
        return data_point


class ESGAggregationService:
    """Computes aggregated ESG metrics for dashboards and reports."""

    @staticmethod
    def get_category_summary(organization_id, period_id: Optional[str] = None) -> dict:
        """Returns completion % and total values per ESG category."""
        from .models import MetricDefinition, ESGCategory

        qs = ESGDataPoint.objects.filter(organization_id=organization_id)
        if period_id:
            qs = qs.filter(reporting_period_id=period_id)

        summary = {}
        for cat in ESGCategory.values:
            cat_qs = qs.filter(metric__category=cat)
            total = cat_qs.count()
            approved = cat_qs.filter(status=DataStatus.APPROVED).count()
            summary[cat] = {
                "total_metrics": total,
                "approved": approved,
                "completion_pct": round(approved / total * 100, 1) if total else 0,
            }
        return summary

    @staticmethod
    def get_emissions_trend(organization_id, years: int = 5) -> list[dict]:
        """Returns annual GHG emissions (Scope 1+2+3) for trend charts."""
        from django.db.models import Sum
        from .models import MetricDefinition

        scope_codes = ["GHG_SCOPE1", "GHG_SCOPE2", "GHG_SCOPE3"]
        qs = (
            ESGDataPoint.objects.filter(
                organization_id=organization_id,
                metric__code__in=scope_codes,
                status=DataStatus.APPROVED,
            )
            .values("metric__code", "reporting_period__start_date")
            .annotate(total=Sum("numeric_value"))
            .order_by("reporting_period__start_date")
        )
        return list(qs)


class BulkDataImportService:
    """Handles bulk import of ESG data from CSV/Excel uploads."""

    @staticmethod
    @transaction.atomic
    def import_from_dataframe(df, organization, reporting_period, user) -> dict:
        """
        Expects columns: metric_code, value, data_source, notes
        Returns: {created: int, updated: int, errors: list}
        """
        from .models import MetricDefinition

        created, updated, errors = 0, 0, []

        for idx, row in df.iterrows():
            try:
                metric = MetricDefinition.objects.get(code=row["metric_code"])
                obj, is_new = ESGDataPoint.objects.update_or_create(
                    organization=organization,
                    metric=metric,
                    reporting_period=reporting_period,
                    facility=None,
                    defaults={
                        "numeric_value": Decimal(str(row["value"])) if metric.data_type == "numeric" else None,
                        "text_value": str(row.get("value", "")) if metric.data_type == "text" else "",
                        "data_source": row.get("data_source", "bulk_import"),
                        "collection_method": "manual",
                        "notes": row.get("notes", ""),
                        "submitted_by": user,
                        "submitted_at": timezone.now(),
                        "status": DataStatus.SUBMITTED,
                    },
                )
                if is_new:
                    created += 1
                else:
                    updated += 1
            except MetricDefinition.DoesNotExist:
                errors.append({"row": idx + 2, "error": f"Unknown metric code: {row.get('metric_code')}"})
            except Exception as e:
                errors.append({"row": idx + 2, "error": str(e)})

        return {"created": created, "updated": updated, "errors": errors}
