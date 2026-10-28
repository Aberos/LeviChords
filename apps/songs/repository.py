"""Database queries for songs."""

from django.db.models import Q, QuerySet

from apps.songs.models import Song


class SongRepository:
    """Repository class for song queries."""

    @staticmethod
    def search(term: str) -> QuerySet[Song]:
        """Return songs whose title or artist contains the term."""
        songs = Song.objects.all()
        term = term.strip()
        if term:
            songs = songs.filter(
                Q(title__icontains=term) | Q(artist__icontains=term)
            )
        return songs
