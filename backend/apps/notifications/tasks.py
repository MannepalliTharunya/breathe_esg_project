"""
Celery tasks for sending emails and in-app notifications.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue="notifications")
def send_password_reset_email(self, email: str, name: str, reset_url: str):
    try:
        subject = "Reset your ESG Platform password"
        html_message = render_to_string(
            "emails/password_reset.html",
            {"name": name, "reset_url": reset_url, "expiry_hours": 1},
        )
        send_mail(
            subject=subject,
            message=f"Reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("Password reset email sent to %s", email)
    except Exception as exc:
        logger.error("Failed to send password reset email to %s: %s", email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, queue="notifications")
def send_report_ready_notification(self, user_id: str, report_id: str, report_name: str):
    from apps.users.models import User
    from .models import Notification

    try:
        user = User.objects.get(id=user_id)
        Notification.objects.create(
            recipient=user,
            notification_type=Notification.NotificationType.REPORT_READY,
            title="Your report is ready",
            message=f'"{report_name}" has been generated and is ready to download.',
            action_url=f"/reports/{report_id}",
            metadata={"report_id": report_id},
        )
        if user.preferences.report_ready_notifications:
            send_mail(
                subject=f"Report ready: {report_name}",
                message=f'Your ESG report "{report_name}" is ready.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
    except Exception as exc:
        logger.error("Failed to send report notification: %s", exc)
        raise self.retry(exc=exc)


@shared_task(queue="notifications")
def send_data_status_notification(data_point_id: str, new_status: str, reviewer_id: str = None):
    from apps.esg_data.models import ESGDataPoint
    from .models import Notification

    try:
        dp = ESGDataPoint.objects.select_related("submitted_by", "metric").get(id=data_point_id)
        if not dp.submitted_by:
            return

        type_map = {
            "approved": Notification.NotificationType.DATA_APPROVED,
            "rejected": Notification.NotificationType.DATA_REJECTED,
        }
        notif_type = type_map.get(new_status, Notification.NotificationType.DATA_SUBMITTED)

        Notification.objects.create(
            recipient=dp.submitted_by,
            notification_type=notif_type,
            title=f"Data point {new_status}",
            message=f"Your submission for {dp.metric.name} has been {new_status}.",
            action_url=f"/esg/data-points/{data_point_id}",
            metadata={"data_point_id": data_point_id, "metric_code": dp.metric.code},
        )
    except Exception as exc:
        logger.error("Failed to send data status notification: %s", exc)
