# Generated by Django 3.2.4 on 2021-06-22 17:34

import ckeditor_uploader.fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("aa_forum", "0004_topic_new_feature"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="message",
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]