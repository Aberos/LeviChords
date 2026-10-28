import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("songs", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Setlist",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField(verbose_name="data")),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        help_text="Ex.: Culto da manhã.",
                        max_length=200,
                        verbose_name="descrição",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="criado em"
                    ),
                ),
            ],
            options={
                "verbose_name": "repertório",
                "verbose_name_plural": "repertórios",
                "ordering": ["-date", "-pk"],
            },
        ),
        migrations.CreateModel(
            name="SetlistItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "position",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="posição"
                    ),
                ),
                (
                    "semitones",
                    models.SmallIntegerField(
                        default=0,
                        help_text="Semitons em relação ao tom original.",
                        validators=[
                            django.core.validators.MinValueValidator(-5),
                            django.core.validators.MaxValueValidator(6),
                        ],
                        verbose_name="transposição",
                    ),
                ),
                (
                    "setlist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="setlists.setlist",
                        verbose_name="repertório",
                    ),
                ),
                (
                    "song",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="setlist_items",
                        to="songs.song",
                        verbose_name="música",
                    ),
                ),
            ],
            options={
                "verbose_name": "música do repertório",
                "verbose_name_plural": "músicas do repertório",
                "ordering": ["position", "pk"],
            },
        ),
        migrations.AddField(
            model_name="setlist",
            name="songs",
            field=models.ManyToManyField(
                related_name="setlists",
                through="setlists.SetlistItem",
                to="songs.song",
                verbose_name="músicas",
            ),
        ),
    ]
