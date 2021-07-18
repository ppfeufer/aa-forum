"""
Models
"""

import math

from ckeditor_uploader.fields import RichTextUploadingField

from django.contrib.auth.models import Group, User
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from aa_forum.constants import INTERNAL_URL_PREFIX, SETTING_MESSAGESPERPAGE
from aa_forum.managers import (
    BoardManager,
    MessageManager,
    SettingsManager,
    TopicManager,
)


def get_sentinel_user() -> User:
    """
    Get user or create one
    :return:
    :rtype:
    """

    return User.objects.get_or_create(username="deleted")[0]


def _generate_slug(MyModel: models.Model, name: str) -> str:
    """
    Generate a valid slug and return it.
    :param MyModel:
    :type MyModel:
    :param name:
    :type name:
    :return:
    :rtype:
    """

    if name == INTERNAL_URL_PREFIX:
        name = "hyphen"

    run = 0
    slug_name = slugify(name, allow_unicode=True)

    while MyModel.objects.filter(slug=slug_name).exists():
        run += 1
        slug_name = slugify(f"{name}-{run}", allow_unicode=True)

    return slug_name


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


class Category(models.Model):
    """
    Category
    """

    name = models.CharField(max_length=254, unique=True)
    slug = models.SlugField(max_length=254, unique=True, allow_unicode=True)
    is_collapsible = models.BooleanField(default=False)
    order = models.IntegerField(default=999999, db_index=True)

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
        Generates the slug.
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        if self._state.adding is True or self.slug == INTERNAL_URL_PREFIX:
            self.slug = _generate_slug(type(self), self.name)

        super().save(*args, **kwargs)


class Board(models.Model):
    """
    Board
    """

    category = models.ForeignKey(
        Category, related_name="boards", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=254)

    slug = models.SlugField(max_length=254, unique=True, allow_unicode=True)
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
    order = models.IntegerField(default=999999, db_index=True)
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

    objects = BoardManager()

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
        Generates the slug.
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        if self._state.adding is True or self.slug == INTERNAL_URL_PREFIX:
            self.slug = _generate_slug(type(self), self.name)

        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """
        Calculate URL for this board and return it.
        """

        return reverse("aa_forum:forum_board", args=[self.category.slug, self.slug])

    def update_last_message(self):
        """
        Update the last message for this board.
        """

        self.last_message = (
            Message.objects.filter(topic__board=self).order_by("-time_posted").first()
        )
        self.save(update_fields=["last_message"])


class Topic(models.Model):
    """
    Topic
    """

    board = models.ForeignKey(Board, related_name="topics", on_delete=models.CASCADE)
    subject = models.CharField(max_length=254)

    slug = models.SlugField(max_length=254, unique=True, allow_unicode=True)
    is_sticky = models.BooleanField(
        default=False,
        db_index=True,
    )
    is_locked = models.BooleanField(
        default=False,
        db_index=True,
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

    objects = TopicManager()

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
        Generate slug for new objects and update first and last messages.
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        if self._state.adding is True or self.slug == INTERNAL_URL_PREFIX:
            self.slug = _generate_slug(type(self), self.subject)

        super().save(*args, **kwargs)

        try:
            self.board.first_message = self.first_message
        except Message.DoesNotExist:
            self.board.first_message = None

        try:
            self.board.last_message = self.last_message
        except Message.DoesNotExist:
            self.board.last_message = None

        self.board.save(update_fields=["first_message", "last_message"])

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

    def get_absolute_url(self) -> str:
        """
        Calculate URL for this topic and return it.
        """

        return reverse(
            "aa_forum:forum_topic",
            args=[self.board.category.slug, self.board.slug, self.slug],
        )

    def update_last_message(self):
        """
        Update the last message for this topic.
        """

        self.last_message = (
            Message.objects.filter(topic=self).order_by("-time_posted").first()
        )
        self.save(update_fields=["last_message"])


class LastMessageSeen(models.Model):
    """
    Stores information about the last message seen by a user in a topic.
    """

    topic = models.ForeignKey("Topic", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_time = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.topic}-{self.user}-{self.message_time}"

    class Meta:
        default_permissions = ()
        indexes = [
            models.Index(
                fields=["topic", "user", "message_time"],
                name="lastmessageseen_compounded",
            ),
        ]


class Message(models.Model):
    """
    Message
    """

    topic = models.ForeignKey(
        Topic,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    time_posted = models.DateTimeField(auto_now_add=True, db_index=True)
    time_modified = models.DateTimeField(auto_now=True)
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
    message = RichTextUploadingField(blank=False)
    message_plaintext = models.TextField(blank=True)

    objects = MessageManager()

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

        self.message_plaintext = strip_tags(self.message)
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

    def get_absolute_url(self):
        """
        Calculate URL for this message and return it.
        """

        messages_per_topic = int(
            Setting.objects.get_setting(setting_key=SETTING_MESSAGESPERPAGE)
        )
        position = (
            self.topic.messages.order_by("time_posted")
            .filter(time_posted__lt=self.time_posted)
            .count()
        ) + 1

        page = math.ceil(position / messages_per_topic)

        if page > 1:
            redirect_path = reverse(
                "aa_forum:forum_topic",
                args=(
                    self.topic.board.category.slug,
                    self.topic.board.slug,
                    self.topic.slug,
                    page,
                ),
            )
        else:
            redirect_path = reverse(
                "aa_forum:forum_topic",
                args=(
                    self.topic.board.category.slug,
                    self.topic.board.slug,
                    self.topic.slug,
                ),
            )

        return f"{redirect_path}#message-{self.pk}"


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
    slug = models.SlugField(max_length=254, unique=True, allow_unicode=True)
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
        Generates the slug.
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        if self._state.adding is True or self.slug == INTERNAL_URL_PREFIX:
            self.slug = _generate_slug(type(self), self.subject)

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


@receiver(post_save, sender=Board)
def sync_parent_board_access_to_child_board(sender, instance, **kwargs):
    """
    Keeps the access restrictions in sync between parent boards and their children
    """

    if instance.parent_board:
        parent_board = Board.objects.get(pk=instance.parent_board.pk)

        instance.groups.set(parent_board.groups.all())
    else:
        child_boards = instance.child_boards.all()

        for child_board in child_boards:
            child_board.groups.set(instance.groups.all())
