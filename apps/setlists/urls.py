"""URL routes for the setlists app."""

from django.urls import path

from apps.setlists import views

app_name = "setlists"

urlpatterns = [
    path("", views.SetlistListView.as_view(), name="list"),
    path("novo/", views.SetlistEditView.as_view(), name="create"),
    path("<int:pk>/", views.SetlistDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.SetlistEditView.as_view(), name="update"),
    path(
        "<int:pk>/excluir/", views.SetlistDeleteView.as_view(), name="delete"
    ),
]
