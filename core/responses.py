from rest_framework.response import Response

def standard_response(success=True, data=None, message="OK", errors=None, status=200):
    """
    Standard response wrapper for all API endpoints.
    """
    return Response(
        {
            "success": success,
            "data": data,
            "message": message,
            "errors": errors,
        },
        status=status,
    )
