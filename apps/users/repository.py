"""Database queries for users."""

from django.contrib.auth.models import Group, Permission, User
from django.db.models import Q, QuerySet


class UserRepository:
    """Repository class for user queries."""

    @staticmethod
    def list_with_groups() -> QuerySet[User]:
        """Return every user, active first, with their groups prefetched."""
        return User.objects.prefetch_related("groups").order_by(
            "-is_active", "first_name", "username"
        )

    @staticmethod
    def group_named(name: str) -> Group:
        """Return the group with the given name, creating it if needed."""
        group, _ = Group.objects.get_or_create(name=name)
        return group

    @staticmethod
    def permissions(names: tuple[str, ...]) -> QuerySet[Permission]:
        """Return the permissions written as ``app_label.codename``."""
        query = Q(pk__in=[])
        for name in names:
            app_label, codename = name.split(".")
            query |= Q(content_type__app_label=app_label, codename=codename)
        return Permission.objects.filter(query)
