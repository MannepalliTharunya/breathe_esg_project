from rest_framework.routers import DefaultRouter
from .views import (
    MetricDefinitionViewSet,
    ReportingPeriodViewSet,
    ESGDataPointViewSet,
    ESGTargetViewSet,
    MaterialityAssessmentViewSet,
    EmissionCategoryViewSet,
)
from .master_views import (
    ESGCategoryMasterViewSet,
    EmissionScopeViewSet,
    CollectionMethodViewSet,
    DataSourceViewSet,
    DataUploadViewSet,
)

router = DefaultRouter()
router.register("metrics", MetricDefinitionViewSet, basename="metric")
router.register("periods", ReportingPeriodViewSet, basename="period")
router.register("data-points", ESGDataPointViewSet, basename="datapoint")
router.register("targets", ESGTargetViewSet, basename="target")
router.register("materiality", MaterialityAssessmentViewSet, basename="materiality")
router.register("emission-categories", EmissionCategoryViewSet, basename="emission-category")
router.register("categories", ESGCategoryMasterViewSet, basename="esg-category")
router.register("emission-scopes", EmissionScopeViewSet, basename="emission-scope")
router.register("collection-methods", CollectionMethodViewSet, basename="collection-method")
router.register("data-sources", DataSourceViewSet, basename="data-source")
router.register("uploads", DataUploadViewSet, basename="data-upload")

urlpatterns = router.urls
