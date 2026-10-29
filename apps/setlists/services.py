"""Services for the setlists app."""

from dataclasses import dataclass

from django.db import transaction

from apps.setlists.forms import BaseSetlistItemFormSet, SetlistForm
from apps.setlists.models import Setlist, SetlistItem
from apps.songs.services import SongService, SongSheet


@dataclass(frozen=True)
class SetlistSong:
    """Song of a setlist opened alone, with its neighbours."""

    item: SetlistItem
    sheet: SongSheet
    number: int
    total: int
    previous_item: SetlistItem | None
    next_item: SetlistItem | None

    @property
    def previous_number(self) -> int:
        """Return the number of the song played before this one."""
        return self.number - 1

    @property
    def next_number(self) -> int:
        """Return the number of the song played after this one."""
        return self.number + 1


class SetlistService:
    """Service class for setlist-related operations."""

    @staticmethod
    def open_song(
        setlist: Setlist, number: int, semitones: int | None = None
    ) -> SetlistSong | None:
        """Return the song at ``number``, counted from one, or ``None``.

        Without ``semitones`` the song is shown in the key chosen for the
        setlist.
        """
        items = list(setlist.items.all())
        if not 1 <= number <= len(items):
            return None
        item = items[number - 1]
        shift = item.semitones if semitones is None else semitones
        return SetlistSong(
            item=item,
            sheet=SongService.build_sheet(item.song, shift),
            number=number,
            total=len(items),
            previous_item=items[number - 2] if number > 1 else None,
            next_item=items[number] if number < len(items) else None,
        )

    @staticmethod
    @transaction.atomic
    def save(form: SetlistForm, formset: BaseSetlistItemFormSet) -> Setlist:
        """Save the setlist and its songs in a single transaction."""
        setlist = form.save()
        formset.instance = setlist
        formset.save_in_order()
        return setlist
