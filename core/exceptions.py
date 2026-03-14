from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from .responses import standard_response
import logging
import sentry_sdk

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize the error response
        message = "Operation failed"
        errors = response.data

        if isinstance(exc, ValidationError):
            message = "Validation failed"
        elif isinstance(exc, (PermissionDenied, DjangoPermissionDenied)):
            message = "Permission denied"
        elif isinstance(exc, (NotFound, Http404)):
            message = "Resource not found"
        
        # In case of rate limit (status code 429)
        if response.status_code == 429:
            message = "Too many requests"

        return standard_response(
            success=False,
            data=None,
            message=message,
            errors=errors,
            status=response.status_code
        )

    # Handle unexpected errors
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    sentry_sdk.capture_exception(exc)

    return standard_response(
        success=False,
        data=None,
        message="An unexpected error occurred",
        errors={"detail": str(exc)},
        status=500
    )
