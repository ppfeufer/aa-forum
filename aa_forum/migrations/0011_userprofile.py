# Generated by Django 4.0.7 on 2022-08-25 22:20

# Django
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

# ckEditor
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("aa_forum", "0010_better_setting_names"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="aa_forum_user_profile",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "signature",
                    ckeditor_uploader.fields.RichTextUploadingField(blank=True),
                ),
                ("website_title", models.CharField(blank=True, max_length=254)),
                ("website_url", models.CharField(blank=True, max_length=254)),
            ],
            options={
                "verbose_name": "user profile",
                "verbose_name_plural": "user profiles",
                "default_permissions": (),
            },
        ),
    ]
