from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        qs = Notification.objects.filter(recipient=self.request.user)
        unread_only = self.request.query_params.get("unread")
        if unread_only == "true":
            qs = qs.filter(is_read=False)
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["unread_count"] = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return response


class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user)

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.mark_read()
        return Response({"detail": "Marked as read."}, status=status.HTTP_200_OK)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.utils import timezone
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({"detail": "All notifications marked as read."}, status=status.HTTP_200_OK)
