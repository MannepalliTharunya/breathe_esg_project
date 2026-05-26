from rest_framework import serializers
from .models import (
    EmissionCategory,
    MetricDefinition,
    ReportingPeriod,
    ESGDataPoint,
    ESGTarget,
    MaterialityAssessment,
    DataStatus,
    CollectionMethod,
    DataSource,
)


class EmissionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionCategory
        fields = "__all__"


class MetricDefinitionSerializer(serializers.ModelSerializer):
    emission_category_detail = EmissionCategorySerializer(source="emission_category", read_only=True)

    class Meta:
        model = MetricDefinition
        fields = [
            "id", "category", "code", "name", "description", "unit",
            "data_type", "is_required", "calculation_guidance",
            "framework_mappings", "tags", "emission_category", "emission_category_detail",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if attrs.get("start_date") and attrs.get("end_date"):
            if attrs["start_date"] >= attrs["end_date"]:
                raise serializers.ValidationError("start_date must be before end_date.")
        return attrs


class ESGDataPointWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESGDataPoint
        fields = [
            "metric", "reporting_period", "facility",
            "numeric_value", "text_value", "boolean_value",
            "data_source", "collection_method", "confidence_level",
            "notes", "attachments",
        ]

    def validate(self, attrs):
        metric = attrs.get("metric")
        if metric:
            if metric.data_type == "numeric" and attrs.get("numeric_value") is None:
                raise serializers.ValidationError({"numeric_value": "Required for numeric metrics."})
            if metric.data_type == "boolean" and attrs.get("boolean_value") is None:
                raise serializers.ValidationError({"boolean_value": "Required for boolean metrics."})
        return attrs

    def validate_collection_method(self, value):
        if CollectionMethod.objects.filter(code=value, is_active=True).exists():
            return value
        legacy = {"manual", "automated", "estimated", "calculated", "manual_entry"}
        if value in legacy:
            return value
        raise serializers.ValidationError(f"Unknown collection method: {value}")

    def validate_data_source(self, value):
        if not value:
            return value
        if DataSource.objects.filter(code=value, is_active=True).exists():
            return value
        if DataSource.objects.filter(name__iexact=value, is_active=True).exists():
            return value
        return value

    def create(self, validated_data):
        from django.utils import timezone

        validated_data["organization"] = self.context["organization"]
        validated_data["submitted_by"] = self.context["request"].user
        validated_data.setdefault("status", DataStatus.SUBMITTED)
        validated_data.setdefault("submitted_at", timezone.now())
        return super().create(validated_data)


class ESGDataPointReadSerializer(serializers.ModelSerializer):
    metric = MetricDefinitionSerializer(read_only=True)
    submitted_by_name = serializers.CharField(source="submitted_by.full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True)
    value = serializers.ReadOnlyField()

    class Meta:
        model = ESGDataPoint
        fields = [
            "id", "metric", "reporting_period", "facility",
            "value", "numeric_value", "text_value", "boolean_value",
            "status", "data_source", "collection_method", "confidence_level",
            "notes", "attachments",
            "submitted_by_name", "submitted_at",
            "reviewed_by_name", "reviewed_at", "review_notes",
            "created_at", "updated_at",
        ]


class DataPointStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=DataStatus.choices)
    review_notes = serializers.CharField(required=False, allow_blank=True)


class ESGTargetSerializer(serializers.ModelSerializer):
    metric_name = serializers.CharField(source="metric.name", read_only=True)
    metric_unit = serializers.CharField(source="metric.unit", read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = ESGTarget
        fields = [
            "id", "metric", "metric_name", "metric_unit",
            "name", "description", "target_type",
            "baseline_year", "baseline_value",
            "target_year", "target_value",
            "is_science_based", "framework_alignment",
            "progress_percentage", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_progress_percentage(self, obj) -> float | None:
        """Calculate progress toward target based on latest approved data."""
        try:
            latest = (
                ESGDataPoint.objects.filter(
                    organization=obj.organization,
                    metric=obj.metric,
                    status="approved",
                )
                .order_by("-reporting_period__end_date")
                .first()
            )
            if not latest or latest.numeric_value is None:
                return None
            baseline = float(obj.baseline_value)
            target = float(obj.target_value)
            current = float(latest.numeric_value)
            if baseline == target:
                return 100.0
            progress = (baseline - current) / (baseline - target) * 100
            return round(min(max(progress, 0), 100), 2)
        except Exception:
            return None


class MaterialityAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialityAssessment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
