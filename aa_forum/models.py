"""
Models
"""

from django.contrib.auth.models import Group, User
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _

from aa_forum.managers import SettingsManager


def get_sentinel_user() -> User:
    """
    Get user or create one
    :return:
    :rtype:
    """

    return User.objects.get_or_create(username="deleted")[0]


def get_slug_on_save(subject: str) -> str:
    """
    Get the slug
    :param subject:
    :type subject:
    :return:
    :rtype:
    """

    run = 0
    subject_slug = slugify(subject, allow_unicode=True)

    while Slugs.objects.filter(slug=subject_slug).exists():
        run += 1
        subject_slug = slugify(subject + "-" + str(run), allow_unicode=True)

    Slugs(slug=subject_slug).save()

    slug_to_return = Slugs.objects.get(slug=subject_slug)

    return slug_to_return


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
            ("basic_access", _("Can access the AA-Forum module")),
            (
                "manage_forum",
                _("Can manage the AA-Forum module (Categories, topics and messages)"),
            ),
        )


class Slugs(models.Model):
    """
    Slugs
    """

    slug = models.SlugField(max_length=255, allow_unicode=True)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Slug")
        verbose_name_plural = _("Slugs")

    @receiver(models.signals.post_delete, sender="aa_forum.Categories")
    def handle_deleted_category(sender, instance, **kwargs):
        """
        Delete category slug, when category is deleted
        :param instance:
        :type instance:
        :param kwargs:
        :type kwargs:
        """

        instance.slug.delete()

    @receiver(models.signals.post_delete, sender="aa_forum.Boards")
    def handle_deleted_board(sender, instance, **kwargs):
        """
        Delete board slug, when board is deleted
        :param instance:
        :type instance:
        :param kwargs:
        :type kwargs:
        """

        instance.slug.delete()

    @receiver(models.signals.post_delete, sender="aa_forum.Topics")
    def handle_deleted_topic(sender, instance, **kwargs):
        """
        Delete topic slug, when topic is deleted
        :param instance:
        :type instance:
        :param kwargs:
        :type kwargs:
        """

        instance.slug.delete()

    def __str__(self) -> str:
        return str(self.slug)


class Categories(models.Model):
    """
    Categories
    """

    name = models.CharField(max_length=254, default="")
    slug = models.ForeignKey(
        Slugs,
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    is_collapsible = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """
        Add the slug on save
        :param force_insert:
        :type force_insert:
        :param force_update:
        :type force_update:
        :param using:
        :type using:
        :param update_fields:
        :type update_fields:
        """

        if self.slug is None or self.slug == "":
            slug = get_slug_on_save(subject=self.name)
            self.slug = slug

        super().save()

    def __str__(self) -> str:
        return str(self.name)


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
    slug = models.ForeignKey(
        Slugs,
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    description = models.TextField(null=True, blank=True)
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
        related_name="aa_forum_boards_group_restriction",
    )
    order = models.IntegerField(default=0)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """
        Add the slug on save
        """

        if self.slug is None or self.slug == "":
            slug = get_slug_on_save(subject=self.name)
            self.slug = slug

        super().save()

    def __str__(self) -> str:
        return str(self.name)

    def latest_topic(self):
        """
        Get the latest topic for this board
        :return:
        :rtype:
        """

        topic = Topics.objects.filter(board=self).order_by("time_modified").last()

        return topic


class Topics(models.Model):
    """
    Topics
    """

    subject = models.CharField(max_length=254, default="")
    slug = models.ForeignKey(
        Slugs,
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    is_sticky = models.BooleanField(
        default=False,
        db_index=True,
    )
    is_locked = models.BooleanField(
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
    time_modified = models.DateTimeField(default=timezone.now)
    read_by = models.ManyToManyField(
        User,
        blank=True,
        related_name="aa_forum_read_topics",
    )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")

        ordering = ["-time_modified"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """
        Add the slug on save
        """

        if self.slug is None or self.slug == "":
            slug = get_slug_on_save(subject=self.subject)
            self.slug = slug

        super().save()

    def first_message(self):
        """
        Get the first message for this topic
        :return:
        :rtype:
        """

        message = Messages.objects.filter(topic=self).first()

        return message

    def last_message(self):
        """
        Get the latest message for this topic
        :return:
        :rtype:
        """

        message = Messages.objects.filter(topic=self).last()

        return message


class Messages(models.Model):
    """
    Messages
    """

    board = models.ForeignKey(
        Boards,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    topic = models.ForeignKey(
        Topics,
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
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
    )
    message = models.TextField(null=True, blank=True)
    read_by = models.ManyToManyField(
        User,
        blank=True,
        related_name="aa_forum_read_messages",
    )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self) -> str:
        return str(self.pk)


class PersonalMessages(models.Model):
    """
    Personal messages
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
    slug = models.ForeignKey(
        Slugs,
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    message = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Personal Message")
        verbose_name_plural = _("Personal Messages")

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """
        Add the slug on save
        """

        if self.slug is None or self.slug == "":
            slug = get_slug_on_save(subject=self.subject)
            self.slug = slug

        super().save()

    def __str__(self) -> str:
        return str(self.subject)


class Settings(models.Model):
    """
    Settings
    """

    variable = models.CharField(
        max_length=254, blank=False, primary_key=True, unique=True
    )
    value = models.TextField(blank=False)

    objects = SettingsManager()

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")
