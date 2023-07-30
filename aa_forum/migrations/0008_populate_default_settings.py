# Django
from django.db import migrations

default_settings_to_migrate = [
    {"variable": "defaultMaxMessages", "value": "15"},
    {"variable": "defaultMaxTopics", "value": "20"},
]


def on_migrate(apps, schema_editor):
    """
    Create default settings on migration
    :param apps:
    :param schema_editor:
    :return:
    """

    Setting = apps.get_model("aa_forum", "Setting")
    db_alias = schema_editor.connection.alias

    Setting.objects.using(db_alias).create(pk=1)


def on_migrate_zero(apps, schema_editor):
    """
    Remove default settings on migratio to zero
    :param apps:
    :param schema_editor:
    :return:
    """

    Setting = apps.get_model("aa_forum", "Setting")
    db_alias = schema_editor.connection.alias
    Setting.objects.using(db_alias).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("aa_forum", "0007_change_settings_to_singleton"),
    ]

    operations = [migrations.RunPython(on_migrate, on_migrate_zero)]
