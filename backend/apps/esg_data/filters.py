import django_filters
from .models import ESGDataPoint


class ESGDataPointFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="metric__category")
    metric_code = django_filters.CharFilter(field_name="metric__code")
    period = django_filters.UUIDFilter(field_name="reporting_period__id")
    facility = django_filters.UUIDFilter(field_name="facility__id")
    status = django_filters.MultipleChoiceFilter(choices=ESGDataPoint._meta.get_field("status").choices)
    submitted_after = django_filters.DateTimeFilter(field_name="submitted_at", lookup_expr="gte")
    submitted_before = django_filters.DateTimeFilter(field_name="submitted_at", lookup_expr="lte")

    class Meta:
        model = ESGDataPoint
        fields = ["category", "metric_code", "period", "facility", "status"]
