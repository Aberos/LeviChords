"""Helpers for pages that replace only a fragment without reloading."""

from django.http import HttpRequest

PARTIAL_PARAMETER = "parcial"


def is_partial(request: HttpRequest) -> bool:
    """Tell whether the page asked only for a fragment to replace."""
    return PARTIAL_PARAMETER in request.GET
