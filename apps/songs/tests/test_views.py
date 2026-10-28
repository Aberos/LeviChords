"""Tests for the songs views."""

import pytest
from django.test import Client
from django.urls import reverse

from apps.setlists.models import Setlist
from apps.songs.models import Song

pytestmark = pytest.mark.django_db


def test_list_shows_songs(logged_client: Client, song: Song) -> None:
    """Logged users see the song list."""
    response = logged_client.get(reverse("songs:list"))
    assert response.status_code == 200
    assert song.title in response.content.decode()


def test_list_filters_by_term(logged_client: Client, song: Song) -> None:
    """The search keeps only matching songs."""
    Song.objects.create(title="Aclame ao Senhor", content="A")
    response = logged_client.get(reverse("songs:list"), {"q": "grande"})
    content = response.content.decode()
    assert song.title in content
    assert "Aclame" not in content


def test_detail_transposes(logged_client: Client, song: Song) -> None:
    """The ``semitons`` parameter changes the key and the chords."""
    response = logged_client.get(song.get_absolute_url(), {"semitons": "2"})
    content = response.content.decode()
    assert "Tom: <strong>A</strong>" in content
    assert "E/G#" in content


def test_detail_ignores_invalid_shift(
    logged_client: Client, song: Song
) -> None:
    """Invalid shifts fall back to the original key."""
    response = logged_client.get(song.get_absolute_url(), {"semitons": "x"})
    assert "Tom: <strong>G</strong>" in response.content.decode()


def test_create_song(logged_client: Client) -> None:
    """Logged users can create songs."""
    response = logged_client.post(
        reverse("songs:create"),
        {"title": "Nova", "artist": "", "key": "D", "content": "D  A"},
    )
    created = Song.objects.get(title="Nova")
    assert response.status_code == 302
    assert response["Location"] == created.get_absolute_url()


def test_create_removes_invisible_characters(logged_client: Client) -> None:
    """Text copied from Cifra Club is stored without zero width spaces."""
    logged_client.post(
        reverse("songs:create"),
        {"title": "Nova", "key": "D", "content": "\u200bD  A\nLetra"},
    )
    assert Song.objects.get(title="Nova").content == "D  A\nLetra"


def test_create_rejects_invalid_key(logged_client: Client) -> None:
    """The key must be a valid note."""
    response = logged_client.post(
        reverse("songs:create"),
        {"title": "Nova", "key": "H", "content": "D"},
    )
    assert response.status_code == 200
    assert not Song.objects.filter(title="Nova").exists()


def test_create_preview_does_not_save(logged_client: Client) -> None:
    """The preview shows the colored sheet without saving the song."""
    response = logged_client.post(
        reverse("songs:create"),
        {"title": "", "key": "", "content": "G  D/F#\nGrande", "preview": "1"},
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert not Song.objects.exists()
    assert '<div class="line line-chords">G  D/F#</div>' in content
    assert "errorlist" not in content
    assert "Grande</textarea>" in content


def test_update_preview_keeps_the_saved_song(
    logged_client: Client, song: Song
) -> None:
    """Previewing an edit does not change the stored song."""
    response = logged_client.post(
        reverse("songs:update", args=[song.pk]),
        {"title": "Outro", "key": "G", "content": "C", "preview": "1"},
    )
    song.refresh_from_db()
    assert response.status_code == 200
    assert song.title == "Grande é o Senhor"
    assert 'value="Outro"' in response.content.decode()


def test_delete_protects_songs_in_setlists(
    logged_client: Client, song: Song
) -> None:
    """Songs used in a setlist are kept."""
    setlist = Setlist.objects.create(date="2026-11-01")
    setlist.items.create(song=song, position=1)
    response = logged_client.post(reverse("songs:delete", args=[song.pk]))
    assert response.status_code == 302
    assert Song.objects.filter(pk=song.pk).exists()
