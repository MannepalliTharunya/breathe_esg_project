"""
Normalization service — processes all pending RawRecords in a batch
and creates NormalizedRecords.
"""
import logging
from django.db import transaction
from apps.ingestion.models import RawRecord, UploadBatch
from .models import NormalizedRecord
from .transformers import get_transformer
from .engine import DuplicateDetector

logger = logging.getLogger(__name__)
BATCH_SIZE = 200


class NormalizationService:
    def __init__(self, batch: UploadBatch):
        self.batch = batch

    def run(self):
        batch = self.batch
        pending = RawRecord.objects.filter(
            batch=batch,
            status=RawRecord.Status.PENDING,
        ).select_related("batch__organization")

        transformer = get_transformer(batch.source_type)
        to_create = []
        processed = 0
        suspicious = 0

        for raw in pending.iterator(chunk_size=500):
            try:
                fields = transformer.transform(raw.raw_data, batch)
            except Exception as e:
                logger.warning("Transform failed row %s: %s", raw.row_number, e)
                raw.status = RawRecord.Status.FAILED
                raw.parse_errors = [str(e)]
                raw.save(update_fields=["status", "parse_errors"])
                continue

            # Duplicate check
            is_dup = DuplicateDetector.is_duplicate(
                organization_id=batch.organization_id,
                source_type=fields["source_type"],
                activity_date=fields["activity_date"],
                activity_value=fields["activity_value"],
                activity_unit=fields["activity_unit"],
                exclude_batch_id=batch.id,
            )
            if is_dup:
                fields["suspicious_reasons"] = fields.get("suspicious_reasons", []) + ["Potential duplicate record"]
                fields["is_suspicious"] = True

            if fields.get("is_suspicious"):
                suspicious += 1

            status = (
                NormalizedRecord.Status.FLAGGED
                if fields.get("is_suspicious") or fields.get("validation_errors")
                else NormalizedRecord.Status.PENDING
            )

            to_create.append(NormalizedRecord(
                organization=batch.organization,
                batch=batch,
                raw_record=raw,
                facility=batch.facility,
                status=status,
                created_by=batch.created_by,
                **{k: v for k, v in fields.items()},
            ))

            raw.status = RawRecord.Status.NORMALIZED
            raw.save(update_fields=["status"])
            processed += 1

            if len(to_create) >= BATCH_SIZE:
                NormalizedRecord.objects.bulk_create(to_create, batch_size=BATCH_SIZE)
                to_create = []

        if to_create:
            NormalizedRecord.objects.bulk_create(to_create, batch_size=BATCH_SIZE)

        # Update batch counters
        batch.processed_rows = processed
        batch.suspicious_rows = suspicious
        batch.save(update_fields=["processed_rows", "suspicious_rows"])
        logger.info("Batch %s normalized: %d records, %d suspicious", batch.id, processed, suspicious)
