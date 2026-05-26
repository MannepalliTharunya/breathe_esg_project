import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue="ingestion", time_limit=600)
def process_upload_batch(self, batch_id: str):
    """Celery task: parse and store raw records for an uploaded batch."""
    from .models import UploadBatch
    from .services import IngestionService

    try:
        batch = UploadBatch.objects.get(id=batch_id)
        IngestionService(batch).run()
    except UploadBatch.DoesNotExist:
        logger.error("Batch %s not found", batch_id)
    except Exception as exc:
        logger.exception("Batch %s task failed", batch_id)
        raise self.retry(exc=exc, countdown=30)
