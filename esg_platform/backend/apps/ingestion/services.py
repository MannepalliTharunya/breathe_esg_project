"""
Ingestion service — orchestrates the full upload → parse → store pipeline.
Called by the Celery task after a file is uploaded.
"""
import logging
from django.utils import timezone
from django.db import transaction
from .models import UploadBatch, RawRecord
from .parsers.registry import get_parser
from .parsers.base import ParseError

logger = logging.getLogger(__name__)

BATCH_SIZE = 500  # DB insert batch size


class IngestionService:
    def __init__(self, batch: UploadBatch):
        self.batch = batch

    def run(self):
        """
        Full ingestion pipeline:
        1. Parse CSV → raw rows
        2. Validate each row
        3. Bulk-insert RawRecords
        4. Trigger normalization task
        """
        batch = self.batch
        batch.status = UploadBatch.Status.PROCESSING
        batch.processing_started_at = timezone.now()
        batch.save(update_fields=["status", "processing_started_at"])

        try:
            self._process()
        except ParseError as e:
            batch.status = UploadBatch.Status.FAILED
            batch.error_summary = str(e)
            batch.save(update_fields=["status", "error_summary"])
            logger.error("Batch %s parse failed: %s", batch.id, e)
            return
        except Exception as e:
            batch.status = UploadBatch.Status.FAILED
            batch.error_summary = f"Unexpected error: {e}"
            batch.save(update_fields=["status", "error_summary"])
            logger.exception("Batch %s failed unexpectedly", batch.id)
            return

        # Trigger normalization
        from apps.normalization.tasks import normalize_batch
        normalize_batch.delay(str(batch.id))

    def _process(self):
        batch = self.batch
        batch.file.seek(0)
        parser = get_parser(batch.source_type, batch.file)

        raw_records_to_create = []
        total = 0
        failed = 0

        for row in parser.parse():
            total += 1
            row_num = row.pop("_row_number")
            raw_data = row.pop("_raw")
            errors = parser.validate_row(row)

            status = RawRecord.Status.FAILED if errors else RawRecord.Status.PENDING

            raw_records_to_create.append(RawRecord(
                organization=batch.organization,
                batch=batch,
                row_number=row_num,
                raw_data=raw_data,
                source_type=batch.source_type,
                status=status,
                parse_errors=errors,
                created_by=batch.created_by,
            ))

            if errors:
                failed += 1

            # Flush in batches to avoid memory issues on large files
            if len(raw_records_to_create) >= BATCH_SIZE:
                RawRecord.objects.bulk_create(raw_records_to_create, batch_size=BATCH_SIZE)
                raw_records_to_create = []

        if raw_records_to_create:
            RawRecord.objects.bulk_create(raw_records_to_create, batch_size=BATCH_SIZE)

        batch.total_rows = total
        batch.failed_rows = failed
        batch.status = UploadBatch.Status.PARTIAL if failed else UploadBatch.Status.COMPLETED
        batch.processing_completed_at = timezone.now()
        batch.save(update_fields=[
            "total_rows", "failed_rows", "status", "processing_completed_at"
        ])
        logger.info("Batch %s: %d rows, %d failed", batch.id, total, failed)
