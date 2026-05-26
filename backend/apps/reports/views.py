from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.permissions import IsOrganizationMember
from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer
from .tasks import generate_report_task


class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOrganizationMember]

    def get_queryset(self):
        org_id = self.request.headers.get("X-Organization-Id")
        return Report.objects.filter(organization_id=org_id).select_related("created_by", "reporting_period")

    def get_serializer_class(self):
        if self.action == "create":
            return ReportCreateSerializer
        return ReportSerializer

    def perform_create(self, serializer):
        report = serializer.save(
            organization=self.request.organization,
            created_by=self.request.user,
        )
        # Kick off async generation
        generate_report_task.delay(str(report.id))

    @action(detail=True, methods=["post"], url_path="regenerate")
    def regenerate(self, request, pk=None):
        report = self.get_object()
        if report.status == Report.ReportStatus.GENERATING:
            return Response(
                {"error": {"code": "conflict", "message": "Report is already being generated."}},
                status=status.HTTP_409_CONFLICT,
            )
        report.status = Report.ReportStatus.DRAFT
        report.error_message = ""
        report.save(update_fields=["status", "error_message"])
        generate_report_task.delay(str(report.id))
        return Response({"detail": "Report regeneration started."}, status=status.HTTP_202_ACCEPTED)
