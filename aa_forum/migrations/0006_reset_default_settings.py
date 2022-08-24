# Django
from django.db import migrations

default_settings_to_migrate = [
    {"variable": "defaultMaxMessages", "value": "15"},
    {"variable": "defaultMaxTopics", "value": "20"},
]


def on_migrate(apps, schema_editor):
    """
    Remove default settings on migration
    :param apps:
    :param schema_editor:
    :return:
    """

    Setting = apps.get_model("aa_forum", "Setting")
    db_alias = schema_editor.connection.alias

    for default_setting in default_settings_to_migrate:
        Setting.objects.using(db_alias).filter(
            variable=default_setting["variable"]
        ).delete()


def on_migrate_zero(apps, schema_editor):
    """
    Add default settings on migration to zero
    :param apps:
    :param schema_editor:
    :return:
    """

    Setting = apps.get_model("aa_forum", "Setting")
    db_alias = schema_editor.connection.alias
    default_settings = [
        Setting(variable=default_setting["variable"], value=default_setting["value"])
        for default_setting in default_settings_to_migrate
    ]
    Setting.objects.using(db_alias).bulk_create(default_settings)


class Migration(migrations.Migration):

    dependencies = [
        ("aa_forum", "0005_announcement_boards"),
    ]

    operations = [migrations.RunPython(on_migrate, on_migrate_zero)]
