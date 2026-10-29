"""Views for the songs app."""

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.core.partials import is_partial
from apps.songs.forms import SongForm
from apps.songs.models import Song
from apps.songs.repository import SongRepository
from apps.songs.services import SongService


class SongListView(PermissionRequiredMixin, ListView[Song]):
    """List songs, optionally filtered by a search term."""

    permission_required = "songs.view_song"
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


class SongDetailView(PermissionRequiredMixin, DetailView[Song]):
    """Show a song in reading mode, transposed by ``semitons``."""

    permission_required = "songs.view_song"
    model = Song
    template_name = "songs/song_detail.html"
    context_object_name = "song"

    def get_template_names(self) -> list[str]:
        """Return only the sheet fragment when the page asks for it."""
        if is_partial(self.request):
            return ["songs/song_reader.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the transposed sheet to the context."""
        context = super().get_context_data(**kwargs)
        semitones = SongService.parse_semitones(
            self.request.GET.get("semitons")
        )
        context["sheet"] = SongService.build_sheet(self.object, semitones)
        context["restore_semitones"] = 0
        context["restore_label"] = "original"
        context["restore_key"] = self.object.key
        return context


def render_preview(
    view: CreateView[Song, SongForm] | UpdateView[Song, SongForm],
) -> HttpResponse:
    """Show the posted sheet colored, without validating or saving it."""
    data = view.request.POST
    preview = SongService.preview(data.get("content", ""))
    if is_partial(view.request):
        return render(
            view.request, "songs/song_preview.html", {"preview": preview}
        )
    form = view.get_form_class()(initial=data.dict(), instance=view.object)
    return view.render_to_response(
        view.get_context_data(form=form, preview=preview)
    )


class SongCreateView(
    PermissionRequiredMixin,
    SuccessMessageMixin[SongForm],
    CreateView[Song, SongForm],
):
    """Create a song, with a preview that does not save it."""

    permission_required = "songs.add_song"
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
    PermissionRequiredMixin,
    SuccessMessageMixin[SongForm],
    UpdateView[Song, SongForm],
):
    """Edit a song, with a preview that does not save it."""

    permission_required = "songs.change_song"
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


class SongDeleteView(PermissionRequiredMixin, DeleteView[Song, Form]):
    """Delete a song that is not used by any setlist."""

    permission_required = "songs.delete_song"
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
