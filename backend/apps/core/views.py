"""
Health check and readiness probe endpoints.
Used by Docker, Kubernetes, and load balancers.
"""
import time
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Liveness probe — returns 200 if the app process is alive.
    """
    return Response({"status": "ok", "timestamp": time.time()})


@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness probe — checks DB and cache connectivity.
    Returns 503 if any dependency is unavailable.
    """
    checks = {}
    overall_ok = True

    # Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        overall_ok = False

    # Cache (Redis)
    try:
        cache.set("_health_probe", "1", timeout=5)
        assert cache.get("_health_probe") == "1"
        checks["cache"] = "ok"
    except Exception as e:
        checks["cache"] = f"error: {e}"
        overall_ok = False

    http_status = status.HTTP_200_OK if overall_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response({"status": "ok" if overall_ok else "degraded", "checks": checks}, status=http_status)
