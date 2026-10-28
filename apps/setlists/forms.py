"""Forms for the setlists app."""

from typing import Any, cast

from django import forms

from apps.setlists.models import Setlist, SetlistItem
from apps.songs.chords import MAX_SEMITONES, MIN_SEMITONES

UNSET_POSITION = 10_000

SEMITONE_CHOICES = [
    (value, f"{value:+d}" if value else "0 (original)")
    for value in range(MIN_SEMITONES, MAX_SEMITONES + 1)
]


class SetlistForm(forms.ModelForm[Setlist]):
    """Form used to create and edit the setlist header."""

    class Meta:
        """Form options."""

        model = Setlist
        fields = ["date", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class SetlistItemForm(forms.ModelForm[SetlistItem]):
    """Form for one song of the setlist."""

    semitones = forms.TypedChoiceField(
        label="Transposição",
        choices=SEMITONE_CHOICES,
        coerce=int,
        initial=0,
    )

    class Meta:
        """Form options."""

        model = SetlistItem
        fields = ["song", "position", "semitones"]
        widgets = {"position": forms.HiddenInput()}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Make the position optional, since it is filled by the page."""
        super().__init__(*args, **kwargs)
        self.fields["position"].required = False

    def has_changed(self) -> bool:
        """Ignore the position, so empty rows stay empty."""
        return any(name != "position" for name in self.changed_data)


class BaseSetlistItemFormSet(
    forms.BaseInlineFormSet[SetlistItem, Setlist, SetlistItemForm]
):
    """Inline formset that stores the songs in the chosen order."""

    def save_in_order(self) -> list[SetlistItem]:
        """Save the items, renumbering their positions from one."""
        self.save(commit=False)
        for removed in self.deleted_objects:
            removed.delete()
        kept = [
            form
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE")
        ]
        kept.sort(
            key=lambda form: form.cleaned_data["position"] or UNSET_POSITION
        )
        items: list[SetlistItem] = []
        for number, form in enumerate(kept, start=1):
            item = form.instance
            item.position = number
            item.save()
            items.append(item)
        return items


SetlistItemFormSet = cast(
    type[BaseSetlistItemFormSet],
    forms.inlineformset_factory(
        Setlist,
        SetlistItem,
        form=SetlistItemForm,
        formset=BaseSetlistItemFormSet,
        extra=3,
        can_delete=True,
    ),
)
