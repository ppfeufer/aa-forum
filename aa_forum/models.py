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

    while Slug.objects.filter(slug=subject_slug).exists():
        run += 1
        subject_slug = slugify(subject + "-" + str(run), allow_unicode=True)

    Slug(slug=subject_slug).save()

    slug_to_return = Slug.objects.get(slug=subject_slug)

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
                _("Can manage the AA-Forum module (Category, topics and messages)"),
            ),
        )


class Slug(models.Model):
    """
    Slug
    """

    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("slug")
        verbose_name_plural = _("slugs")

    @receiver(models.signals.post_delete, sender="aa_forum.Category")
    def handle_deleted_category(sender, instance, **kwargs):
        """
        Delete category slug, when category is deleted
        :param instance:
        :type instance:
        :param kwargs:
        :type kwargs:
        """

        instance.slug.delete()

    @receiver(models.signals.post_delete, sender="aa_forum.Board")
    def handle_deleted_board(sender, instance, **kwargs):
        """
        Delete board slug, when board is deleted
        :param instance:
        :type instance:
        :param kwargs:
        :type kwargs:
        """

        instance.slug.delete()

    @receiver(models.signals.post_delete, sender="aa_forum.Topic")
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


class Category(models.Model):
    """
    Category
    """

    name = models.CharField(max_length=254, default="")
    slug = models.ForeignKey(
        Slug,
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    is_collapsible = models.BooleanField(default=False)
    order = models.IntegerField(default=0, db_index=True)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self) -> str:
        return str(self.name)

    def save(self, *args, **kwargs):
        # Add the slug on save
        if not self.slug:
            slug = get_slug_on_save(subject=self.name)
            self.slug = slug
        super().save(*args, **kwargs)


class Board(models.Model):
    """
    Board
    """

    category = models.ForeignKey(
        Category,
        related_name="boards",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=254, default="")
    slug = models.ForeignKey(
        Slug,
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
        verbose_name = _("board")
        verbose_name_plural = _("boards")

    def __str__(self) -> str:
        return str(self.name)

    def save(self, *args, **kwargs):
        # Add the slug on save
        if not self.slug:
            slug = get_slug_on_save(subject=self.name)
            self.slug = slug
        super().save(*args, **kwargs)

    # def last_message(self) -> "Message":
    #     """Return the last posted message for this board."""
    #     return (
    #         Message.objects.filter(topic__board=self)
    #         .select_related("topic", "user_created__profile__main_character")
    #         .order_by("-time_modified")[0]
    #     )


class Topic(models.Model):
    """
    Topic
    """

    subject = models.CharField(max_length=254, default="")
    slug = models.ForeignKey(
        Slug,
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
        Board,
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
    time_modified = models.DateTimeField(default=timezone.now, db_index=True)
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
        verbose_name = _("topic")
        verbose_name_plural = _("topics")

        ordering = ["-time_modified"]

    def __str__(self) -> str:
        return str(self.subject)

    def save(self, *args, **kwargs):
        # Add the slug on save
        if not self.slug:
            slug = get_slug_on_save(subject=self.subject)
            self.slug = slug
        super().save(*args, **kwargs)

    def first_message(self):
        """
        Get the first message for this topic
        :return:
        :rtype:
        """

        message = self.messages.order_by("time_modified")[0]
        return message

    # def last_message(self):
    #     """
    #     Get the latest message for this topic
    #     :return:
    #     :rtype:
    #     """

    #     message = self.messages.select_related(
    #         "user_created__profile__main_character"
    #     ).order_by("-time_modified")[0]

    #     return message


class Message(models.Model):
    """
    Message
    """

    topic = models.ForeignKey(
        Topic,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    time_posted = models.DateTimeField(default=timezone.now)
    time_modified = models.DateTimeField(default=timezone.now, db_index=True)
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
        verbose_name = _("message")
        verbose_name_plural = _("messages")

    def __str__(self) -> str:
        return str(self.pk)


class PersonalMessage(models.Model):
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
        Slug,
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
        verbose_name = _("personal message")
        verbose_name_plural = _("personal messages")

    def __str__(self) -> str:
        return str(self.subject)

    def save(self, *args, **kwargs):
        # Add the slug on save
        if not self.slug:
            slug = get_slug_on_save(subject=self.subject)
            self.slug = slug
        super().save(*args, **kwargs)


class Setting(models.Model):
    """
    Setting
    """

    variable = models.CharField(
        max_length=254, blank=False, primary_key=True, unique=True
    )
    value = models.TextField(blank=False)

    objects = SettingsManager()

    def __str__(self) -> str:
        return self.variable

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("setting")
        verbose_name_plural = _("settings")
