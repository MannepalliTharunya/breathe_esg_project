from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import NormalizedRecordViewSet, EmissionCategoryListView

router = DefaultRouter()
router.register("records", NormalizedRecordViewSet, basename="normalized-record")

urlpatterns = router.urls + [
    path("categories/", EmissionCategoryListView.as_view(), name="emission-categories"),
]
