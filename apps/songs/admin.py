"""Admin configuration for the songs app."""

from django.contrib import admin

from apps.songs.models import Song


@admin.register(Song)
class SongAdmin(admin.ModelAdmin[Song]):
    """Admin options for songs."""

    list_display = ["title", "artist", "key", "updated_at"]
    search_fields = ["title", "artist"]
