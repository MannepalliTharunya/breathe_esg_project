"""
Shared pytest fixtures available to all test modules.
"""
import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, OrganizationFactory, MembershipFactory


@pytest.fixture(scope="session")
def django_db_setup():
    """Use a test database."""
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def admin_user(db):
    from tests.factories import AdminUserFactory
    return AdminUserFactory()


@pytest.fixture
def org(db):
    return OrganizationFactory()


@pytest.fixture
def membership(db, user, org):
    return MembershipFactory(user=user, organization=org, role="esg_manager")


@pytest.fixture
def authenticated_client(api_client, user, org, membership):
    """An API client authenticated as `user` with `org` as the active organization."""
    api_client.force_authenticate(user=user)
    api_client.credentials(HTTP_X_ORGANIZATION_ID=str(org.id))
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user, org, db):
    MembershipFactory(user=admin_user, organization=org, role="admin")
    api_client.force_authenticate(user=admin_user)
    api_client.credentials(HTTP_X_ORGANIZATION_ID=str(org.id))
    return api_client
