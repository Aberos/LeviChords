"""Tests for what each access level can do on the site."""

import pytest
from django.contrib.auth.models import Group, User
from django.test import Client
from django.urls import reverse

from apps.setlists.models import Setlist
from apps.songs.models import Song
from apps.users.roles import ROLE_PERMISSIONS, Role
from apps.users.services import UserService

pytestmark = pytest.mark.django_db


@pytest.fixture
def setlist(song: Song) -> Setlist:
    """Return a setlist with one song."""
    setlist = Setlist.objects.create(date="2026-11-01")
    setlist.items.create(song=song, position=1)
    return setlist


@pytest.fixture
def editing_urls(song: Song, setlist: Setlist) -> list[str]:
    """Return the pages that change songs or setlists."""
    return [
        reverse("songs:create"),
        reverse("songs:update", args=[song.pk]),
        reverse("songs:delete", args=[song.pk]),
        reverse("setlists:create"),
        reverse("setlists:update", args=[setlist.pk]),
        reverse("setlists:delete", args=[setlist.pk]),
    ]


@pytest.fixture
def reading_urls(song: Song, setlist: Setlist) -> list[str]:
    """Return the pages that only show songs or setlists."""
    return [
        reverse("songs:list"),
        reverse("songs:detail", args=[song.pk]),
        reverse("setlists:list"),
        reverse("setlists:detail", args=[setlist.pk]),
        reverse("setlists:song", args=[setlist.pk, 1]),
    ]


@pytest.fixture
def users_urls(user: User) -> list[str]:
    """Return the pages that manage users."""
    return [
        reverse("users:list"),
        reverse("users:create"),
        reverse("users:update", args=[user.pk]),
    ]


def test_groups_have_the_permissions_of_each_level() -> None:
    """Every access level has a group with exactly its permissions."""
    for role, names in ROLE_PERMISSIONS.items():
        group = Group.objects.get(name=role.label)
        codenames = set(group.permissions.values_list("codename", flat=True))
        assert codenames == {name.split(".")[1] for name in names}


def test_reader_only_reads(
    reader_client: Client,
    reading_urls: list[str],
    editing_urls: list[str],
    users_urls: list[str],
) -> None:
    """A reader opens songs and setlists, and nothing else."""
    for url in reading_urls:
        assert reader_client.get(url).status_code == 200, url
    for url in editing_urls + users_urls:
        assert reader_client.get(url).status_code == 403, url


def test_reader_cannot_post_changes(reader_client: Client, song: Song) -> None:
    """Posting directly is refused to a reader as well."""
    response = reader_client.post(reverse("songs:delete", args=[song.pk]))
    assert response.status_code == 403
    assert Song.objects.filter(pk=song.pk).exists()


def test_reader_does_not_see_editing_buttons(
    reader_client: Client, song: Song, setlist: Setlist
) -> None:
    """The buttons to create, edit and delete are hidden from readers."""
    pages = [
        reader_client.get(reverse("songs:list")),
        reader_client.get(song.get_absolute_url()),
        reader_client.get(reverse("setlists:list")),
        reader_client.get(setlist.get_absolute_url()),
    ]
    for response in pages:
        content = response.content.decode()
        assert "/editar/" not in content
        assert "/excluir/" not in content
        assert "/nova/" not in content
        assert "/novo/" not in content
        assert reverse("users:list") not in content


def test_editor_edits_but_does_not_manage_users(
    logged_client: Client,
    reading_urls: list[str],
    editing_urls: list[str],
    users_urls: list[str],
) -> None:
    """An editor changes songs and setlists, but not users."""
    for url in reading_urls + editing_urls:
        assert logged_client.get(url).status_code == 200, url
    for url in users_urls:
        assert logged_client.get(url).status_code == 403, url
    response = logged_client.get(reverse("songs:list"))
    assert reverse("users:list") not in response.content.decode()


def test_admin_does_everything(
    manager_client: Client,
    reading_urls: list[str],
    editing_urls: list[str],
    users_urls: list[str],
) -> None:
    """An administrator opens every page and sees the users tab."""
    for url in reading_urls + editing_urls + users_urls:
        assert manager_client.get(url).status_code == 200, url
    response = manager_client.get(reverse("songs:list"))
    assert reverse("users:list") in response.content.decode()


def test_user_without_level_sees_nothing(client: Client, song: Song) -> None:
    """A user outside every level gets the permission denied page."""
    client.force_login(User.objects.create_user("novo", password="x"))
    response = client.get(reverse("songs:list"))
    assert response.status_code == 403
    assert "Sem permissão" in response.content.decode()


def test_superuser_is_admin(admin_user: User) -> None:
    """A superuser counts as administrator without any group."""
    assert UserService.role_of(admin_user) == Role.ADMIN
