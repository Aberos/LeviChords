"""URL routes for the songs app."""

from django.urls import path

from apps.songs import views

app_name = "songs"

urlpatterns = [
    path("", views.SongListView.as_view(), name="list"),
    path("nova/", views.SongCreateView.as_view(), name="create"),
    path("<int:pk>/", views.SongDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.SongUpdateView.as_view(), name="update"),
    path("<int:pk>/excluir/", views.SongDeleteView.as_view(), name="delete"),
]
