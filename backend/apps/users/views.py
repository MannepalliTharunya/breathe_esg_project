import logging
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.core.utils import get_client_ip
from .models import User, UserPreferences
from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    UserProfileSerializer,
    UserPreferencesSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserListSerializer,
)
from .services import AuthService, UserService

logger = logging.getLogger(__name__)


@extend_schema(tags=["Authentication"])
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = AuthService.generate_tokens(user)
        tokens["user"] = UserProfileSerializer(user, context={"request": request}).data
        return Response(tokens, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Authentication"])
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        AuthService.record_successful_login(user, get_client_ip(request))
        tokens = AuthService.generate_tokens(user)
        # Serialize the user object before returning
        tokens["user"] = UserProfileSerializer(user, context={"request": request}).data
        return Response(tokens, status=status.HTTP_200_OK)


@extend_schema(tags=["Authentication"])
class LogoutView(APIView):
    def post(self, request):
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
        except (TokenError, InvalidToken, KeyError):
            pass
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


@extend_schema(tags=["Authentication"])
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.initiate_password_reset(serializer.validated_data["email"])
        # Always return 200 to prevent email enumeration
        return Response(
            {"detail": "If that email exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Authentication"])
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        success = AuthService.confirm_password_reset(
            serializer.validated_data["token"],
            serializer.validated_data["new_password"],
        )
        if not success:
            return Response(
                {"error": {"code": "invalid_token", "message": "Invalid or expired reset token."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)


@extend_schema(tags=["Users"])
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=["Users"])
class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        UserService.change_password(request.user, serializer.validated_data["new_password"])
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


@extend_schema(tags=["Users"])
class UserPreferencesView(generics.RetrieveUpdateAPIView):
    serializer_class = UserPreferencesSerializer

    def get_object(self):
        prefs, _ = UserPreferences.objects.get_or_create(user=self.request.user)
        return prefs


@extend_schema(tags=["Users"])
class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["created_at", "email", "last_name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return User.objects.filter(is_active=True).select_related("preferences")
