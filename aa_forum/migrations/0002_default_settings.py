# Django
from django.db import migrations

default_settings_to_migrate = [
    {"variable": "defaultMaxMessages", "value": "15"},
    {"variable": "defaultMaxTopics", "value": "20"},
]


def on_migrate(apps, schema_editor):
    """
    Add default settings on migration
    :param apps:
    :type apps:
    :param schema_editor:
    :type schema_editor:
    """

    Setting = apps.get_model("aa_forum", "Setting")
    db_alias = schema_editor.connection.alias
    default_settings = [
        Setting(variable=default_setting["variable"], value=default_setting["value"])
        for default_setting in default_settings_to_migrate
    ]
    Setting.objects.using(db_alias).bulk_create(default_settings)


def on_migrate_zero(apps, schema_editor):
    """
    Remove default settings on migration to zero
    :param apps:
    :type apps:
    :param schema_editor:
    :type schema_editor:
    """

    Setting = apps.get_model("aa_forum", "Setting")
    db_alias = schema_editor.connection.alias

    for default_setting in default_settings_to_migrate:
        Setting.objects.using(db_alias).filter(
            variable=default_setting["variable"]
        ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("aa_forum", "0001_initial"),
    ]

    operations = [migrations.RunPython(on_migrate, on_migrate_zero)]
