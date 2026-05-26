from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id", "name", "report_type", "status",
            "file_url", "file_size_bytes", "generation_config",
            "error_message", "generated_at", "published_at",
            "created_by_name", "created_at",
        ]
        read_only_fields = [
            "id", "status", "file_url", "file_size_bytes",
            "error_message", "generated_at", "published_at", "created_at",
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["name", "report_type", "reporting_period", "generation_config"]
