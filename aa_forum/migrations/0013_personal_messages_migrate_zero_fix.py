# Django
from django.db import migrations


def on_migrate(apps, schema_editor):
    """
    Just pass through this one
    :param apps:
    :param schema_editor:
    :return:
    """

    pass


def on_migrate_zero(apps, schema_editor):
    """
    Remove all personal messages before jumping back to 0012
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
