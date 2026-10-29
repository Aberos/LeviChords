"""Shared pytest fixtures."""

import pytest
from django.contrib.auth.models import User
from django.test import Client

from apps.songs.models import Song
from apps.users.roles import Role
from apps.users.services import UserService


def create_user(username: str, role: Role) -> User:
    """Create a user with the given access level."""
    account = User.objects.create_user(username=username, password="senha-123")
    UserService.assign_role(account, role)
    return account


@pytest.fixture
def user(db: None) -> User:
    """Return an editor, able to edit songs and setlists."""
    return create_user("musico", Role.EDITOR)


@pytest.fixture
def reader_client(client: Client, db: None) -> Client:
    """Return a test client authenticated as a reader."""
    client.force_login(create_user("leitor", Role.READER))
    return client


@pytest.fixture
def manager(db: None) -> User:
    """Return an administrator who is not a superuser."""
    return create_user("gestor", Role.ADMIN)


@pytest.fixture
def manager_client(client: Client, manager: User) -> Client:
    """Return a test client authenticated as an administrator."""
    client.force_login(manager)
    return client


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
