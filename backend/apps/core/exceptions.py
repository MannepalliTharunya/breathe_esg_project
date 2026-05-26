import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default handler to return a consistent error envelope:
    {
        "error": {
            "code": "...",
            "message": "...",
            "details": {...}
        }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "error": {
                "code": _get_error_code(response.status_code),
                "message": _extract_message(response.data),
                "details": response.data,
            }
        }
        response.data = error_payload
    else:
        # Unhandled exception — log and return 500
        logger.exception("Unhandled exception in view", exc_info=exc)
        response = Response(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _get_error_code(status_code: int) -> str:
    codes = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "unprocessable_entity",
        429: "too_many_requests",
        500: "internal_server_error",
    }
    return codes.get(status_code, "error")


def _extract_message(data) -> str:
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        first_key = next(iter(data), None)
        if first_key:
            val = data[first_key]
            return str(val[0]) if isinstance(val, list) else str(val)
    if isinstance(data, list) and data:
        return str(data[0])
    return "An error occurred."
