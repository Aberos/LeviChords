"""Models for setlists and their ordered songs."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from apps.songs.chords import MAX_SEMITONES, MIN_SEMITONES, transpose_key
from apps.songs.models import Song


class Setlist(models.Model):
    """Represent the songs planned for a service."""

    date = models.DateField("data")
    description = models.CharField(
        "descrição",
        max_length=200,
        blank=True,
        help_text="Ex.: Culto da manhã.",
    )
    songs = models.ManyToManyField(
        Song,
        through="SetlistItem",
        related_name="setlists",
        verbose_name="músicas",
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        """Model options."""

        ordering = ["-date", "-pk"]
        verbose_name = "repertório"
        verbose_name_plural = "repertórios"

    def __str__(self) -> str:
        """Return the date followed by the description, when present."""
        date = self.date.strftime("%d/%m/%Y")
        if self.description:
            return f"{date} – {self.description}"
        return date

    def get_absolute_url(self) -> str:
        """Return the URL of the setlist reading page."""
        return reverse("setlists:detail", kwargs={"pk": self.pk})


class SetlistItem(models.Model):
    """Represent a song placed in a setlist position and key."""

    setlist = models.ForeignKey(
        Setlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="repertório",
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.PROTECT,
        related_name="setlist_items",
        verbose_name="música",
    )
    position = models.PositiveSmallIntegerField("posição", default=0)
    semitones = models.SmallIntegerField(
        "transposição",
        default=0,
        validators=[
            MinValueValidator(MIN_SEMITONES),
            MaxValueValidator(MAX_SEMITONES),
        ],
        help_text="Semitons em relação ao tom original.",
    )

    class Meta:
        """Model options."""

        ordering = ["position", "pk"]
        verbose_name = "música do repertório"
        verbose_name_plural = "músicas do repertório"

    def __str__(self) -> str:
        """Return the position followed by the song."""
        return f"{self.position}. {self.song}"

    @property
    def key(self) -> str:
        """Return the key the song is played in this setlist."""
        if not self.song.key:
            return ""
        return transpose_key(self.song.key, self.semitones)
