"""Views shared by the whole site."""

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpResponse

from apps.core.forms import RememberMeAuthenticationForm


class RememberMeLoginView(LoginView):
    """Login that ends the session on browser close unless remembered."""

    form_class = RememberMeAuthenticationForm

    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        """Log the user in and choose how long the session lasts."""
        response = super().form_valid(form)
        if not form.cleaned_data.get("remember"):
            self.request.session.set_expiry(0)
        return response
