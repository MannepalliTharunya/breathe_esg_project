import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue="default")
def run_integration_sync(self, integration_id: str):
    from .models import DataIntegration

    try:
        integration = DataIntegration.objects.get(id=integration_id)
        integration.sync_status = DataIntegration.SyncStatus.ACTIVE
        integration.save(update_fields=["sync_status"])

        # Dispatch to the correct connector
        from .connectors import get_connector
        connector = get_connector(integration)
        records_synced = connector.sync()

        integration.last_sync_at = timezone.now()
        integration.last_sync_records = records_synced
        integration.last_error = ""
        integration.save(update_fields=["last_sync_at", "last_sync_records", "last_error"])
        logger.info("Integration %s synced %d records", integration_id, records_synced)

    except Exception as exc:
        logger.exception("Integration sync failed: %s", integration_id)
        try:
            integration = DataIntegration.objects.get(id=integration_id)
            integration.sync_status = DataIntegration.SyncStatus.ERROR
            integration.last_error = str(exc)
            integration.save(update_fields=["sync_status", "last_error"])
        except Exception:
            pass
        raise self.retry(exc=exc)
