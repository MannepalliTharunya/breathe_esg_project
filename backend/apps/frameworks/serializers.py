from rest_framework import serializers
from .models import Framework, FrameworkRequirement, OrganizationFramework


class FrameworkSerializer(serializers.ModelSerializer):
    requirement_count = serializers.SerializerMethodField()

    class Meta:
        model = Framework
        fields = ["id", "code", "name", "version", "description", "issuing_body", "website", "is_active", "requirement_count"]

    def get_requirement_count(self, obj) -> int:
        return obj.requirements.count()


class FrameworkRequirementSerializer(serializers.ModelSerializer):
    framework_code = serializers.CharField(source="framework.code", read_only=True)

    class Meta:
        model = FrameworkRequirement
        fields = "__all__"


class OrganizationFrameworkSerializer(serializers.ModelSerializer):
    framework = FrameworkSerializer(read_only=True)
    framework_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrganizationFramework
        fields = ["id", "framework", "framework_id", "adopted_at", "is_primary", "compliance_score", "last_assessed_at"]
