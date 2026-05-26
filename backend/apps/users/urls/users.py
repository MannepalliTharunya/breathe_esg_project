from django.urls import path
from apps.users.views import MeView, ChangePasswordView, UserPreferencesView, UserListView

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("me/", MeView.as_view(), name="user-me"),
    path("me/password/", ChangePasswordView.as_view(), name="user-change-password"),
    path("me/preferences/", UserPreferencesView.as_view(), name="user-preferences"),
]
