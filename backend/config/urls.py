from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Health / readiness probes
    path("api/v1/", include("apps.core.urls")),

    # API v1
    path("api/v1/auth/", include("apps.users.urls.auth")),
    path("api/v1/users/", include("apps.users.urls.users")),
    path("api/v1/organizations/", include("apps.organizations.urls")),
    path("api/v1/esg/", include("apps.esg_data.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/frameworks/", include("apps.frameworks.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/integrations/", include("apps.integrations.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),

    # OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Prometheus metrics (only when the app is installed)
if "django_prometheus" in settings.INSTALLED_APPS:
    from django.urls import include as _include
    urlpatterns += [path("", _include("django_prometheus.urls"))]

if settings.DEBUG:
    try:
        import debug_toolbar
        if "debug_toolbar" in settings.INSTALLED_APPS:
            urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
