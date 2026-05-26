"""
Celery tasks for async report generation.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, queue="reports", time_limit=600)
def generate_report_task(self, report_id: str):
    from .models import Report
    from .services import ReportGenerationService

    try:
        report = Report.objects.get(id=report_id)
        report.status = Report.ReportStatus.GENERATING
        report.save(update_fields=["status"])

        service = ReportGenerationService(report)
        file_url, file_size = service.generate()

        report.status = Report.ReportStatus.READY
        report.file_url = file_url
        report.file_size_bytes = file_size
        report.generated_at = timezone.now()
        report.save(update_fields=["status", "file_url", "file_size_bytes", "generated_at"])

        from apps.notifications.tasks import send_report_ready_notification
        send_report_ready_notification.delay(
            str(report.created_by_id), str(report.id), report.name
        )
        logger.info("Report %s generated successfully", report_id)

    except Exception as exc:
        logger.exception("Report generation failed for %s", report_id)
        try:
            report = Report.objects.get(id=report_id)
            report.status = Report.ReportStatus.FAILED
            report.error_message = str(exc)
            report.save(update_fields=["status", "error_message"])
        except Exception:
            pass
        raise self.retry(exc=exc)
