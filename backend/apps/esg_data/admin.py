from django.contrib import admin
from .models import MetricDefinition, ReportingPeriod, ESGDataPoint, ESGTarget, MaterialityAssessment


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "category", "unit", "data_type", "is_required"]
    list_filter = ["category", "data_type", "is_required"]
    search_fields = ["code", "name"]
    ordering = ["category", "code"]


@admin.register(ReportingPeriod)
class ReportingPeriodAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "period_type", "start_date", "end_date", "is_locked"]
    list_filter = ["period_type", "is_locked"]
    search_fields = ["name", "organization__name"]
    ordering = ["-start_date"]


@admin.register(ESGDataPoint)
class ESGDataPointAdmin(admin.ModelAdmin):
    list_display = [
        "metric", "organization", "reporting_period",
        "numeric_value", "status", "collection_method", "confidence_level", "submitted_at",
    ]
    list_filter = ["status", "collection_method", "metric__category"]
    search_fields = ["metric__code", "metric__name", "organization__name"]
    readonly_fields = ["id", "created_at", "updated_at", "submitted_at", "reviewed_at"]
    ordering = ["-created_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("metric", "organization", "reporting_period")


@admin.register(ESGTarget)
class ESGTargetAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "metric", "baseline_year", "target_year", "is_science_based"]
    list_filter = ["is_science_based", "target_type"]
    search_fields = ["name", "organization__name"]


@admin.register(MaterialityAssessment)
class MaterialityAssessmentAdmin(admin.ModelAdmin):
    list_display = ["topic", "organization", "category", "financial_materiality_score", "impact_materiality_score", "is_material"]
    list_filter = ["category", "is_material"]
    search_fields = ["topic", "organization__name"]
