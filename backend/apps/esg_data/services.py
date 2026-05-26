"""
ESG data business logic: workflow transitions, bulk import, aggregation.
"""
import logging
from decimal import Decimal, InvalidOperation
from typing import Optional
import pandas as pd
from django.db import transaction
from django.utils import timezone
from .models import ESGDataPoint, DataStatus, DataUpload, MetricDefinition

logger = logging.getLogger(__name__)

REQUIRED_IMPORT_COLUMNS = {"metric_code", "value"}

# Maps canonical import column names to accepted header variants (after lowercasing).
COLUMN_ALIASES: dict[str, list[str]] = {
    "metric_code": [
        "metric_code", "metric", "metric_name", "metricname", "esg_metric",
        "indicator", "parameter", "metric_id", "kpi", "metric code",
    ],
    "value": [
        "value", "values", "amount", "numeric_value", "reading", "data",
        "quantity", "usage", "consumption", "emissions", "total",
    ],
    "facility_code": [
        "facility_code", "facility", "facility_name", "site", "location",
        "plant", "facility code",
    ],
    "data_source": ["data_source", "source", "data source", "origin"],
    "collection_method": ["collection_method", "method", "collection method"],
    "notes": ["notes", "note", "comments", "comment", "description"],
}


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

    SCOPE_METRIC_CODES = {
        "scope1": ["GHG_SCOPE1", "CARBON_EMISSIONS", "DIESEL_CONSUMPTION", "FUEL_CONSUMPTION", "NATURAL_GAS_USAGE"],
        "scope2": ["GHG_SCOPE2", "ELECTRICITY_CONSUMPTION"],
        "scope3": ["GHG_SCOPE3", "BUSINESS_TRAVEL_EMISSIONS"],
    }

    @staticmethod
    def get_category_summary(organization_id, period_id: Optional[str] = None) -> dict:
        """Returns completion % and total values per ESG category."""
        from .models import ESGCategory

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
        """Returns annual GHG emissions by scope for trend charts."""
        from django.db.models import Sum

        all_codes = []
        for codes in ESGAggregationService.SCOPE_METRIC_CODES.values():
            all_codes.extend(codes)

        qs = (
            ESGDataPoint.objects.filter(
                organization_id=organization_id,
                metric__code__in=all_codes,
                status=DataStatus.APPROVED,
            )
            .values("metric__code", "reporting_period__start_date")
            .annotate(total=Sum("numeric_value"))
            .order_by("reporting_period__start_date")
        )
        return list(qs)

    @staticmethod
    def aggregate_scope_totals(data_points_qs) -> dict:
        from django.db.models import Sum

        totals = {"scope1": 0.0, "scope2": 0.0, "scope3": 0.0}
        for scope, codes in ESGAggregationService.SCOPE_METRIC_CODES.items():
            val = (
                data_points_qs.filter(metric__code__in=codes)
                .aggregate(total=Sum("numeric_value"))["total"]
            )
            totals[scope] = float(val or 0)
        return totals


