"""
Connector registry — each integration type has a dedicated connector class.
"""
import logging
import requests
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    def __init__(self, integration):
        self.integration = integration
        self.config = integration.config

    @abstractmethod
    def sync(self) -> int:
        """Execute sync and return number of records processed."""
        ...

    def _map_to_metric_code(self, source_field: str) -> str | None:
        return self.integration.field_mappings.get(source_field)


class RestApiConnector(BaseConnector):
    def sync(self) -> int:
        url = self.config.get("url")
        headers = self.config.get("headers", {})
        auth_token = self.config.get("auth_token")
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        records = data if isinstance(data, list) else data.get("data", [])
        self._process_records(records)
        return len(records)

    def _process_records(self, records: list):
        from apps.esg_data.models import ESGDataPoint, MetricDefinition
        from apps.esg_data.models import DataStatus
        from django.utils import timezone
        from decimal import Decimal

        for record in records:
            for source_field, value in record.items():
                metric_code = self._map_to_metric_code(source_field)
                if not metric_code:
                    continue
                try:
                    metric = MetricDefinition.objects.get(code=metric_code)
                    ESGDataPoint.objects.update_or_create(
                        organization=self.integration.organization,
                        metric=metric,
                        reporting_period_id=self.config.get("reporting_period_id"),
                        defaults={
                            "numeric_value": Decimal(str(value)),
                            "data_source": self.integration.name,
                            "collection_method": "automated",
                            "status": DataStatus.SUBMITTED,
                            "submitted_at": timezone.now(),
                        },
                    )
                except Exception as e:
                    logger.warning("Failed to process field %s: %s", source_field, e)


class SFTPConnector(BaseConnector):
    def sync(self) -> int:
        # Implement SFTP file download and parsing
        logger.info("SFTP sync not yet implemented for integration %s", self.integration.id)
        return 0


def get_connector(integration) -> BaseConnector:
    connectors = {
        "rest_api": RestApiConnector,
        "sftp": SFTPConnector,
    }
    cls = connectors.get(integration.integration_type)
    if not cls:
        raise ValueError(f"No connector for type: {integration.integration_type}")
    return cls(integration)
