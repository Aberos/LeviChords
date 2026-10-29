"""Give the editor level to the users created before the access levels."""

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

EDITOR_GROUP = "Editor"


def existing_users_as_editors(
    apps: Apps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    """Keep the users that could already edit everything as editors."""
    group_model = apps.get_model("auth", "Group")
    user_model = apps.get_model("auth", "User")
    editor, _ = group_model.objects.get_or_create(name=EDITOR_GROUP)
    users = user_model.objects.filter(is_superuser=False, groups=None)
    editor.user_set.add(*users)


class Migration(migrations.Migration):
    """Data migration for the users created before the access levels."""

    dependencies = [("auth", "0012_alter_user_first_name_max_length")]

    operations = [
        migrations.RunPython(
            existing_users_as_editors, migrations.RunPython.noop
        ),
    ]
