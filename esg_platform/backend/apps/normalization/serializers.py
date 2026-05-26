from rest_framework import serializers
from .models import NormalizedRecord, ApprovalWorkflow, EmissionCategory


class EmissionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionCategory
        fields = ["id", "scope", "code", "name", "description", "ghg_protocol_category"]


class NormalizedRecordSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    emission_category_name = serializers.CharField(source="emission_category.name", read_only=True)
    batch_filename = serializers.CharField(source="batch.original_filename", read_only=True)
    raw_data = serializers.JSONField(source="raw_record.raw_data", read_only=True)
    row_number = serializers.IntegerField(source="raw_record.row_number", read_only=True)

    class Meta:
        model = NormalizedRecord
        fields = [
            "id", "batch", "batch_filename", "row_number", "raw_data",
            "scope", "source_type", "emission_category", "emission_category_name",
            "activity_value", "activity_unit", "activity_date",
            "activity_period_start", "activity_period_end",
            "emission_factor", "emission_factor_source", "co2e_kg",
            "vendor_name", "cost_center", "document_reference",
            "original_value", "original_unit",
            "facility", "facility_name", "department", "department_name",
            "status", "is_suspicious", "is_locked",
            "suspicious_reasons", "validation_errors", "transformation_log",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "batch", "row_number", "raw_data", "scope", "source_type",
            "activity_value", "activity_unit", "activity_date",
            "original_value", "original_unit", "is_locked",
            "suspicious_reasons", "validation_errors", "transformation_log",
            "created_at", "updated_at",
        ]


class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    decided_by = serializers.CharField(source="created_by.get_full_name", read_only=True)
    decided_by_email = serializers.CharField(source="created_by.email", read_only=True)

    class Meta:
        model = ApprovalWorkflow
        fields = [
            "id", "normalized_record", "decision", "comment",
            "previous_status", "new_status",
            "decided_by", "decided_by_email", "created_at",
        ]
        read_only_fields = ["id", "previous_status", "new_status", "decided_by", "decided_by_email", "created_at"]


class ApprovalActionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=ApprovalWorkflow.Decision.choices)
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class BulkApprovalSerializer(serializers.Serializer):
    record_ids = serializers.ListField(child=serializers.UUIDField(), min_length=1, max_length=500)
    decision = serializers.ChoiceField(choices=ApprovalWorkflow.Decision.choices)
    comment = serializers.CharField(required=False, allow_blank=True, default="")
