"""Forms for user accounts."""

from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from apps.users.roles import Role

ROLE_HELP = (
    "Leitor só vê músicas e repertórios. Editor também cadastra, edita e "
    "exclui. Administrador também cadastra usuários."
)


def role_field() -> forms.TypedChoiceField:
    """Return the field used to choose the access level."""
    return forms.TypedChoiceField(
        label="Nível",
        choices=Role.choices,
        coerce=Role,
        initial=Role.READER,
        help_text=ROLE_HELP,
    )


class UserCreateForm(UserCreationForm[User]):
    """Create a user with a password and an access level."""

    role = role_field()

    class Meta:
        """Form options."""

        model = User
        fields = ["username", "first_name"]
        labels = {"username": "Usuário", "first_name": "Nome"}


class UserUpdateForm(forms.ModelForm[User]):
    """Edit a user, optionally setting a new password."""

    role = role_field()
    new_password = forms.CharField(
        label="Nova senha",
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Deixe em branco para manter a senha atual.",
    )

    class Meta:
        """Form options."""

        model = User
        fields = ["username", "first_name", "is_active"]
        labels = {
            "username": "Usuário",
            "first_name": "Nome",
            "is_active": "Ativo",
        }
        help_texts = {
            "username": "",
            "is_active": "Desmarque para impedir o acesso sem apagar o "
            "usuário.",
        }

    def __init__(self, *args: Any, acting_user: User, **kwargs: Any) -> None:
        """Lock the fields that would take away access by mistake."""
        super().__init__(*args, **kwargs)
        if self.instance.is_superuser:
            self.fields["role"].disabled = True
            self.fields["role"].help_text = (
                "Superusuário, sempre administrador."
            )
        if self.instance.pk == acting_user.pk:
            self.fields["role"].disabled = True
            self.fields["is_active"].disabled = True
            self.fields["role"].help_text = (
                "Você não pode mudar o próprio nível nem se desativar."
            )

    def clean_new_password(self) -> str:
        """Check the new password against the password validators."""
        password: str = self.cleaned_data["new_password"]
        if password:
            validate_password(password, self.instance)
        return password

    def save(self, commit: bool = True) -> User:
        """Save the user, replacing the password when a new one was given."""
        user = super().save(commit=False)
        if self.cleaned_data["new_password"]:
            user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm[User]):
    """Let users change the name shown on the site."""

    class Meta:
        """Form options."""

        model = User
        fields = ["first_name"]
        labels = {"first_name": "Nome"}
