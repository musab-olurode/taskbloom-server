from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication


class TokenAuthSupportCookie(TokenAuthentication):
    """
    Extend the TokenAuthentication class to support cookie based authentication
    """

    def authenticate(self, request):
        # Check if 'token' is in the request cookies.
        # Give precedence to 'Authorization' header.
        if "token" in request.COOKIES and "HTTP_AUTHORIZATION" not in request.META:
            return self.authenticate_credentials(request.COOKIES.get("token"))
        return super().authenticate(request)


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            response = Response(
                {"status": False, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return response
