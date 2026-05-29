from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import AuditLog
from .serializers import AuditLogSerializer


@extend_schema(tags=["Audit"])
class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["action", "resource_type", "user_id"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return AuditLog.objects.none()
        org_id = self.request.headers.get("X-Organization-Id")
        qs = AuditLog.objects.all()
        if org_id:
            qs = qs.filter(organization_id=org_id)
        elif not self.request.user.is_superuser:
            org_ids = self.request.user.memberships.filter(is_active=True).values_list("organization_id", flat=True)
            qs = qs.filter(organization_id__in=org_ids)
        return qs