class BulkDataImportService:
    """Handles bulk import of ESG data from CSV/Excel uploads."""

    @staticmethod
    def parse_file(file) -> pd.DataFrame:
        content = file.read()
        if file.name.lower().endswith(".csv"):
            df = pd.read_csv(pd.io.common.BytesIO(content))
        else:
            df = pd.read_excel(pd.io.common.BytesIO(content))
        df = df.dropna(how="all")
        return df

    @staticmethod
    def _normalize_header(name: str) -> str:
        return str(name).lower().strip().replace(" ", "_")

    @staticmethod
    def normalize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        """Rename file columns to canonical names; return (df, original_column_labels)."""
        original_labels = [str(c) for c in df.columns]
        rename_map: dict[str, str] = {}
        used_canonical: set[str] = set()

        for col in df.columns:
            normalized = BulkDataImportService._normalize_header(col)
            canonical = None
            for target, aliases in COLUMN_ALIASES.items():
                alias_keys = {BulkDataImportService._normalize_header(a) for a in aliases}
                if normalized in alias_keys or normalized == target:
                    canonical = target
                    break
            if canonical and canonical not in used_canonical:
                rename_map[col] = canonical
                used_canonical.add(canonical)

        out = df.rename(columns=rename_map)
        return out, original_labels

    @staticmethod
    def validate_dataframe(df: pd.DataFrame, original_columns: list[str] | None = None) -> list[dict]:
        errors = []
        columns = set(df.columns)
        missing = REQUIRED_IMPORT_COLUMNS - columns
        if missing:
            found = original_columns or list(df.columns)
            found_txt = ", ".join(found[:12]) + ("…" if len(found) > 12 else "")
            errors.append({
                "row": 0,
                "error": (
                    f"Missing required columns: {', '.join(sorted(missing))}. "
                    f"Found in file: {found_txt or '(none)'}. "
                    "Use headers metric_code (or Metric) and value (or Value), or download the template."
                ),
            })
        return errors

    @staticmethod
    def _cell_str(val) -> str:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        s = str(val).strip()
        return "" if s.lower() == "nan" else s

    @staticmethod
    def preview_dataframe(df: pd.DataFrame, limit: int = 10) -> list[dict]:
        rows = []
        for idx, row in df.head(limit).iterrows():
            val = row.get("value")
            if val is not None and isinstance(val, float) and pd.isna(val):
                val = None
            rows.append({
                "row": int(idx) + 2,
                "metric_code": BulkDataImportService._cell_str(row.get("metric_code", "")),
                "value": val if val is not None and not (isinstance(val, float) and pd.isna(val)) else "",
                "facility_code": BulkDataImportService._cell_str(row.get("facility_code", "")),
                "data_source": BulkDataImportService._cell_str(row.get("data_source", "")),
                "notes": BulkDataImportService._cell_str(row.get("notes", "")),
            })
        return rows

    @staticmethod
    @transaction.atomic
    def import_from_dataframe(
        df: pd.DataFrame,
        organization,
        reporting_period,
        user,
        *,
        file_name: str = "upload.csv",
        source_type: str = "manual",
        commit: bool = True,
    ) -> dict:
        """
        Expects columns: metric_code, value, facility_code (optional),
        data_source (optional), notes (optional), collection_method (optional)
        """
        from apps.organizations.models import Facility

        df, original_columns = BulkDataImportService.normalize_columns(df.copy())

        validation_errors = BulkDataImportService.validate_dataframe(df, original_columns)
        if validation_errors:
            return {
                "created": 0,
                "updated": 0,
                "errors": validation_errors,
                "preview": [],
                "detected_columns": original_columns,
            }

        created, updated, errors = 0, 0, []
        preview = BulkDataImportService.preview_dataframe(df)

        if not commit:
            return {"created": 0, "updated": 0, "errors": [], "preview": preview}

        facilities = {
            f.name.lower().replace(" ", "_"): f
            for f in Facility.objects.filter(organization=organization, is_active=True)
        }
        # Also map by slug-like facility name
        for f in Facility.objects.filter(organization=organization, is_active=True):
            key = f.name.lower().replace(" ", "_")
            facilities[key] = f

        for idx, row in df.iterrows():
            try:
                metric_code = str(row["metric_code"]).strip()
                metric = MetricDefinition.objects.get(code=metric_code)

                facility = None
                facility_code = row.get("facility_code")
                if facility_code and not pd.isna(facility_code):
                    fc = str(facility_code).strip().lower().replace(" ", "_")
                    facility = facilities.get(fc)
                    if not facility:
                        errors.append({
                            "row": int(idx) + 2,
                            "error": f"Unknown facility: {facility_code}",
                        })
                        continue

                value = row["value"]
                if pd.isna(value):
                    errors.append({"row": int(idx) + 2, "error": "Value is required"})
                    continue

                defaults = {
                    "numeric_value": None,
                    "text_value": "",
                    "boolean_value": None,
                    "data_source": str(row.get("data_source", source_type) or source_type),
                    "collection_method": str(row.get("collection_method", "excel_upload")),
                    "notes": str(row.get("notes", "") or ""),
                    "submitted_by": user,
                    "submitted_at": timezone.now(),
                    "status": DataStatus.SUBMITTED,
                    "confidence_level": int(row.get("confidence_level", 90) or 90),
                }

                if metric.data_type == "numeric":
                    defaults["numeric_value"] = Decimal(str(value))
                elif metric.data_type == "boolean":
                    defaults["boolean_value"] = str(value).lower() in ("true", "1", "yes")
                else:
                    defaults["text_value"] = str(value)

                obj, is_new = ESGDataPoint.objects.update_or_create(
                    organization=organization,
                    metric=metric,
                    reporting_period=reporting_period,
                    facility=facility,
                    defaults=defaults,
                )
                if is_new:
                    created += 1
                else:
                    updated += 1
            except MetricDefinition.DoesNotExist:
                errors.append({
                    "row": int(idx) + 2,
                    "error": f"Unknown metric code: {row.get('metric_code')}",
                })
            except (InvalidOperation, ValueError) as e:
                errors.append({"row": int(idx) + 2, "error": f"Invalid value: {e}"})
            except Exception as e:
                errors.append({"row": int(idx) + 2, "error": str(e)})

        upload_status = DataUpload.UploadStatus.SUCCESS
        if errors and (created or updated):
            upload_status = DataUpload.UploadStatus.PARTIAL
        elif errors:
            upload_status = DataUpload.UploadStatus.FAILED

        DataUpload.objects.create(
            organization=organization,
            reporting_period=reporting_period,
            uploaded_by=user,
            file_name=file_name,
            source_type=source_type,
            status=upload_status,
            rows_created=created,
            rows_updated=updated,
            rows_failed=len(errors),
            preview_rows=preview[:5],
            error_details=errors[:50],
        )

        return {"created": created, "updated": updated, "errors": errors, "preview": preview}
