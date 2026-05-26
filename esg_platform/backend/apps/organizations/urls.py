from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, FacilityViewSet, DepartmentViewSet

router = DefaultRouter()
router.register("", OrganizationViewSet, basename="organization")
router.register("facilities", FacilityViewSet, basename="facility")
router.register("departments", DepartmentViewSet, basename="department")

urlpatterns = router.urls
