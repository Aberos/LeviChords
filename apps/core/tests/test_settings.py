"""Tests for the database configuration read from the environment."""

from config.settings import database_from_url


def test_database_from_url_reads_every_part() -> None:
    """A Render-style URL fills name, user, password, host and port."""
    database = database_from_url(
        "postgresql://levi:s3nh%40forte@dpg-abc.oregon-postgres.render.com"
        ":6543/levichords"
    )

    assert database == {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "levichords",
        "USER": "levi",
        "PASSWORD": "s3nh@forte",
        "HOST": "dpg-abc.oregon-postgres.render.com",
        "PORT": "6543",
    }


def test_database_from_url_uses_default_port() -> None:
    """Without a port in the URL, PostgreSQL's default port is used."""
    database = database_from_url("postgresql://levi:senha@dpg-abc/levichords")

    assert database["HOST"] == "dpg-abc"
    assert database["PORT"] == "5432"
