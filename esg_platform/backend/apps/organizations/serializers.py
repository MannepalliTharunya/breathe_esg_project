from rest_framework import serializers
from .models import Organization, Facility, Department, OrganizationMember


class OrganizationSerializer(serializers.ModelSerializer):
    facility_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ["id", "name", "legal_name", "industry", "country", "reporting_year",
                  "is_active", "facility_count", "user_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_facility_count(self, obj):
        return obj.facilities.filter(is_active=True).count()

    def get_user_count(self, obj):
        return obj.users.filter(is_active=True).count()


class FacilitySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = Facility
        fields = ["id", "organization", "organization_name", "name", "code",
                  "facility_type", "country", "city", "address", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class DepartmentSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.name", read_only=True)

    class Meta:
        model = Department
        fields = ["id", "organization", "facility", "facility_name", "name", "code", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
