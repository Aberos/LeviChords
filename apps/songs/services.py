"""Services for the songs app."""

from dataclasses import dataclass

from apps.songs.chords import (
    SheetLine,
    normalize_semitones,
    parse_sheet,
    transpose_key,
)
from apps.songs.models import Song


@dataclass(frozen=True)
class SongSheet:
    """Song prepared for the reading mode in a given key."""

    song: Song
    semitones: int
    key: str
    lines: list[SheetLine]

    @property
    def semitones_up(self) -> int:
        """Return the shift that raises the current key by one semitone."""
        return normalize_semitones(self.semitones + 1)

    @property
    def semitones_down(self) -> int:
        """Return the shift that lowers the current key by one semitone."""
        return normalize_semitones(self.semitones - 1)


class SongService:
    """Service class for song-related operations."""

    @staticmethod
    def parse_semitones(raw: str | None) -> int:
        """Convert a user supplied shift, ignoring invalid values."""
        try:
            return normalize_semitones(int(raw or "0"))
        except ValueError:
            return 0

    @staticmethod
    def preview(content: str) -> list[SheetLine]:
        """Return the classified lines of a sheet that was not saved yet."""
        return parse_sheet(content)

    @staticmethod
    def build_sheet(song: Song, semitones: int = 0) -> SongSheet:
        """Return the song lines transposed by the given semitones."""
        semitones = normalize_semitones(semitones)
        return SongSheet(
            song=song,
            semitones=semitones,
            key=transpose_key(song.key, semitones) if song.key else "",
            lines=parse_sheet(song.content, semitones, song.key),
        )
