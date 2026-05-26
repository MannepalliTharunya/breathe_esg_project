from rest_framework import serializers
from apps.core.utils import mask_sensitive_value
from .models import DataIntegration


class DataIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataIntegration
        fields = [
            "id", "name", "integration_type", "sync_status",
            "field_mappings", "sync_frequency",
            "last_sync_at", "last_sync_records", "last_error", "created_at",
        ]
        read_only_fields = ["id", "sync_status", "last_sync_at", "last_sync_records", "last_error", "created_at"]


class DataIntegrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataIntegration
        fields = ["name", "integration_type", "config", "field_mappings", "sync_frequency"]

    def validate_config(self, value):
        # In production, encrypt sensitive fields before storing
        return value
