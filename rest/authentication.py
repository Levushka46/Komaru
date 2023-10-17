from rest_framework_simplejwt.authentication import JWTAuthentication, AuthUser
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from rest.models import Session


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token: Token) -> AuthUser:
        user = super().get_user(validated_token)
        jwt_token = str(validated_token)

        try:
            session = Session.objects.get(user=user, jwt_token=jwt_token)
        except Session.DoesNotExist:
            raise AuthenticationFailed(_("Session not found"), code="session_not_found")

        return user
