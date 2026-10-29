"""Tests for the user management views."""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from apps.users.roles import Role
from apps.users.services import UserService

pytestmark = pytest.mark.django_db


def _update_data(account: User, **changes: str) -> dict[str, str]:
    """Build the POST data of the edit form for ``account``."""
    data = {
        "username": account.username,
        "first_name": account.first_name,
        "is_active": "on" if account.is_active else "",
        "role": str(UserService.role_of(account) or Role.READER),
        "new_password": "",
    }
    data.update(changes)
    return {key: value for key, value in data.items() if value != ""}


def test_list_shows_users_and_levels(
    manager_client: Client, user: User
) -> None:
    """The list shows every user with their access level."""
    content = manager_client.get(reverse("users:list")).content.decode()
    assert "musico" in content
    assert "Editor" in content
    assert "Administrador" in content


def test_admin_creates_a_reader(manager_client: Client) -> None:
    """A new user gets the chosen level and can log in."""
    response = manager_client.post(
        reverse("users:create"),
        {
            "username": "joao",
            "first_name": "João",
            "password1": "Teclado-2026!",
            "password2": "Teclado-2026!",
            "role": "reader",
        },
    )
    created = User.objects.get(username="joao")
    assert response["Location"] == reverse("users:list")
    assert UserService.role_of(created) == Role.READER
    assert created.check_password("Teclado-2026!")


def test_create_rejects_different_passwords(manager_client: Client) -> None:
    """The password confirmation must match."""
    response = manager_client.post(
        reverse("users:create"),
        {
            "username": "joao",
            "password1": "Teclado-2026!",
            "password2": "Outra-2026!",
            "role": "reader",
        },
    )
    assert response.status_code == 200
    assert not User.objects.filter(username="joao").exists()


def test_admin_changes_level_and_password(
    manager_client: Client, user: User
) -> None:
    """The level is replaced and a new password is set when given."""
    manager_client.post(
        reverse("users:update", args=[user.pk]),
        _update_data(user, role="reader", new_password="Violao-2026!"),
    )
    user.refresh_from_db()
    assert UserService.role_of(user) == Role.READER
    assert user.groups.count() == 1
    assert user.check_password("Violao-2026!")


def test_blank_password_keeps_the_current_one(
    manager_client: Client, user: User
) -> None:
    """Leaving the new password blank keeps the old one."""
    manager_client.post(
        reverse("users:update", args=[user.pk]), _update_data(user)
    )
    user.refresh_from_db()
    assert user.check_password("senha-123")


def test_admin_deactivates_a_user(manager_client: Client, user: User) -> None:
    """A deactivated user can no longer log in."""
    manager_client.post(
        reverse("users:update", args=[user.pk]),
        _update_data(user, is_active=""),
    )
    user.refresh_from_db()
    assert not user.is_active
    assert not Client().login(username="musico", password="senha-123")


def test_admin_cannot_demote_or_deactivate_themselves(
    manager_client: Client, manager: User
) -> None:
    """The own level and active flag are locked on the edit form."""
    manager_client.post(
        reverse("users:update", args=[manager.pk]),
        _update_data(manager, role="reader", is_active=""),
    )
    manager.refresh_from_db()
    assert manager.is_active
    assert UserService.role_of(manager) == Role.ADMIN


def test_admin_cannot_edit_a_superuser(
    manager_client: Client, admin_user: User
) -> None:
    """Only a superuser edits another superuser."""
    url = reverse("users:update", args=[admin_user.pk])
    assert manager_client.get(url).status_code == 404
    content = manager_client.get(reverse("users:list")).content.decode()
    assert url not in content


def test_superuser_edits_other_superusers(
    admin_client: Client, admin_user: User
) -> None:
    """A superuser may edit a superuser, but the level stays locked."""
    other = User.objects.create_superuser("chefe", password="x")
    response = admin_client.get(reverse("users:update", args=[other.pk]))
    assert response.status_code == 200
    assert "sempre administrador" in response.content.decode()
