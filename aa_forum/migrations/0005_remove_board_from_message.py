# Generated by Django 3.1.10 on 2021-06-14 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("aa_forum", "0004_singular_model_names"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="board",
        ),
    ]