"""Access levels of the site and the permissions of each one."""

from django.db import models


class Role(models.TextChoices):
    """Access level of a user, stored as the name of a group."""

    ADMIN = "admin", "Administrador"
    EDITOR = "editor", "Editor"
    READER = "reader", "Leitor"


READER_PERMISSIONS: tuple[str, ...] = (
    "songs.view_song",
    "setlists.view_setlist",
    "setlists.view_setlistitem",
)
EDITOR_PERMISSIONS: tuple[str, ...] = (
    *READER_PERMISSIONS,
    "songs.add_song",
    "songs.change_song",
    "songs.delete_song",
    "setlists.add_setlist",
    "setlists.change_setlist",
    "setlists.delete_setlist",
    "setlists.add_setlistitem",
    "setlists.change_setlistitem",
    "setlists.delete_setlistitem",
)
ADMIN_PERMISSIONS: tuple[str, ...] = (
    *EDITOR_PERMISSIONS,
    "auth.view_user",
    "auth.add_user",
    "auth.change_user",
)
ROLE_PERMISSIONS: dict[Role, tuple[str, ...]] = {
    Role.ADMIN: ADMIN_PERMISSIONS,
    Role.EDITOR: EDITOR_PERMISSIONS,
    Role.READER: READER_PERMISSIONS,
}
