"""
Models
"""

# Standard Library
import math

# Third Party
import unidecode

# Django
from django.contrib.auth.models import Group, User
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# ckEditor
from ckeditor_uploader.fields import RichTextUploadingField

# AA Forum
from aa_forum.constants import (
    DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER,
    INTERNAL_URL_PREFIX,
    SETTING_MESSAGESPERPAGE,
)
from aa_forum.helper.text import string_cleanup
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
    slug_name = slugify(unidecode.unidecode(name), allow_unicode=True)

    while MyModel.objects.filter(slug=slug_name).exists():
        run += 1
        slug_name = slugify(unidecode.unidecode(f"{name}-{run}"), allow_unicode=True)

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
    order = models.IntegerField(
        default=DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER, db_index=True
    )

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

        if self.slug == "":
            self.slug = _generate_slug(
                type(self), f"{self.__class__.__name__} {self.pk}"
            )
            self.save()


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
    discord_webhook = models.CharField(
        blank=True, null=True, default=None, max_length=254
    )
    use_webhook_for_replies = models.BooleanField(
        default=False,
        help_text=(
            "Use this Discord Webhook for replies as well? When activated every reply "
            "to any topic in this board will be posted to the defined Discord channel. "
            "(Child boards are excluded) Chose wisely! (Default: NO)"
        ),
    )
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
        help_text=(
            "User in at least one of these groups have access to this board. If "
            "no groups are selected, everyone with access to the forum has also "
            "access to this board."
        ),
    )
    is_announcement_board = models.BooleanField(
        default=False,
        help_text=(
            "Mark this board as an 'Announcement Board', meaning that only certain "
            "selected groups can start new topics. All others who have access to this "
            "board will still be able to discuss in the topics though. (Default: NO)"
        ),
    )
    announcement_groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="aa_forum_boards_group_start_topic_restriction",
        help_text=(
            "User in at least one of the selected groups will be able to start topics "
            "in 'Announcement Boards'. If no group is selected, only forum admins can "
            "do so."
        ),
    )
    order = models.IntegerField(
        default=DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER, db_index=True
    )
    first_message = models.ForeignKey(
        "Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",
        # for adding "Re:" if needed, must be within the same topic as last message
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

        if self.slug == "":
            self.slug = _generate_slug(
                type(self), f"{self.__class__.__name__} {self.pk}"
            )
            self.save()

    def get_absolute_url(self) -> str:
        """
        Calculate URL for this board and return it.
        """

        return reverse("aa_forum:forum_board", args=[self.category.slug, self.slug])

    def user_can_start_topic(self, user: User) -> bool:
        """
        Determine if we have an Announcement Board and the current user can start a topic
        :param user:
        :return:
        """

        user_can_start_topic = True

        if self.is_announcement_board:
            if (
                user.has_perm("aa_forum.manage_forum")
                or user.groups.filter(pk__in=self.announcement_groups.all()).exists()
            ):
                user_can_start_topic = True
            else:
                user_can_start_topic = False

        return user_can_start_topic

    def _update_message_references(self):
        """
        Update the first and last message for this board - and parent board if needed.
        """

        self.last_message = (
            Message.objects.filter(
                Q(topic__board=self) | Q(topic__board__parent_board=self)
            )
            .order_by("-time_posted")
            .first()
        )
        if self.last_message:
            self.first_message = self.last_message.topic.messages.order_by(
                "time_posted"
            ).first()
        else:
            self.first_message = None
        self.save(update_fields=["first_message", "last_message"])
        if self.parent_board:
            self.parent_board._update_message_references()


class Topic(models.Model):
    """
    Topic
    """

    board = models.ForeignKey(Board, related_name="topics", on_delete=models.CASCADE)
    subject = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True, allow_unicode=True)
    is_sticky = models.BooleanField(default=False, db_index=True)
    is_locked = models.BooleanField(default=False, db_index=True)
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

        if not self._state.adding and self.pk:
            try:
                old_instance = Topic.objects.get(pk=self.pk)
            except Topic.DoesNotExist:
                old_instance = None
        else:
            old_instance = None

        board_needs_update = old_instance and (
            old_instance.first_message != self.first_message
            or old_instance.last_message != self.last_message
        )

        if self._state.adding is True or self.slug == INTERNAL_URL_PREFIX:
            self.slug = _generate_slug(type(self), self.subject)

        super().save(*args, **kwargs)

        if self.slug == "":
            self.slug = _generate_slug(
                type(self), f"{self.__class__.__name__} {self.pk}"
            )
            self.save()

        if board_needs_update:
            self.board._update_message_references()

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        """
        On delete
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """
        board_needs_update = (
            self.first_message == self.board.first_message
            or self.last_message == self.board.last_message
        )
        super().delete(*args, **kwargs)
        if board_needs_update:
            self.board._update_message_references()

    def get_absolute_url(self) -> str:
        """
        Calculate URL for this topic and return it.
        """

        return reverse(
            "aa_forum:forum_topic",
            args=[self.board.category.slug, self.board.slug, self.slug],
        )

    def _update_message_references(self):
        """
        Update the first and last message for this topic.
        """

        self.first_message = (
            Message.objects.filter(topic=self).order_by("time_posted").first()
        )
        self.last_message = (
            Message.objects.filter(topic=self).order_by("-time_posted").first()
        )
        self.save(update_fields=["first_message", "last_message"])


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

        self.message = string_cleanup(self.message)
        self.message_plaintext = strip_tags(self.message)

        super().save(*args, **kwargs)

        update_fields = []

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

        topic_needs_update = (
            self.topic.first_message == self or self.topic.last_message == self
        )
        board_needs_update = (
            self.topic.board.first_message == self
            or self.topic.board.last_message == self
        )

        super().delete(*args, **kwargs)

        if topic_needs_update:
            self.topic._update_message_references()

        if board_needs_update:
            self.topic.board._update_message_references()

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

    def excerpt(self, length: int = 250, with_end_marker: bool = True) -> str:
        """
        Returns an excerpt of a given length (default: 250) of a
        messages' plaintext content
        :param length:
        :param with_end_marker:
        :return:
        """

        end_marker = " […]" if with_end_marker is True else ""

        if len(self.message_plaintext) >= length:
            excerpt = self.message_plaintext[0:length] + end_marker
        else:
            excerpt = self.message_plaintext + end_marker

        return excerpt


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
