import logging
from django.db import transaction
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from apps.core.permissions import IsTenantMember, IsAdminOrAnalyst
from apps.audit.services import AuditService
from .models import NormalizedRecord, ApprovalWorkflow, EmissionCategory
from .serializers import (
    NormalizedRecordSerializer, ApprovalWorkflowSerializer,
    ApprovalActionSerializer, BulkApprovalSerializer, EmissionCategorySerializer,
)
from .filters import NormalizedRecordFilter

logger = logging.getLogger(__name__)


@extend_schema(tags=["Review"])
class NormalizedRecordViewSet(viewsets.ModelViewSet):
    """
    Central analyst review endpoint.
    Supports filtering, search, approve/reject, bulk actions.
    """
    permission_classes = [IsTenantMember]
    serializer_class = NormalizedRecordSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = NormalizedRecordFilter
    ordering_fields = ["activity_date", "created_at", "co2e_kg", "activity_value"]
    ordering = ["-created_at"]
    # Allow POST only for custom actions (approve/reject/flag/bulk-action)
    # Disallow create/delete via the standard router
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return NormalizedRecord.objects.none()
        return (
            NormalizedRecord.objects.filter(organization=self.request.organization)
            .select_related(
                "raw_record", "batch", "facility", "department",
                "emission_category", "created_by",
            )
            .prefetch_related("approvals")
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        from rest_framework.exceptions import MethodNotAllowed
        raise MethodNotAllowed("POST")

    def destroy(self, request, *args, **kwargs):
        from rest_framework.exceptions import MethodNotAllowed
        raise MethodNotAllowed("DELETE")

    @action(detail=True, methods=["post"], url_path="approve",
            permission_classes=[IsTenantMember, IsAdminOrAnalyst])
    def approve(self, request, pk=None):
        record = self.get_object()
        return self._apply_decision(request, record, "approved")

    @action(detail=True, methods=["post"], url_path="reject",
            permission_classes=[IsTenantMember, IsAdminOrAnalyst])
    def reject(self, request, pk=None):
        record = self.get_object()
        return self._apply_decision(request, record, "rejected")

    @action(detail=True, methods=["post"], url_path="flag",
            permission_classes=[IsTenantMember, IsAdminOrAnalyst])
    def flag(self, request, pk=None):
        record = self.get_object()
        return self._apply_decision(request, record, "flagged")

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        record = self.get_object()
        approvals = ApprovalWorkflow.objects.filter(
            normalized_record=record
        ).select_related("created_by").order_by("-created_at")
        return Response(ApprovalWorkflowSerializer(approvals, many=True).data)

    @action(detail=False, methods=["post"], url_path="bulk-action",
            permission_classes=[IsTenantMember, IsAdminOrAnalyst])
    def bulk_action(self, request):
        serializer = BulkApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record_ids = serializer.validated_data["record_ids"]
        decision = serializer.validated_data["decision"]
        comment = serializer.validated_data.get("comment", "")

        records = NormalizedRecord.objects.filter(
            id__in=record_ids,
            organization=request.organization,
            is_locked=False,
        )
        updated = 0
        with transaction.atomic():
            for record in records:
                self._apply_decision_to_record(record, decision, comment, request.user)
                updated += 1

        return Response({"updated": updated, "decision": decision})

    def _apply_decision(self, request, record, decision):
        serializer = ApprovalActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.validated_data.get("comment", "")

        if record.is_locked:
            return Response(
                {"error": {"message": "Record is audit-locked and cannot be modified."}},
                status=status.HTTP_409_CONFLICT,
            )

        with transaction.atomic():
            self._apply_decision_to_record(record, decision, comment, request.user)

        return Response(NormalizedRecordSerializer(record).data)

    @staticmethod
    def _apply_decision_to_record(record, decision, comment, user):
        prev_status = record.status
        status_map = {
            "approved": NormalizedRecord.Status.APPROVED,
            "rejected": NormalizedRecord.Status.REJECTED,
            "flagged": NormalizedRecord.Status.FLAGGED,
        }
        new_status = status_map[decision]

        ApprovalWorkflow.objects.create(
            organization=record.organization,
            normalized_record=record,
            decision=decision,
            comment=comment,
            previous_status=prev_status,
            new_status=new_status,
            created_by=user,
        )

        record.status = new_status
        if decision == "approved":
            record.is_locked = True  # Lock on approval
        record.save(update_fields=["status", "is_locked"])

        # Write audit log
        AuditService.log(
            organization=record.organization,
            user=user,
            action=f"record_{decision}",
            resource_type="NormalizedRecord",
            resource_id=str(record.id),
            before={"status": prev_status},
            after={"status": new_status, "comment": comment},
        )


@extend_schema(tags=["Review"])
class EmissionCategoryListView(generics.ListAPIView):
    serializer_class = EmissionCategorySerializer
    permission_classes = [IsTenantMember]
    queryset = EmissionCategory.objects.all().order_by("scope", "code")
