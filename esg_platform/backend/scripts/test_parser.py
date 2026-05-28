import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_local")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django; django.setup()

from apps.ingestion.models import UploadBatch
from apps.ingestion.parsers.registry import get_parser
from apps.ingestion.services import IngestionService

# Test SAP Excel batch
sap = UploadBatch.objects.filter(original_filename__icontains="SAP").first()
if sap:
    print(f"SAP batch: {sap.original_filename} | source={sap.source_type}")
    sap.file.seek(0)
    try:
        parser = get_parser("sap", sap.file)
        rows = list(parser.parse())
        print(f"  Parser OK: {len(rows)} rows")
        if rows:
            r = rows[0]
            print(f"  plant_code={r.get('plant_code')!r}")
            print(f"  quantity={r.get('quantity')!r}")
            print(f"  unit={r.get('unit')!r}")
            print(f"  posting_date={r.get('posting_date')!r}")
            print(f"  fuel_type={r.get('fuel_type')!r}")
            # Validate first row
            errs = parser.validate_row(r)
            print(f"  validation errors: {errs}")
    except Exception as e:
        print(f"  Error: {e}")

    # Now reprocess it
    print("\nReprocessing SAP batch...")
    sap.status = "pending"
    sap.error_summary = ""
    sap.total_rows = 0
    sap.failed_rows = 0
    sap.save()
    IngestionService(sap).run()
    sap.refresh_from_db()
    print(f"  After reprocess: status={sap.status} total={sap.total_rows} failed={sap.failed_rows} suspicious={sap.suspicious_rows}")
    if sap.error_summary:
        print(f"  Error: {sap.error_summary}")
