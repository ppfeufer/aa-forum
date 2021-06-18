"""
Models
"""

from typing import Optional

from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.dispatch import receiver
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

    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)

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

    name = models.CharField(max_length=254, unique=True)
    slug = models.ForeignKey(Slug, related_name="+", on_delete=models.CASCADE)
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

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Add the slug on save if it does not exist
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        try:
            self.slug
        except ObjectDoesNotExist:
            self.slug = get_slug_on_save(subject=self.name)
        super().save(*args, **kwargs)


class Board(models.Model):
    """
    Board
    """

    category = models.ForeignKey(
        Category, related_name="boards", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=254)

    slug = models.ForeignKey(Slug, related_name="+", on_delete=models.CASCADE)
    description = models.TextField(blank=True)
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
    first_message = models.ForeignKey(
        "Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",
    )
    last_message = models.ForeignKey(
        "Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",
    )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("board")
        verbose_name_plural = _("boards")
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="fpk_board")
        ]

    def __str__(self) -> str:
        return str(self.name)

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Add the slug on save if it does not exist
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        try:
            self.slug
        except ObjectDoesNotExist:
            self.slug = get_slug_on_save(subject=self.name)
        super().save(*args, **kwargs)

    def update_last_message(self) -> Optional[models.Model]:
        """
        Update the last message for this board.
        """

        self.last_message = (
            Message.objects.filter(topic__board=self).order_by("-time_modified").first()
        )
        self.save(update_fields=["last_message"])


class Topic(models.Model):
    """
    Topic
    """

    board = models.ForeignKey(Board, related_name="topics", on_delete=models.CASCADE)
    subject = models.CharField(max_length=254)

    slug = models.ForeignKey(Slug, related_name="+", on_delete=models.CASCADE)
    is_sticky = models.BooleanField(
        default=False,
        db_index=True,
    )
    is_locked = models.BooleanField(
        default=False,
        db_index=True,
    )
    read_by = models.ManyToManyField(
        User,
        blank=True,
        related_name="aa_forum_read_topics",
    )
    first_message = models.ForeignKey(
        "Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",
    )
    last_message = models.ForeignKey(
        "Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",
    )
    last_message_seen = models.ManyToManyField(User, through="LastMessageSeen")

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("topic")
        verbose_name_plural = _("topics")
        constraints = [
            models.UniqueConstraint(fields=["board", "subject"], name="fpk_topic")
        ]

    def __str__(self) -> str:
        return str(self.subject)

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Add the slug on save if it does not exist
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        try:
            self.slug
        except ObjectDoesNotExist:
            self.slug = get_slug_on_save(subject=self.subject)
        super().save(*args, **kwargs)

        update_fields = list()

        if self.board.first_message != self.first_message:
            self.board.first_message = self.first_message
            update_fields.append("first_message")

        if self.board.last_message != self.last_message:
            self.board.last_message = self.last_message
            update_fields.append("last_message")

        if update_fields:
            self.board.save(update_fields=update_fields)

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        """
        On delete
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        board_needs_update = self.last_message = self.board.last_message

        super().delete(*args, **kwargs)

        if board_needs_update:
            self.board.update_last_message()

    def update_last_message(self) -> Optional[models.Model]:
        """
        Updated the last message for this topic.
        """

        self.last_message = (
            Message.objects.filter(topic=self).order_by("-time_modified").first()
        )
        self.save(update_fields=["last_message"])


class LastMessageSeen(models.Model):
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_time = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.topic}-{self.user}-{self.message_time}"


class Message(models.Model):
    """
    Message
    """

    topic = models.ForeignKey(
        Topic,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    time_posted = models.DateTimeField(
        auto_now_add=True
    )  # TODO: Add index with next model update
    time_modified = models.DateTimeField(auto_now=True, db_index=True)
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
    message = models.TextField(blank=True)
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

    @transaction.atomic()
    def save(self, *args, **kwargs) -> None:
        """
        Add the slug on save if it does not exist
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        super().save(*args, **kwargs)

        update_fields = list()

        if not self.topic.first_message:
            self.topic.first_message = self
            update_fields.append("first_message")

        if self.topic.last_message != self:
            self.topic.last_message = self
            update_fields.append("last_message")

        if update_fields:
            self.topic.save(update_fields=update_fields)

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        """
        On delete
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        topic_needs_update = self.topic.last_message == self
        board_needs_update = self.topic.board.last_message == self

        super().delete(*args, **kwargs)

        if topic_needs_update:
            self.topic.update_last_message()

        if board_needs_update:
            self.topic.board.update_last_message()


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
    time_sent = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=254)
    slug = models.ForeignKey(Slug, related_name="+", on_delete=models.CASCADE)
    message = models.TextField(blank=True)
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

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Add the slug on save if it does not exist
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        try:
            self.slug
        except ObjectDoesNotExist:
            self.slug = get_slug_on_save(subject=self.subject)
        super().save(*args, **kwargs)


class Setting(models.Model):
    """
    Setting
    """

    variable = models.CharField(max_length=254, blank=False, unique=True)
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
