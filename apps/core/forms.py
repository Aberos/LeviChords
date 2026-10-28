"""Forms shared by the whole site."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm


class RememberMeAuthenticationForm(AuthenticationForm):
    """Login form with the option to keep the session after closing."""

    remember = forms.BooleanField(label="Lembrar de mim", required=False)
