"""Tests for the page where users change their own name and password."""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_every_level_opens_the_account_page(
    reader_client: Client,
) -> None:
    """Even a reader reaches the account page and its link."""
    response = reader_client.get(reverse("account:profile"))
    content = response.content.decode()
    assert response.status_code == 200
    assert "leitor" in content
    assert "Leitor" in content
    assert reverse("account:password") in content


def test_user_changes_own_name(logged_client: Client, user: User) -> None:
    """The name is saved for the logged user."""
    response = logged_client.post(
        reverse("account:profile"), {"first_name": "Levi"}
    )
    user.refresh_from_db()
    assert response["Location"] == reverse("account:profile")
    assert user.first_name == "Levi"


def test_user_changes_own_password_and_stays_logged(
    logged_client: Client, user: User
) -> None:
    """The new password works and the session is kept."""
    response = logged_client.post(
        reverse("account:password"),
        {
            "old_password": "senha-123",
            "new_password1": "Teclado-2026!",
            "new_password2": "Teclado-2026!",
        },
    )
    user.refresh_from_db()
    assert response["Location"] == reverse("account:profile")
    assert user.check_password("Teclado-2026!")
    assert logged_client.get(reverse("songs:list")).status_code == 200


def test_password_change_requires_the_current_password(
    logged_client: Client, user: User
) -> None:
    """A wrong current password keeps the old one."""
    response = logged_client.post(
        reverse("account:password"),
        {
            "old_password": "errada",
            "new_password1": "Teclado-2026!",
            "new_password2": "Teclado-2026!",
        },
    )
    user.refresh_from_db()
    assert response.status_code == 200
    assert user.check_password("senha-123")


def test_topbar_links_to_the_account(reader_client: Client) -> None:
    """The top bar offers the account page on every page."""
    response = reader_client.get(reverse("songs:list"))
    assert reverse("account:profile") in response.content.decode()
