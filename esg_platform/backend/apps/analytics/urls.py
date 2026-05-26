from django.urls import path
from .views import (
    DashboardSummaryView,
    EmissionsBySourceView,
    MonthlyTrendView,
    FacilityEmissionsView,
    IngestionQualityView,
    SuspiciousRecordsView,
)

urlpatterns = [
    path("dashboard/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("emissions/by-source/", EmissionsBySourceView.as_view(), name="emissions-by-source"),
    path("emissions/monthly/", MonthlyTrendView.as_view(), name="monthly-trend"),
    path("emissions/by-facility/", FacilityEmissionsView.as_view(), name="facility-emissions"),
    path("ingestion-quality/", IngestionQualityView.as_view(), name="ingestion-quality"),
    path("suspicious/", SuspiciousRecordsView.as_view(), name="suspicious-records"),
]
