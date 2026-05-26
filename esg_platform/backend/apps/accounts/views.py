import logging
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

logger = logging.getLogger(__name__)


@extend_schema(tags=["Auth"])
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Auth"])
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        # Embed role and org in token claims
        refresh["role"] = user.role
        refresh["org_id"] = str(user.organization_id) if user.organization_id else None
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        })


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
        except (TokenError, KeyError):
            pass
        return Response({"detail": "Logged out successfully."})


@extend_schema(tags=["Auth"])
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


@extend_schema(tags=["Auth"])
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["created_at", "email"]

    def get_queryset(self):
        qs = CustomUser.objects.filter(is_active=True)
        if not self.request.user.is_staff:
            qs = qs.filter(organization=self.request.organization)
        return qs.select_related("organization")
