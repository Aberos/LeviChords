"""URL routes for the account of the logged user."""

from django.urls import path

from apps.users import views

app_name = "account"

urlpatterns = [
    path("", views.ProfileView.as_view(), name="profile"),
    path("senha/", views.OwnPasswordChangeView.as_view(), name="password"),
]
