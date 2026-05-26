import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, queue="normalization", time_limit=600)
def normalize_batch(self, batch_id: str):
    from apps.ingestion.models import UploadBatch
    from .services import NormalizationService
    try:
        batch = UploadBatch.objects.get(id=batch_id)
        NormalizationService(batch).run()
    except UploadBatch.DoesNotExist:
        logger.error("Batch %s not found for normalization", batch_id)
    except Exception as exc:
        logger.exception("Normalization failed for batch %s", batch_id)
        raise self.retry(exc=exc, countdown=60)
