"""Views for managing user accounts."""

from typing import Any

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from apps.users.forms import ProfileForm, UserCreateForm, UserUpdateForm
from apps.users.repository import UserRepository
from apps.users.roles import Role
from apps.users.services import UserService


class UserListView(PermissionRequiredMixin, ListView[User]):
    """List the users with their access levels."""

    permission_required = "auth.view_user"
    template_name = "users/user_list.html"
    context_object_name = "accounts"

    def get_queryset(self) -> QuerySet[User]:
        """Return every user with their groups."""
        return UserRepository.list_with_groups()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Pair each user with their access level and edit permission."""
        context = super().get_context_data(**kwargs)
        acting_user = self.request.user
        context["rows"] = [
            (
                account,
                UserService.role_of(account),
                isinstance(acting_user, User)
                and UserService.can_edit(acting_user, account),
            )
            for account in context["accounts"]
        ]
        return context


class UserCreateView(
    PermissionRequiredMixin, CreateView[User, UserCreateForm]
):
    """Create a user with an access level."""

    permission_required = "auth.add_user"
    form_class = UserCreateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")

    def form_valid(self, form: UserCreateForm) -> HttpResponse:
        """Save the user together with the access level."""
        self.object = UserService.save(form)
        messages.success(self.request, "Usuário cadastrado.")
        return HttpResponseRedirect(self.get_success_url())


class UserUpdateView(
    PermissionRequiredMixin, UpdateView[User, UserUpdateForm]
):
    """Edit a user, keeping superusers out of reach of other admins."""

    permission_required = "auth.change_user"
    form_class = UserUpdateForm
    template_name = "users/user_form.html"
    context_object_name = "account"
    success_url = reverse_lazy("users:list")

    def get_queryset(self) -> QuerySet[User]:
        """Return the users the current user is allowed to edit."""
        accounts = UserRepository.list_with_groups()
        if self.request.user.is_superuser:
            return accounts
        return accounts.exclude(is_superuser=True)

    def get_initial(self) -> dict[str, Any]:
        """Fill the access level with the one the user has now."""
        initial = super().get_initial()
        initial["role"] = UserService.role_of(self.object) or Role.READER
        return initial

    def get_form_kwargs(self) -> dict[str, Any]:
        """Pass the current user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["acting_user"] = self.request.user
        return kwargs

    def form_valid(self, form: UserUpdateForm) -> HttpResponse:
        """Save the user together with the access level."""
        self.object = UserService.save(form)
        messages.success(self.request, "Usuário atualizado.")
        return HttpResponseRedirect(self.get_success_url())


class ProfileView(UpdateView[User, ProfileForm]):
    """Let the logged user change their own name."""

    form_class = ProfileForm
    template_name = "users/profile.html"
    context_object_name = "account"
    success_url = reverse_lazy("account:profile")

    def get_object(self, queryset: QuerySet[User] | None = None) -> User:
        """Return the logged user."""
        if not isinstance(self.request.user, User):
            raise PermissionDenied
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the access level of the logged user."""
        context = super().get_context_data(**kwargs)
        context["role"] = UserService.role_of(self.object)
        return context

    def form_valid(self, form: ProfileForm) -> HttpResponse:
        """Save the name and confirm it to the user."""
        response = super().form_valid(form)
        messages.success(self.request, "Nome atualizado.")
        return response


class OwnPasswordChangeView(PasswordChangeView):
    """Let the logged user change their password, keeping the session."""

    template_name = "users/password_change.html"
    success_url = reverse_lazy("account:profile")

    def form_valid(self, form: PasswordChangeForm) -> HttpResponse:
        """Change the password and confirm it to the user."""
        response = super().form_valid(form)
        messages.success(self.request, "Senha alterada.")
        return response
