"""Application configuration for user accounts."""

from typing import Any

from django.apps import AppConfig
from django.db.models.signals import post_migrate


def sync_role_groups(sender: AppConfig, **kwargs: Any) -> None:
    """Keep the groups of each access level with their permissions."""
    from apps.users.services import UserService

    UserService.sync_groups()


class UsersConfig(AppConfig):
    """Configure the users app."""

    name = "apps.users"
    verbose_name = "Usuários"

    def ready(self) -> None:
        """Update the access level groups after every migration."""
        post_migrate.connect(sync_role_groups, sender=self)
