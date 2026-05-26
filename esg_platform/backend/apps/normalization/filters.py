import django_filters
from .models import NormalizedRecord


class NormalizedRecordFilter(django_filters.FilterSet):
    scope = django_filters.MultipleChoiceFilter(choices=NormalizedRecord._meta.get_field("scope").choices)
    source_type = django_filters.MultipleChoiceFilter(
        choices=[("sap", "SAP"), ("utility", "Utility"), ("travel", "Travel")]
    )
    status = django_filters.MultipleChoiceFilter(choices=NormalizedRecord.Status.choices)
    is_suspicious = django_filters.BooleanFilter()
    is_locked = django_filters.BooleanFilter()
    facility = django_filters.UUIDFilter(field_name="facility__id")
    batch = django_filters.UUIDFilter(field_name="batch__id")
    date_from = django_filters.DateFilter(field_name="activity_date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="activity_date", lookup_expr="lte")
    vendor = django_filters.CharFilter(field_name="vendor_name", lookup_expr="icontains")
    search = django_filters.CharFilter(method="search_filter")

    class Meta:
        model = NormalizedRecord
        fields = ["scope", "source_type", "status", "is_suspicious", "is_locked", "facility", "batch"]

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            vendor_name__icontains=value
        ) | queryset.filter(
            cost_center__icontains=value
        ) | queryset.filter(
            document_reference__icontains=value
        )
