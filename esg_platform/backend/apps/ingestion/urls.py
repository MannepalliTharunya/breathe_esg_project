from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UploadBatchViewSet, RawRecordListView, download_template

router = DefaultRouter()
router.register("batches", UploadBatchViewSet, basename="upload-batch")

urlpatterns = router.urls + [
    path("raw-records/", RawRecordListView.as_view(), name="raw-record-list"),
    path("template/<str:source_type>/", download_template, name="download-template"),
]
