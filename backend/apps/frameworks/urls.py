from rest_framework.routers import DefaultRouter
from .views import FrameworkViewSet, FrameworkRequirementViewSet, OrganizationFrameworkViewSet

router = DefaultRouter()
router.register("", FrameworkViewSet, basename="framework")
router.register("requirements", FrameworkRequirementViewSet, basename="framework-requirement")
router.register("organization", OrganizationFrameworkViewSet, basename="org-framework")

urlpatterns = router.urls
