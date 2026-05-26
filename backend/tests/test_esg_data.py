"""
ESG data endpoint tests.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from tests.factories import (
    UserFactory, OrganizationFactory, MembershipFactory,
    MetricDefinitionFactory, ReportingPeriodFactory, ESGDataPointFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def org_with_member(db):
    org = OrganizationFactory()
    user = UserFactory()
    membership = MembershipFactory(user=user, organization=org, role="esg_manager")
    return org, user, membership


@pytest.fixture
def authenticated_client(api_client, org_with_member):
    org, user, _ = org_with_member
    api_client.force_authenticate(user=user)
    api_client.credentials(HTTP_X_ORGANIZATION_ID=str(org.id))
    return api_client, org, user


@pytest.mark.django_db
class TestESGDataPoints:
    def test_list_data_points(self, authenticated_client):
        client, org, user = authenticated_client
        period = ReportingPeriodFactory(organization=org)
        metric = MetricDefinitionFactory()
        ESGDataPointFactory(organization=org, metric=metric, reporting_period=period)

        url = reverse("datapoint-list")
        response = client.get(url)
        assert response.status_code == 200
        assert response.data["pagination"]["count"] >= 1

    def test_create_data_point(self, authenticated_client):
        client, org, user = authenticated_client
        period = ReportingPeriodFactory(organization=org)
        metric = MetricDefinitionFactory(data_type="numeric")

        url = reverse("datapoint-list")
        payload = {
            "metric": str(metric.id),
            "reporting_period": str(period.id),
            "numeric_value": "1234.56",
            "collection_method": "manual",
            "confidence_level": 90,
        }
        response = client.post(url, payload, format="json")
        assert response.status_code == 201
        assert response.data["status"] == "draft"

    def test_status_transition_draft_to_submitted(self, authenticated_client):
        client, org, user = authenticated_client
        period = ReportingPeriodFactory(organization=org)
        dp = ESGDataPointFactory(organization=org, reporting_period=period, status="draft")

        url = reverse("datapoint-update-status", kwargs={"pk": str(dp.id)})
        response = client.post(url, {"status": "submitted"}, format="json")
        assert response.status_code == 200
        assert response.data["status"] == "submitted"

    def test_invalid_status_transition(self, authenticated_client):
        client, org, user = authenticated_client
        period = ReportingPeriodFactory(organization=org)
        dp = ESGDataPointFactory(organization=org, reporting_period=period, status="draft")

        url = reverse("datapoint-update-status", kwargs={"pk": str(dp.id)})
        response = client.post(url, {"status": "approved"}, format="json")
        assert response.status_code == 400

    def test_filter_by_category(self, authenticated_client):
        client, org, user = authenticated_client
        period = ReportingPeriodFactory(organization=org)
        env_metric = MetricDefinitionFactory(category="E")
        soc_metric = MetricDefinitionFactory(category="S")
        ESGDataPointFactory(organization=org, metric=env_metric, reporting_period=period)
        ESGDataPointFactory(organization=org, metric=soc_metric, reporting_period=period)

        url = reverse("datapoint-list")
        response = client.get(url, {"category": "E"})
        assert response.status_code == 200
        for dp in response.data["results"]:
            assert dp["metric"]["category"] == "E"

    def test_unauthenticated_access_denied(self, api_client):
        url = reverse("datapoint-list")
        response = api_client.get(url)
        assert response.status_code == 401
