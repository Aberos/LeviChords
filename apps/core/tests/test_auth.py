"""Tests for the login requirement on every page."""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from apps.setlists.models import Setlist
from apps.songs.models import Song

pytestmark = pytest.mark.django_db


@pytest.fixture
def protected_urls(song: Song) -> list[str]:
    """Return one URL of every page of the site."""
    setlist = Setlist.objects.create(date="2026-11-01")
    return [
        reverse("home"),
        reverse("songs:list"),
        reverse("songs:create"),
        reverse("songs:detail", args=[song.pk]),
        reverse("songs:update", args=[song.pk]),
        reverse("songs:delete", args=[song.pk]),
        reverse("setlists:list"),
        reverse("setlists:create"),
        reverse("setlists:detail", args=[setlist.pk]),
        reverse("setlists:update", args=[setlist.pk]),
        reverse("setlists:delete", args=[setlist.pk]),
    ]


def test_anonymous_users_are_sent_to_login(
    client: Client, protected_urls: list[str]
) -> None:
    """Every page redirects anonymous users to the login page."""
    login = reverse("login")
    for url in protected_urls:
        response = client.get(url)
        assert response.status_code == 302, url
        assert response["Location"] == f"{login}?next={url}", url


def test_login_page_is_public(client: Client) -> None:
    """The login page opens without authentication."""
    response = client.get(reverse("login"))
    assert response.status_code == 200
    assert 'name="username"' in response.content.decode()


def test_login_with_valid_credentials(client: Client, user: User) -> None:
    """Valid credentials open the site."""
    response = client.post(
        reverse("login"), {"username": "musico", "password": "senha-123"}
    )
    assert response.status_code == 302
    assert response["Location"] == reverse("home")


def test_login_with_invalid_credentials(client: Client, user: User) -> None:
    """Invalid credentials keep the user on the login page."""
    response = client.post(
        reverse("login"), {"username": "musico", "password": "errada"}
    )
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_login_page_offers_remember_me(client: Client) -> None:
    """The login page shows the remember me checkbox."""
    response = client.get(reverse("login"))
    assert 'name="remember"' in response.content.decode()


def test_login_without_remember_ends_on_browser_close(
    client: Client, user: User
) -> None:
    """Without remember me, the session ends when the browser closes."""
    client.post(
        reverse("login"), {"username": "musico", "password": "senha-123"}
    )
    assert client.session.get_expire_at_browser_close()


def test_login_with_remember_keeps_the_session(
    client: Client, user: User
) -> None:
    """With remember me, the session survives closing the browser."""
    client.post(
        reverse("login"),
        {"username": "musico", "password": "senha-123", "remember": "on"},
    )
    assert "_auth_user_id" in client.session
    assert not client.session.get_expire_at_browser_close()
    assert client.session.get_expiry_age() == 60 * 60 * 24 * 30


def test_logout_returns_to_login(logged_client: Client) -> None:
    """After logging out, pages require the login again."""
    logged_client.post(reverse("logout"))
    response = logged_client.get(reverse("songs:list"))
    assert response.status_code == 302
