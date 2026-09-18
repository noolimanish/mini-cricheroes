import logging

from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Global exception handler for Django REST Framework.

    Expected API exceptions are handled by DRF normally.
    Unexpected exceptions are logged and returned with
    a consistent error response.
    """

    response = exception_handler(exc, context)

    if response is not None:
        return response

    view = context.get("view")
    request = context.get("request")

    logger.exception(
        "Unhandled API exception: view=%s method=%s path=%s",
        view.__class__.__name__ if view else "UnknownView",
        request.method if request else "UnknownMethod",
        request.path if request else "UnknownPath",
        exc_info=exc
    )

    from rest_framework.response import Response
    from rest_framework import status

    return Response(
        {
            "error": "An unexpected server error occurred."
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )