"""
ESG data workflow service unit tests.
"""
import pytest
from apps.esg_data.services import DataPointWorkflowService
from apps.esg_data.models import DataStatus
from tests.factories import UserFactory, ESGDataPointFactory, OrganizationFactory, ReportingPeriodFactory


@pytest.mark.django_db
class TestDataPointWorkflow:
    def test_draft_to_submitted(self, db):
        user = UserFactory()
        org = OrganizationFactory()
        period = ReportingPeriodFactory(organization=org)
        dp = ESGDataPointFactory(organization=org, reporting_period=period, status=DataStatus.DRAFT)

        result = DataPointWorkflowService.transition(dp, DataStatus.SUBMITTED, user)
        assert result.status == DataStatus.SUBMITTED
        assert result.submitted_by == user
        assert result.submitted_at is not None

    def test_submitted_to_approved(self, db):
        user = UserFactory()
        org = OrganizationFactory()
        period = ReportingPeriodFactory(organization=org)
        dp = ESGDataPointFactory(organization=org, reporting_period=period, status=DataStatus.SUBMITTED)

        result = DataPointWorkflowService.transition(dp, DataStatus.APPROVED, user, notes="Looks good")
        assert result.status == DataStatus.APPROVED
        assert result.reviewed_by == user
        assert result.review_notes == "Looks good"

    def test_invalid_transition_raises(self, db):
        user = UserFactory()
        org = OrganizationFactory()
        period = ReportingPeriodFactory(organization=org)
        dp = ESGDataPointFactory(organization=org, reporting_period=period, status=DataStatus.DRAFT)

        with pytest.raises(ValueError, match="Cannot transition"):
            DataPointWorkflowService.transition(dp, DataStatus.APPROVED, user)

    def test_rejected_returns_to_draft(self, db):
        user = UserFactory()
        org = OrganizationFactory()
        period = ReportingPeriodFactory(organization=org)
        dp = ESGDataPointFactory(organization=org, reporting_period=period, status=DataStatus.REJECTED)

        result = DataPointWorkflowService.transition(dp, DataStatus.DRAFT, user)
        assert result.status == DataStatus.DRAFT
