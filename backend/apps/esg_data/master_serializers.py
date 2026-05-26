from rest_framework import serializers
from .models import (
    ESGCategoryMaster,
    EmissionScope,
    CollectionMethod,
    DataSource,
    DataUpload,
)


class ESGCategoryMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESGCategoryMaster
        fields = ["id", "code", "name", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = fields


class EmissionScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionScope
        fields = ["id", "code", "name", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = fields


class CollectionMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionMethod
        fields = ["id", "code", "name", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = fields


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = [
            "id", "code", "name", "source_type", "description",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = fields


class DataUploadSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source="uploaded_by.email", read_only=True)
    reporting_period_name = serializers.CharField(source="reporting_period.name", read_only=True)

    class Meta:
        model = DataUpload
        fields = [
            "id", "file_name", "source_type", "status",
            "rows_created", "rows_updated", "rows_failed",
            "preview_rows", "error_details",
            "uploaded_by_email", "reporting_period_name",
            "created_at", "updated_at",
        ]
        read_only_fields = fields
