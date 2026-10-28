"""Admin configuration for the setlists app."""

from django.contrib import admin

from apps.setlists.models import Setlist, SetlistItem


class SetlistItemInline(admin.TabularInline[SetlistItem, Setlist]):
    """Inline editor for the songs of a setlist."""

    model = SetlistItem
    extra = 1
    autocomplete_fields = ["song"]


@admin.register(Setlist)
class SetlistAdmin(admin.ModelAdmin[Setlist]):
    """Admin options for setlists."""

    list_display = ["date", "description"]
    date_hierarchy = "date"
    inlines = [SetlistItemInline]
