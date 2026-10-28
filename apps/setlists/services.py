"""Services for the setlists app."""

from django.db import transaction

from apps.setlists.forms import BaseSetlistItemFormSet, SetlistForm
from apps.setlists.models import Setlist
from apps.songs.services import SongService, SongSheet


class SetlistService:
    """Service class for setlist-related operations."""

    @staticmethod
    def build_sheets(setlist: Setlist) -> list[SongSheet]:
        """Return every song of the setlist in the key chosen for it."""
        return [
            SongService.build_sheet(item.song, item.semitones)
            for item in setlist.items.all()
        ]

    @staticmethod
    @transaction.atomic
    def save(form: SetlistForm, formset: BaseSetlistItemFormSet) -> Setlist:
        """Save the setlist and its songs in a single transaction."""
        setlist = form.save()
        formset.instance = setlist
        formset.save_in_order()
        return setlist
