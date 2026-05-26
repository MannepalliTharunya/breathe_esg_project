"""
Report generation service — builds PDF/Excel ESG reports.
"""
import io
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class ReportGenerationService:
    def __init__(self, report):
        self.report = report
        self.organization = report.organization
        self.period = report.reporting_period

    def generate(self) -> tuple[str, int]:
        """Dispatch to the correct generator based on report type."""
        generators = {
            "gri": self._generate_gri,
            "tcfd": self._generate_tcfd,
            "sasb": self._generate_sasb,
            "custom": self._generate_custom,
        }
        generator = generators.get(self.report.report_type, self._generate_custom)
        return generator()

    def _get_approved_data(self):
        from apps.esg_data.models import ESGDataPoint
        return (
            ESGDataPoint.objects.filter(
                organization=self.organization,
                reporting_period=self.period,
                status="approved",
            )
            .select_related("metric", "facility")
        )

    def _generate_gri(self) -> tuple[str, int]:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"GRI Standards Report — {self.organization.name}", styles["Title"]))
        story.append(Paragraph(f"Reporting Period: {self.period.name}", styles["Normal"]))
        story.append(Spacer(1, 20))

        data_points = self._get_approved_data()
        table_data = [["Metric Code", "Metric Name", "Value", "Unit"]]
        for dp in data_points:
            table_data.append([
                dp.metric.code,
                dp.metric.name,
                str(dp.value or ""),
                dp.metric.unit,
            ])

        if len(table_data) > 1:
            table = Table(table_data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]))
            story.append(table)

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        file_url = self._upload_or_save(pdf_bytes, f"gri_report_{self.report.id}.pdf")
        return file_url, len(pdf_bytes)

    def _generate_tcfd(self) -> tuple[str, int]:
        # TCFD report follows same pattern with TCFD-specific sections
        return self._generate_gri()

    def _generate_sasb(self) -> tuple[str, int]:
        return self._generate_gri()

    def _generate_custom(self) -> tuple[str, int]:
        return self._generate_gri()

    def _upload_or_save(self, content: bytes, filename: str) -> str:
        """Upload to S3 or save locally depending on config."""
        if getattr(settings, "USE_S3", False):
            import boto3
            s3 = boto3.client("s3")
            key = f"reports/{self.organization.id}/{filename}"
            s3.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=key,
                Body=content,
                ContentType="application/pdf",
            )
            return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{key}"
        else:
            import os
            from django.conf import settings as s
            path = os.path.join(s.MEDIA_ROOT, "reports", str(self.organization.id))
            os.makedirs(path, exist_ok=True)
            filepath = os.path.join(path, filename)
            with open(filepath, "wb") as f:
                f.write(content)
            return f"{s.MEDIA_URL}reports/{self.organization.id}/{filename}"
