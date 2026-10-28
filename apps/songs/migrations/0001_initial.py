import django.core.validators
import re
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Song",
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
                    "title",
                    models.CharField(max_length=200, verbose_name="título"),
                ),
                (
                    "artist",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="artista"
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        blank=True,
                        help_text="Ex.: G, F#, Bb, Am.",
                        max_length=4,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Informe um tom válido, como G, F#, Bb ou Am.",
                                regex=re.compile(
                                    "^(?P<root>[A-G][#b]?)(?P<minor>m?)$"
                                ),
                            )
                        ],
                        verbose_name="tom original",
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        help_text="Cole a cifra com os acordes na linha acima da letra.",
                        verbose_name="cifra",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="criada em"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="atualizada em"
                    ),
                ),
            ],
            options={
                "verbose_name": "música",
                "verbose_name_plural": "músicas",
                "ordering": ["title"],
            },
        ),
    ]
