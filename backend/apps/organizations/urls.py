from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, FacilityViewSet, MembershipViewSet, DepartmentViewSet

router = DefaultRouter()
router.register("", OrganizationViewSet, basename="organization")
router.register("(?P<org_pk>[^/.]+)/facilities", FacilityViewSet, basename="facility")
router.register("(?P<org_pk>[^/.]+)/members", MembershipViewSet, basename="membership")
router.register("(?P<org_pk>[^/.]+)/departments", DepartmentViewSet, basename="department")

urlpatterns = router.urls
