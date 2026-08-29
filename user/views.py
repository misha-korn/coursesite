import logging

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.serializators import (
    ChangePasswordSerializer,
    MeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PublicSerializer,
    RegisterSerializer, EmailChangeRequestSerializer, EmailChangeConfirmSerializer, VerifyEmailConfirmSerializer,
)
from user.tasks import send_reset_password_confirmation, send_change_email_confirmation, send_change_email_warning, \
    send_verify_email_confirmation
from user.tokens import make_reset_password_token, make_change_email_token, make_verify_email_token

logger = logging.getLogger(__name__)

User = get_user_model()


class ThrottledObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        logger.info("Зарегистрирован новый пользователь: %s", serializer.validated_data["username"])

        token = make_verify_email_token(user)
        send_verify_email_confirmation.delay(user.email, token)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


class PublicUserView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicSerializer
    queryset = User.objects.filter(is_active=True)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        for token in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=token)

        logger.info("Пользователь %s сменил пароль", request.user.pk)
        return Response(status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(
            email=email,
            is_active=True,
        ).first()

        if user and user.email_verified:
            token = make_reset_password_token(user)
            send_reset_password_confirmation.delay(email, user.email_verified, token)
        return Response(status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)

        logger.info("Пользователь %s восстановил пароль", user.pk)

        return Response(status=status.HTTP_200_OK)


class EmailChangeRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailChangeRequestSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        new_email = serializer.validated_data["new_email"]
        user = self.request.user
        token = make_change_email_token(user, new_email)

        if user.email and user.email_verified:
            send_change_email_warning.delay(user.email, user.email_verified, new_email)
        send_change_email_confirmation.delay(new_email, token)

        return Response(status=status.HTTP_200_OK)


class EmailChangeConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailChangeConfirmSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        logger.info("Пользователь %s сменил почту на %s", user.pk, user.email)

        return Response(status=status.HTTP_200_OK)


class VerifyEmailRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        if request.user.email_verified:
            return Response(status=status.HTTP_200_OK)
        token = make_verify_email_token(self.request.user)
        send_verify_email_confirmation.delay(request.user.email, token)

        return Response(status=status.HTTP_200_OK)


class VerifyEmailConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyEmailConfirmSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        logger.info("Пользователь %s подтвердил свою почту %s", user.pk, user.email)

        return Response(status=status.HTTP_200_OK)