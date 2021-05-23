"""
Models
"""

from django.contrib.auth.models import Group, User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


def get_sentinel_user() -> User:
    """
    get user or create one
    :return:
    :rtype:
    """

    return User.objects.get_or_create(username="deleted")[0]


class General(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:
        """
        Meta definitions
        """

        verbose_name = "AA-Forum"
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access the AA-SRP module"),
            ("manage_forum", "Can manage the forum (Categories, topics and messages)"),
        )


class Categories(models.Model):
    """
    Categories
    """

    name = models.CharField(max_length=254, default="")
    order = models.IntegerField(default=0)
    collapsible = models.BooleanField(default=False)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Boards(models.Model):
    """
    Boards
    """

    category = models.ForeignKey(
        Categories,
        related_name="boards",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=254, default="")
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0)
    parent_board = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="child_boards",
        on_delete=models.CASCADE,
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="aa_forum_boards",
    )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")


class Topics(models.Model):
    """
    Topics
    """

    sticky = models.BooleanField(
        default=False,
        db_index=True,
    )
    locked = models.BooleanField(
        default=False,
        db_index=True,
    )
    board = models.ForeignKey(
        Boards,
        related_name="topics",
        on_delete=models.CASCADE,
    )
    user_started = models.ForeignKey(
        User,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
    )
    user_updated = models.ForeignKey(
        User,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
    )
    num_views = models.IntegerField(default=0)
    num_replies = models.IntegerField(default=0)
    first_message = models.ForeignKey(
        "Messages",
        related_name="+",
        on_delete=models.CASCADE,
    )
    last_message = models.ForeignKey(
        "Messages",
        related_name="+",
        on_delete=models.CASCADE,
    )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")


class Messages(models.Model):
    """
    Messages
    """

    topic = models.ForeignKey(
        Topics,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    board = models.ForeignKey(
        Boards,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    time_posted = models.DateTimeField(default=timezone.now)
    time_modified = models.DateTimeField(default=timezone.now)
    user_created = models.ForeignKey(
        User,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
    )
    user_updated = models.ForeignKey(
        User,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
    )
    subject = models.CharField(max_length=254, default="")
    message = models.TextField(null=True, blank=True)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")


class PersonalMessages(models.Model):
    """
    PersonalMessages
    """

    sender = models.ForeignKey(
        User,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
    )
    recipient = models.ForeignKey(
        User,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
    )
    time_sent = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=254, default="")
    message = models.TextField(null=True, blank=True)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Personal Message")
        verbose_name_plural = _("Personal Messages")
