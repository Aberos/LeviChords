"""Database queries for setlists."""

from datetime import date

from django.db.models import Count, Prefetch, QuerySet

from apps.setlists.models import Setlist, SetlistItem


class SetlistRepository:
    """Repository class for setlist queries."""

    @staticmethod
    def list_with_song_count() -> QuerySet[Setlist]:
        """Return every setlist, newest first, with ``song_count``."""
        return Setlist.objects.annotate(song_count=Count("items")).order_by(
            "-date", "-pk"
        )

    @staticmethod
    def with_songs() -> QuerySet[Setlist]:
        """Return setlists with their ordered items and songs prefetched."""
        items = SetlistItem.objects.select_related("song")
        return Setlist.objects.prefetch_related(
            Prefetch("items", queryset=items)
        )

    @staticmethod
    def next_from(day: date) -> Setlist | None:
        """Return the first setlist on or after the given day."""
        return (
            Setlist.objects.filter(date__gte=day)
            .order_by("date", "pk")
            .first()
        )
