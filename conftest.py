"""Shared pytest fixtures."""

import pytest
from django.contrib.auth.models import User
from django.test import Client

from apps.songs.models import Song


@pytest.fixture
def user(db: None) -> User:
    """Return a regular user able to edit songs and setlists."""
    return User.objects.create_user(username="musico", password="senha-123")


@pytest.fixture
def logged_client(client: Client, user: User) -> Client:
    """Return a test client authenticated as ``user``."""
    client.force_login(user)
    return client


@pytest.fixture
def song(db: None) -> Song:
    """Return a song in G with one chord line and one lyric line."""
    return Song.objects.create(
        title="Grande é o Senhor",
        artist="Ministério",
        key="G",
        content="[Intro] G  D\n\nG        D/F#\nGrande é o Senhor\n",
    )
