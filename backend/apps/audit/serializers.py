from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            "id", "user_id", "user_email", "organization_id",
            "action", "resource_type", "resource_id",
            "ip_address", "request_method", "request_path",
            "changes", "metadata", "status_code", "created_at",
        ]
        read_only_fields = fields
