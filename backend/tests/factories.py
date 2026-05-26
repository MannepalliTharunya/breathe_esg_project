"""
Factory Boy factories for all core models.
Use these in tests instead of raw model.objects.create() calls.
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.utils import timezone

fake = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = "users.User"
        django_get_or_create = ("email",)

    email = factory.LazyAttribute(lambda _: fake.unique.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    password = factory.PostGenerationMethodCall("set_password", "TestPassword123!")
    is_active = True
    is_verified = True
    role = "analyst"


class AdminUserFactory(UserFactory):
    role = "org_admin"
    is_staff = True


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = "organizations.Organization"

    name = factory.LazyAttribute(lambda _: fake.company())
    industry = "technology"
    country = "US"
    is_active = True
    subscription_tier = "professional"


class MembershipFactory(DjangoModelFactory):
    class Meta:
        model = "organizations.OrganizationMembership"

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)
    role = "analyst"
    is_active = True


class MetricDefinitionFactory(DjangoModelFactory):
    class Meta:
        model = "esg_data.MetricDefinition"
        django_get_or_create = ("code",)

    category = "E"
    code = factory.LazyAttribute(lambda _: f"TEST_{fake.unique.bothify('??##')}")
    name = factory.LazyAttribute(lambda _: fake.sentence(nb_words=4))
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    unit = "tCO2e"
    data_type = "numeric"
    is_required = False


class ReportingPeriodFactory(DjangoModelFactory):
    class Meta:
        model = "esg_data.ReportingPeriod"

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.LazyAttribute(lambda _: f"FY{fake.year()}")
    period_type = "annual"
    start_date = factory.LazyAttribute(lambda _: fake.date_between(start_date="-2y", end_date="-1y"))
    end_date = factory.LazyAttribute(lambda obj: obj.start_date.replace(year=obj.start_date.year + 1))
    is_locked = False


class ESGDataPointFactory(DjangoModelFactory):
    class Meta:
        model = "esg_data.ESGDataPoint"

    organization = factory.SubFactory(OrganizationFactory)
    metric = factory.SubFactory(MetricDefinitionFactory)
    reporting_period = factory.SubFactory(ReportingPeriodFactory)
    numeric_value = factory.LazyAttribute(lambda _: fake.pydecimal(left_digits=5, right_digits=2, positive=True))
    status = "draft"
    collection_method = "manual"
    confidence_level = 95
