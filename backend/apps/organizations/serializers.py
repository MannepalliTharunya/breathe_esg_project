from rest_framework import serializers
from apps.users.serializers import UserListSerializer
from .models import Organization, Facility, OrganizationMembership, Department


class OrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id", "name", "legal_name", "industry", "country",
            "website", "logo", "description", "employee_count",
            "annual_revenue", "fiscal_year_end", "reporting_currency",
            "is_active", "subscription_tier", "member_count", "created_at",
        ]
        read_only_fields = ["id", "created_at", "member_count"]

    def get_member_count(self, obj) -> int:
        return obj.memberships.filter(is_active=True).count()


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class MembershipSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ["id", "user", "user_id", "role", "is_active", "joined_at"]
        read_only_fields = ["id", "joined_at"]

    def create(self, validated_data):
        validated_data["organization_id"] = self.context["org_pk"]
        validated_data["invited_by"] = self.context["request"].user
        return super().create(validated_data)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["organization_id"] = self.context.get("org_pk") or validated_data.get("organization_id")
        return super().create(validated_data)
