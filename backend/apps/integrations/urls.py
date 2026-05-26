from rest_framework.routers import DefaultRouter
from .views import DataIntegrationViewSet

router = DefaultRouter()
router.register("", DataIntegrationViewSet, basename="integration")

urlpatterns = router.urls
