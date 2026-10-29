"""Views for the setlists app."""

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.forms import Form
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)

from apps.core.partials import is_partial
from apps.setlists.forms import SetlistForm, SetlistItemFormSet
from apps.setlists.models import Setlist
from apps.setlists.repository import SetlistRepository
from apps.setlists.services import SetlistService
from apps.songs.services import SongService


class HomeRedirectView(RedirectView):
    """Open the next setlist, or the list when none is scheduled."""

    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str:
        """Return the URL of the next setlist."""
        setlist = SetlistRepository.next_from(timezone.localdate())
        if setlist is None:
            return reverse("setlists:list")
        return setlist.get_absolute_url()


class SetlistListView(PermissionRequiredMixin, ListView[Setlist]):
    """List setlists, newest first."""

    permission_required = "setlists.view_setlist"
    template_name = "setlists/setlist_list.html"
    context_object_name = "setlists"
    paginate_by = 20

    def get_queryset(self) -> QuerySet[Setlist]:
        """Return the setlists with their song count."""
        return SetlistRepository.list_with_song_count()


class SetlistDetailView(PermissionRequiredMixin, DetailView[Setlist]):
    """Show the songs of a setlist, each one opening on its own page."""

    permission_required = "setlists.view_setlist"
    template_name = "setlists/setlist_detail.html"
    context_object_name = "setlist"

    def get_queryset(self) -> QuerySet[Setlist]:
        """Return setlists with their songs prefetched."""
        return SetlistRepository.with_songs()


class SetlistSongView(PermissionRequiredMixin, DetailView[Setlist]):
    """Show a single song of a setlist in reading mode."""

    permission_required = "setlists.view_setlist"
    template_name = "setlists/setlist_song.html"
    context_object_name = "setlist"

    def get_queryset(self) -> QuerySet[Setlist]:
        """Return setlists with their songs prefetched."""
        return SetlistRepository.with_songs()

    def get_template_names(self) -> list[str]:
        """Return only the sheet fragment when the page asks for it."""
        if is_partial(self.request):
            return ["songs/song_reader.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the chosen song, transposed by ``semitons`` if given."""
        context = super().get_context_data(**kwargs)
        raw = self.request.GET.get("semitons")
        semitones = None if raw is None else SongService.parse_semitones(raw)
        current = SetlistService.open_song(
            self.object, self.kwargs["number"], semitones
        )
        if current is None:
            raise Http404("Música não encontrada no repertório.")
        context["current"] = current
        context["song"] = current.item.song
        context["sheet"] = current.sheet
        context["restore_semitones"] = current.item.semitones
        context["restore_label"] = "no repertório"
        context["restore_key"] = current.item.key
        return context


class SetlistEditView(
    PermissionRequiredMixin, UpdateView[Setlist, SetlistForm]
):
    """Create or edit a setlist together with its ordered songs."""

    model = Setlist
    form_class = SetlistForm
    template_name = "setlists/setlist_form.html"

    def get_permission_required(self) -> tuple[str, ...]:
        """Require the add permission to create and change to edit."""
        if "pk" not in self.kwargs:
            return ("setlists.add_setlist",)
        return ("setlists.change_setlist",)

    def get_object(self, queryset: QuerySet[Setlist] | None = None) -> Setlist:
        """Return the setlist being edited, or a new one without ``pk``."""
        if "pk" not in self.kwargs:
            return Setlist()
        return super().get_object(queryset)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add the songs formset to the context."""
        if "formset" not in kwargs:
            kwargs["formset"] = SetlistItemFormSet(instance=self.object)
        return super().get_context_data(**kwargs)

    def form_valid(self, form: SetlistForm) -> HttpResponse:
        """Save the setlist only when every song row is valid."""
        formset = SetlistItemFormSet(self.request.POST, instance=form.instance)
        if not formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, formset=formset)
            )
        self.object = SetlistService.save(form, formset)
        messages.success(self.request, "Repertório salvo.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form: SetlistForm) -> HttpResponse:
        """Show the form again, keeping the song rows filled."""
        formset = SetlistItemFormSet(self.request.POST, instance=form.instance)
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


class SetlistDeleteView(PermissionRequiredMixin, DeleteView[Setlist, Form]):
    """Delete a setlist, keeping its songs."""

    permission_required = "setlists.delete_setlist"
    model = Setlist
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("setlists:list")

    def form_valid(self, form: Form) -> HttpResponse:
        """Delete the setlist and confirm it to the user."""
        response = super().form_valid(form)
        messages.success(self.request, "Repertório excluído.")
        return response
