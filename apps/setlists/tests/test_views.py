"""Tests for the setlists views."""

from datetime import timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.setlists.models import Setlist
from apps.songs.models import Song

pytestmark = pytest.mark.django_db


def _formset_data(
    rows: list[dict[str, str]], initial: int = 0
) -> dict[str, str]:
    """Build the POST data of the songs formset."""
    data = {
        "items-TOTAL_FORMS": str(len(rows)),
        "items-INITIAL_FORMS": str(initial),
        "items-MIN_NUM_FORMS": "0",
        "items-MAX_NUM_FORMS": "1000",
    }
    for index, row in enumerate(rows):
        for field, value in row.items():
            data[f"items-{index}-{field}"] = value
    return data


def test_home_opens_next_setlist(logged_client: Client) -> None:
    """The home page redirects to the next scheduled setlist."""
    today = timezone.localdate()
    Setlist.objects.create(date=today - timedelta(days=7))
    upcoming = Setlist.objects.create(date=today + timedelta(days=3))
    Setlist.objects.create(date=today + timedelta(days=10))
    response = logged_client.get(reverse("home"))
    assert response["Location"] == upcoming.get_absolute_url()


def test_home_without_setlists_opens_list(logged_client: Client) -> None:
    """Without upcoming setlists the list is shown."""
    response = logged_client.get(reverse("home"))
    assert response["Location"] == reverse("setlists:list")


def test_create_setlist_in_chosen_order(
    logged_client: Client, song: Song
) -> None:
    """Songs are saved in the order given by their positions."""
    other = Song.objects.create(title="Aclame", key="D", content="D")
    rows = [
        {"song": str(song.pk), "position": "2", "semitones": "2"},
        {"song": str(other.pk), "position": "1", "semitones": "0"},
        {"song": "", "position": "3", "semitones": "0"},
    ]
    data = {"date": "2026-11-01", "description": "Manhã"}
    data.update(_formset_data(rows))
    response = logged_client.post(reverse("setlists:create"), data)
    setlist = Setlist.objects.get()
    items = list(setlist.items.all())
    assert response.status_code == 302
    assert [item.song for item in items] == [other, song]
    assert [item.position for item in items] == [1, 2]
    assert items[1].key == "A"


def test_update_removes_items(logged_client: Client, song: Song) -> None:
    """Checked rows are removed from the setlist."""
    setlist = Setlist.objects.create(date="2026-11-01")
    item = setlist.items.create(song=song, position=1)
    rows = [
        {
            "id": str(item.pk),
            "setlist": str(setlist.pk),
            "song": str(song.pk),
            "position": "1",
            "semitones": "0",
            "DELETE": "on",
        }
    ]
    data = {"date": "2026-11-01", "description": ""}
    data.update(_formset_data(rows, initial=1))
    logged_client.post(reverse("setlists:update", args=[setlist.pk]), data)
    assert not setlist.items.exists()


def test_detail_shows_songs_in_their_keys(
    logged_client: Client, song: Song
) -> None:
    """Each song is shown in the key chosen for the setlist."""
    setlist = Setlist.objects.create(date="2026-11-01")
    setlist.items.create(song=song, position=1, semitones=-2)
    response = logged_client.get(setlist.get_absolute_url())
    content = response.content.decode()
    assert song.title in content
    assert "C/E" in content
