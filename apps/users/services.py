"""Services for the users app."""

from django.contrib.auth.models import User
from django.db import transaction

from apps.users.forms import UserCreateForm, UserUpdateForm
from apps.users.repository import UserRepository
from apps.users.roles import ROLE_PERMISSIONS, Role


class UserService:
    """Service class for user accounts and access levels."""

    @staticmethod
    def sync_groups() -> None:
        """Create the group of each access level with its permissions."""
        for role, names in ROLE_PERMISSIONS.items():
            group = UserRepository.group_named(role.label)
            group.permissions.set(UserRepository.permissions(names))

    @staticmethod
    def role_of(user: User) -> Role | None:
        """Return the access level of the user, or ``None`` without one."""
        if user.is_superuser:
            return Role.ADMIN
        names = {group.name for group in user.groups.all()}
        for role in Role:
            if role.label in names:
                return role
        return None

    @staticmethod
    def can_edit(acting_user: User, account: User) -> bool:
        """Tell whether ``acting_user`` may edit ``account``.

        Only a superuser edits another superuser, so an administrator
        cannot take over a superuser by changing their password.
        """
        if not acting_user.has_perm("auth.change_user"):
            return False
        return acting_user.is_superuser or not account.is_superuser

    @staticmethod
    def assign_role(user: User, role: Role) -> None:
        """Leave the user only in the group of the given access level."""
        others = [UserRepository.group_named(item.label) for item in Role]
        user.groups.remove(*others)
        user.groups.add(UserRepository.group_named(role.label))

    @staticmethod
    @transaction.atomic
    def save(form: UserCreateForm | UserUpdateForm) -> User:
        """Save the user, the new password and the chosen access level."""
        user = form.save()
        if not form.fields["role"].disabled:
            UserService.assign_role(user, Role(form.cleaned_data["role"]))
        return user
