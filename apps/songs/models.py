"""Models for songs and their chord sheets."""

from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

from apps.songs.chords import KEY_PATTERN

key_validator = RegexValidator(
    regex=KEY_PATTERN,
    message="Informe um tom válido, como G, F#, Bb ou Am.",
)


class Song(models.Model):
    """Represent a song with its chord sheet as plain text."""

    title = models.CharField("título", max_length=200)
    artist = models.CharField("artista", max_length=200, blank=True)
    key = models.CharField(
        "tom original",
        max_length=4,
        blank=True,
        validators=[key_validator],
        help_text="Ex.: G, F#, Bb, Am.",
    )
    content = models.TextField(
        "cifra",
        help_text="Cole a cifra com os acordes na linha acima da letra.",
    )
    created_at = models.DateTimeField("criada em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizada em", auto_now=True)

    class Meta:
        """Model options."""

        ordering = ["title"]
        verbose_name = "música"
        verbose_name_plural = "músicas"

    def __str__(self) -> str:
        """Return the title followed by the artist, when present."""
        if self.artist:
            return f"{self.title} ({self.artist})"
        return str(self.title)

    def get_absolute_url(self) -> str:
        """Return the URL of the song reading page."""
        return reverse("songs:detail", kwargs={"pk": self.pk})
