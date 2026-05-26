from rest_framework import serializers
from .models import UploadBatch, RawRecord


class UploadBatchSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    facility_name = serializers.CharField(source="facility.name", read_only=True)
    success_rate = serializers.ReadOnlyField()

    class Meta:
        model = UploadBatch
        fields = [
            "id", "source_type", "original_filename", "file_size_bytes",
            "status", "total_rows", "processed_rows", "failed_rows", "suspicious_rows",
            "facility", "facility_name", "notes", "error_summary", "success_rate",
            "processing_started_at", "processing_completed_at",
            "created_by", "created_by_name", "created_at",
        ]
        read_only_fields = [
            "id", "status", "total_rows", "processed_rows", "failed_rows",
            "suspicious_rows", "error_summary", "success_rate",
            "processing_started_at", "processing_completed_at", "created_by", "created_at",
        ]


class UploadBatchCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = UploadBatch
        fields = ["source_type", "file", "facility", "notes"]

    def validate_file(self, value):
        name = value.name.lower()
        if not (name.endswith(".csv") or name.endswith(".xlsx") or name.endswith(".xls")):
            raise serializers.ValidationError("Only CSV and Excel files are accepted.")
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 100 MB.")
        return value


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = [
            "id", "batch", "row_number", "raw_data", "source_type",
            "status", "parse_errors", "created_at",
        ]
        read_only_fields = fields
