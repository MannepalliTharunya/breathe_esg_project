from django.urls import path, include

# Review endpoints are served through normalization app
urlpatterns = [
    path("", include("apps.normalization.urls")),
]
