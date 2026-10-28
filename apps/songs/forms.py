"""Forms for the songs app."""

from django import forms

from apps.songs.chords import clean_text
from apps.songs.models import Song


class SongForm(forms.ModelForm[Song]):
    """Form used to create and edit songs."""

    class Meta:
        """Form options."""

        model = Song
        fields = ["title", "artist", "key", "content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 24,
                    "class": "sheet-editor",
                    "spellcheck": "false",
                }
            ),
        }

    def clean_content(self) -> str:
        """Store the sheet without the invisible characters of copied text."""
        return clean_text(self.cleaned_data["content"])
