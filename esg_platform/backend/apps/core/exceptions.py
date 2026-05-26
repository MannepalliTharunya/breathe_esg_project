import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": {
                "code": _status_to_code(response.status_code),
                "message": _extract_message(response.data),
                "details": response.data,
            }
        }
    else:
        logger.exception("Unhandled exception", exc_info=exc)
        response = Response(
            {"error": {"code": "internal_error", "message": "An unexpected error occurred.", "details": {}}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return response


def _status_to_code(s):
    return {400: "bad_request", 401: "unauthorized", 403: "forbidden",
            404: "not_found", 409: "conflict", 422: "unprocessable", 500: "internal_error"}.get(s, "error")


def _extract_message(data):
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        first = next(iter(data), None)
        if first:
            v = data[first]
            return str(v[0]) if isinstance(v, list) else str(v)
    if isinstance(data, list) and data:
        return str(data[0])
    return "An error occurred."
