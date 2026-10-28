"""Views for the songs app."""

from typing import Any

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.songs.forms import SongForm
from apps.songs.models import Song
from apps.songs.repository import SongRepository
from apps.songs.services import SongService


class SongListView(ListView[Song]):
    """List songs, optionally filtered by a search term."""

    template_name = "songs/song_list.html"
    context_object_name = "songs"
    paginate_by = 50

    def get_queryset(self) -> QuerySet[Song]:
        """Return the songs matching the ``q`` parameter."""
        return SongRepository.search(self.request.GET.get("q", ""))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the search term to the context."""
        context = super().get_context_data(**kwargs)
        context["term"] = self.request.GET.get("q", "").strip()
        return context


class SongDetailView(DetailView[Song]):
    """Show a song in reading mode, transposed by ``semitons``."""

    model = Song
    template_name = "songs/song_detail.html"
    context_object_name = "song"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the transposed sheet to the context."""
        context = super().get_context_data(**kwargs)
        semitones = SongService.parse_semitones(
            self.request.GET.get("semitons")
        )
        context["sheet"] = SongService.build_sheet(self.object, semitones)
        return context


def render_preview(
    view: CreateView[Song, SongForm] | UpdateView[Song, SongForm],
) -> HttpResponse:
    """Show the posted sheet colored, without validating or saving it."""
    data = view.request.POST
    form = view.get_form_class()(initial=data.dict(), instance=view.object)
    preview = SongService.preview(data.get("content", ""))
    return view.render_to_response(
        view.get_context_data(form=form, preview=preview)
    )


class SongCreateView(
    SuccessMessageMixin[SongForm],
    CreateView[Song, SongForm],
):
    """Create a song, with a preview that does not save it."""

    model = Song
    form_class = SongForm
    template_name = "songs/song_form.html"
    success_message = "Música salva."

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Save the song, or only preview it when asked."""
        if "preview" in request.POST:
            self.object = None
            return render_preview(self)
        return super().post(request, *args, **kwargs)


class SongUpdateView(
    SuccessMessageMixin[SongForm],
    UpdateView[Song, SongForm],
):
    """Edit a song, with a preview that does not save it."""

    model = Song
    form_class = SongForm
    template_name = "songs/song_form.html"
    success_message = "Música atualizada."

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        """Save the changes, or only preview them when asked."""
        if "preview" in request.POST:
            self.object = self.get_object()
            return render_preview(self)
        return super().post(request, *args, **kwargs)


class SongDeleteView(DeleteView[Song, Form]):
    """Delete a song that is not used by any setlist."""

    model = Song
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("songs:list")

    def form_valid(self, form: Form) -> HttpResponse:
        """Delete the song or explain why it is protected."""
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Esta música está em um repertório e não pode ser excluída.",
            )
            return redirect(self.object)
        messages.success(self.request, "Música excluída.")
        return response
