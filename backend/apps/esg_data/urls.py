from rest_framework.routers import DefaultRouter
from .views import (
    MetricDefinitionViewSet,
    ReportingPeriodViewSet,
    ESGDataPointViewSet,
    ESGTargetViewSet,
    MaterialityAssessmentViewSet,
    EmissionCategoryViewSet,
)

router = DefaultRouter()
router.register("metrics", MetricDefinitionViewSet, basename="metric")
router.register("periods", ReportingPeriodViewSet, basename="period")
router.register("data-points", ESGDataPointViewSet, basename="datapoint")
router.register("targets", ESGTargetViewSet, basename="target")
router.register("materiality", MaterialityAssessmentViewSet, basename="materiality")
router.register("emission-categories", EmissionCategoryViewSet, basename="emission-category")

urlpatterns = router.urls
