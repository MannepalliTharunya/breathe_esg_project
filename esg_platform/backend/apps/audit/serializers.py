from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id", "organization", "user", "user_email", "user_name",
            "action", "resource_type", "resource_id",
            "before_value", "after_value",
            "ip_address", "source_system", "created_at",
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else "System"
