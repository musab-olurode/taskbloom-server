from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.authtoken.models import Token
from .models import User
from rest_framework.response import Response


def create_jwt_token(response: Response, user_id):
    user = User.objects.get(id=user_id)
    token, _ = Token.objects.get_or_create(user=user)

    max_age = 1 * 24 * 60 * 60  # 1 day
    response.set_cookie(
        "token",
        token.key,
        max_age=max_age,
        secure=True,
        httponly=False,
        samesite="None",
    )
