"""
Authentication endpoints:
- POST /registration/ : create user + profile, return token + basic user data
- POST /login/        : return token + basic user data

Uses DRF TokenAuthentication.
"""

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import EmailAuthTokenSerializer, RegistrationSerializer


class LoginView(ObtainAuthToken):
    """
    Login endpoint that returns a DRF auth token plus basic user information.
    """

    permission_classes = [AllowAny]
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Validate credentials, get/create token, return token payload.
        """
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )


class RegistrationView(generics.CreateAPIView):
    """
    Registration endpoint that creates a user and returns a DRF auth token.
    """

    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create user, get/create token, return token payload.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )
