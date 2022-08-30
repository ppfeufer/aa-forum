# Django
from django.db import migrations


def on_migrate(apps, schema_editor):
    """
    Remove default settings on migration
    :param apps:
    :param schema_editor:
    :return:
    """

    pass


def on_migrate_zero(apps, schema_editor):
    """
    Add default settings on migration to zero
    :param apps:
    :param schema_editor:
    :return:
    """

    PersonalMessage = apps.get_model("aa_forum", "PersonalMessage")
    db_alias = schema_editor.connection.alias
    PersonalMessage.objects.using(db_alias).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("aa_forum", "0012_personal_messages"),
    ]

    operations = [migrations.RunPython(on_migrate, on_migrate_zero)]
