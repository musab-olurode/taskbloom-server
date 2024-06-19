# middleware.py
from django.conf import settings
from django.contrib.auth.middleware import get_user
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import BaseAuthentication
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


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get("token")
        if not token:
            return None
        user = get_user(token)
        return (user, None)


class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user, _ = JWTAuthentication().authenticate(request)
        if user:
            request.user = user


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
