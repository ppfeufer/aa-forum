"""
Models for AA-Forum
"""

# Standard Library
import math
from typing import ClassVar

# Third Party
import unidecode
from solo.models import SingletonModel

# Django
from django.contrib.auth.models import Group, Permission, User
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.django import users_with_permission
from app_utils.logging import LoggerAddTag

# CKEditor
from django_ckeditor_5.fields import CKEditor5Field

# AA Forum
from aa_forum import __title__
from aa_forum.constants import (
    DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER,
    INTERNAL_URL_PREFIX,
)
from aa_forum.helper.text import string_cleanup
from aa_forum.managers import (
    BoardManager,
    MessageManager,
    PersonalMessageManager,
    SettingManager,
    TopicManager,
)

logger = LoggerAddTag(my_logger=get_extension_logger(name=__name__), prefix=__title__)


def get_sentinel_user() -> User:
    """
    Get the sentinel user or create one

    :return:
    :rtype:
    """

    return User.objects.get_or_create(username="deleted")[0]


def _generate_slug(calling_model: models.Model, name: str) -> str:
    """
    Generate a slug for a model

    :param calling_model:
    :type calling_model:
    :param name:
    :type name:
    :return:
    :rtype:
    """

    if name == INTERNAL_URL_PREFIX:
        name = "hyphen"

    run = 0
    slug_name = slugify(value=unidecode.unidecode(name), allow_unicode=True)

    while calling_model.objects.filter(slug=slug_name).exists():
        run += 1
        slug_name = slugify(
            value=unidecode.unidecode(f"{name}-{run}"), allow_unicode=True
        )

    return slug_name


class General(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        verbose_name = _("AA-Forum")
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", _("Can access the AA-Forum module")),
            (
                "manage_forum",
                _("Can manage the AA-Forum module (Category, topics and messages)"),
            ),
        )

    @classmethod
    def basic_permission(cls):
        """
        Return the basic permission for this app

        :return:
        :rtype:
        """

        return Permission.objects.select_related("content_type").get(
            content_type__app_label=cls._meta.app_label, codename="basic_access"
        )

    @classmethod
    def users_with_basic_access(cls) -> models.QuerySet:
        """
        Return all users with basic access to this app

        :return:
        :rtype:
        """

        return users_with_permission(permission=cls.basic_permission())


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

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self) -> str:
        """
        Return the name of the category

        :return:
        :rtype:
        """

        return str(self.name)

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Generates the slug

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        if self._state.adding is True or self.slug == INTERNAL_URL_PREFIX:
            self.slug = _generate_slug(calling_model=type(self), name=self.name)

        super().save(*args, **kwargs)

        if self.slug == "":
            self.slug = _generate_slug(
                calling_model=type(self), name=f"{self.__class__.__name__} {self.pk}"
            )
            self.save()


class Board(models.Model):
    """
    Board
    """

    category = models.ForeignKey(
        to=Category, related_name="boards", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True, allow_unicode=True)
    description = models.TextField(
        blank=True, help_text=_("Board description (optional)")
    )
    discord_webhook = models.CharField(
        blank=True,
        null=True,
        default=None,
        max_length=254,
        help_text=_(
            "Discord webhook URL for the channel to post about new topics in this "
            "board. (This setting is optional)"
        ),
    )
    use_webhook_for_replies = models.BooleanField(
        default=False,
        help_text=_(
            "Use this Discord webhook for replies as well? When activated every "
            "reply to any topic in this board will be posted to the defined "
            "Discord channel. (Child boards are excluded) Chose wisely! "
            "(Default: NO)"
        ),
    )
    parent_board = models.ForeignKey(
        to="self",
        blank=True,
        null=True,
        related_name="child_boards",
        on_delete=models.CASCADE,
    )
    groups = models.ManyToManyField(
        to=Group,
        blank=True,
        related_name="aa_forum_boards_group_restriction",
        help_text=_(
            "This will restrict access to this board to the selected groups. If no "
            "groups are selected, everyone who can access the forum can also access "
            "this board. (This setting is optional)"
        ),
    )
    is_announcement_board = models.BooleanField(
        default=False,
        help_text=_(
            'Mark this board as an "Announcement Board", meaning that only certain '
            "selected groups can start new topics. All others who have access to this "
            "board will still be able to discuss in the topics though. This setting "
            "will not be inherited to child boards. (Default: NO)"
        ),
    )
    announcement_groups = models.ManyToManyField(
        to=Group,
        blank=True,
        related_name="aa_forum_boards_group_start_topic_restriction",
        help_text=_(
            "User in at least one of the selected groups will be able to start topics "
            'in "Announcement Boards". If no group is selected, only forum admins can '
            "do so. This setting will not be inherited to child boards. (Hint: These "
            "restrictions only take effect when a board is marked as "
            '"Announcement Board", see checkbox above.)'
        ),
    )
    order = models.IntegerField(
        default=DEFAULT_CATEGORY_AND_BOARD_SORT_ORDER, db_index=True
    )
    first_message = models.ForeignKey(
        to="Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",  # Don't add this to translations
        # for adding "Re:" if needed, must be within the same topic as last message
    )
    last_message = models.ForeignKey(
        to="Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",  # Don't add this to translations
    )

    objects: ClassVar[BoardManager] = BoardManager()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("board")
        verbose_name_plural = _("boards")
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="fpk_board")
        ]

    class TopicAlreadyExists(Exception):
        """
        Exception when a topic with the same subject already exists in this board

        This should be caught and handled.

        Example:
            >>> try:
            ...     new_topic = current_board.new_topic(
            ...         subject="Foobar",
            ...         message="Barfoo",
            ...         user=request.user,
            ...     )
            ... except current_board.TopicAlreadyExists as exc:
            ...     messages.warning(request=request, message=exc)
            ...
            ...     return render(
            ...         request=request,
            ...         template_name="aa_forum/view/forum/new-topic.html",
            ...         context={"board": current_board, "form": form},
            ...     )
        """

        def __init__(self, topic: "Topic") -> None:
            """
            Initialize our Exception

            :param topic:
            :type topic:
            """

            super().__init__(topic)

            self._topic = topic

        @property
        def topic_url(self) -> str:
            """
            Build the URL to the already existing topic.
            We need this later in the error message.

            :return:
            :rtype:
            """

            existing_topic_url = reverse(
                viewname="aa_forum:forum_topic",
                kwargs={
                    "category_slug": self._topic.board.category.slug,
                    "board_slug": self._topic.board.slug,
                    "topic_slug": self._topic.slug,
                },
            )

            return existing_topic_url

        def __str__(self) -> str:
            """
            Return the error message

            :return:
            :rtype:
            """

            return str(
                mark_safe(
                    s=_(
                        f'<h4>Warning!</h4><p>There is already a topic with the exact same subject in this board.</p><p>See here: <a href="{self.topic_url}">{self._topic.subject}</a></p>'  # pylint: disable=line-too-long
                    )
                )
            )

    def __str__(self) -> str:
        """
        Return the name of the board

        :return:
        :rtype:
        """

        return str(self.name)

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Generates the slug

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        if self._state.adding is True or self.slug == INTERNAL_URL_PREFIX:
            self.slug = _generate_slug(calling_model=type(self), name=self.name)

        super().save(*args, **kwargs)

        if self.slug == "":
            self.slug = _generate_slug(
                calling_model=type(self), name=f"{self.__class__.__name__} {self.pk}"
            )
            self.save()

    def get_absolute_url(self) -> str:
        """
        Calculate URL for this board and return it.

        :return:
        :rtype:
        """

        return reverse(
            viewname="aa_forum:forum_board", args=[self.category.slug, self.slug]
        )

    def user_can_start_topic(self, user: User) -> bool:
        """
        Check if the user can start a topic in this board

        :param user:
        :type user:
        :return:
        :rtype:
        """

        if self.is_announcement_board:
            return bool(
                user.has_perm(perm="aa_forum.manage_forum")
                or user.groups.filter(pk__in=self.announcement_groups.all()).exists()
            )

        return True

    def _update_message_references(self):
        """
        Update the first and last message for this board.

        :return:
        :rtype:
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

    def new_topic(self, subject: str, message: str, user: User) -> "Topic":
        """
        Start a new topic in this board

        Warning:
            This function will NOT check if the current logged-in user
            has access to the board or is allowed to start a new topic
            in this board.
            You have to implement these checks on your own!

            The following checks are recommended:
            - User has access to the board:
                >>> try:
                ...     current_board: Board = (
                ...         Board.objects.select_related("category")
                ...         .user_has_access(user=request.user)
                ...         .filter(category__slug=category_slug, slug=board_slug)
                ...         .get()
                ...     )
                ... except Board.DoesNotExist:
                ...     messages.error(
                ...         request=request,
                ...         message=mark_safe(
                ...             s=_(
                ...                 "<h4>Error!</h4><p>The board you were trying to post in does "
                ...                 "either not exist, or you don't have access to it.</p>"
                ...             )
                ...         ),
                ...     )
            - User can start a topic in the current board. If the user can't, it's probably an Announcement Board.
                >>> if not current_board.user_can_start_topic(user=request.user):
                ...    messages.error(
                ...        request=request,
                ...        message=mark_safe(
                ...            s=_(
                ...                "<h4>Error!</h4><p>The board you were trying to post in is "
                ...                "an announcement board and you don't have the permissions to "
                ...                "start a topic there.</p>"
                ...            )
                ...        ),
                ...    )

        :param subject:
        :type subject:
        :param message:
        :type message:
        :param user:
        :type user:
        :return:
        :rtype:
        """

        logger.debug(msg="Starting new topic")

        with transaction.atomic():
            # Check if a topic with the same subject already exists in this board
            existing_topic = Topic.objects.filter(board=self, subject__iexact=subject)

            if existing_topic.exists():
                logger.debug(msg=f'Topic "{subject}" already exists!')

                existing_topic = existing_topic.get()

                raise self.TopicAlreadyExists(topic=existing_topic)

            new_topic = Topic(board=self, subject=subject)
            new_topic.save()

            new_message = Message(topic=new_topic, user_created=user, message=message)
            new_message.save()

            logger.info(
                msg=(
                    f'{user} started a new topic "{subject}" '
                    f'in board "{self.name}".'
                )
            )

            # Send to webhook if one is configured
            if self.discord_webhook is not None:
                # AA Forum
                from aa_forum.helper.discord_messages import (  # pylint: disable=import-outside-toplevel
                    send_message_to_discord_webhook,
                )

                send_message_to_discord_webhook(
                    board=self,
                    topic=new_topic,
                    message=new_message,
                    headline=f'**New topic has been started in board "{self.name}"**',
                )

            return new_topic


class Topic(models.Model):
    """
    Topic
    """

    board = models.ForeignKey(to=Board, related_name="topics", on_delete=models.CASCADE)
    subject = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True, allow_unicode=True)
    is_sticky = models.BooleanField(default=False, db_index=True)
    is_locked = models.BooleanField(default=False, db_index=True)
    first_message = models.ForeignKey(
        to="Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",  # Don't add this to translations
    )
    last_message = models.ForeignKey(
        to="Message",
        editable=False,
        null=True,
        default=None,
        related_name="+",
        on_delete=models.SET_DEFAULT,
        help_text="Shortcut for better performance",  # Don't add this to translations
    )

    objects: ClassVar[TopicManager] = TopicManager()

    class Meta:  # pylint: disable=too-few-public-methods
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
        """
        Return the subject of the topic

        :return:
        :rtype:
        """

        return str(self.subject)

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Generate slug for new objects and update first and last messages.

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
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
            self.slug = _generate_slug(calling_model=type(self), name=self.subject)

        super().save(*args, **kwargs)

        if self.slug == "":
            self.slug = _generate_slug(
                calling_model=type(self), name=f"{self.__class__.__name__} {self.pk}"
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
        :return:
        :rtype:
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

        :return:
        :rtype:
        """

        return reverse(
            viewname="aa_forum:forum_topic",
            args=[self.board.category.slug, self.board.slug, self.slug],
        )

    def _update_message_references(self):
        """
        Update the first and last message for this topic.

        :return:
        :rtype:
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

    topic = models.ForeignKey(
        to=Topic, on_delete=models.CASCADE, related_name="last_message_seen"
    )
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="aa_forum_last_message_seen"
    )
    message_time = models.DateTimeField()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        indexes = [
            models.Index(
                fields=["topic", "user", "message_time"],
                name="lastmessageseen_compounded",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a string representation of this object

        :return:
        :rtype:
        """

        return f"{self.topic}-{self.user}-{self.message_time}"


class Message(models.Model):
    """
    Message
    """

    topic = models.ForeignKey(
        to=Topic,
        related_name="messages",
        on_delete=models.CASCADE,
    )
    time_posted = models.DateTimeField(auto_now_add=True, db_index=True)
    time_modified = models.DateTimeField(auto_now=True)
    user_created = models.ForeignKey(
        to=User,
        related_name="+",
        on_delete=models.SET(value=get_sentinel_user),
    )
    user_updated = models.ForeignKey(
        to=User,
        blank=True,
        null=True,
        related_name="+",
        on_delete=models.SET(value=get_sentinel_user),
    )
    message = CKEditor5Field(blank=False, config_name="extends")
    message_plaintext = models.TextField(blank=True)

    objects: ClassVar[MessageManager] = MessageManager()

    class Meta:  # pylint: disable=too-few-public-methods
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
        Saving

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        self.message = string_cleanup(string=self.message)
        self.message_plaintext = strip_tags(value=self.message)

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
        :return:
        :rtype:
        """

        topic_needs_update = self in (self.topic.first_message, self.topic.last_message)
        board_needs_update = self in (
            self.topic.board.first_message,
            self.topic.board.last_message,
        )

        super().delete(*args, **kwargs)

        if topic_needs_update:
            self.topic._update_message_references()

        if board_needs_update:
            self.topic.board._update_message_references()

    def get_absolute_url(self):
        """
        Calculate URL for this message and return it.

        :return:
        :rtype:
        """

        messages_per_topic = int(
            Setting.objects.get_setting(setting_key=Setting.Field.MESSAGESPERPAGE)
        )
        position = (
            self.topic.messages.order_by("time_posted")
            .filter(time_posted__lt=self.time_posted)
            .count()
        ) + 1

        page = math.ceil(position / messages_per_topic)

        if page > 1:
            redirect_path = reverse(
                viewname="aa_forum:forum_topic",
                args=(
                    self.topic.board.category.slug,
                    self.topic.board.slug,
                    self.topic.slug,
                    page,
                ),
            )
        else:
            redirect_path = reverse(
                viewname="aa_forum:forum_topic",
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
        to=User,
        related_name="+",
        on_delete=models.CASCADE,
    )
    recipient = models.ForeignKey(
        to=User,
        related_name="+",
        on_delete=models.CASCADE,
    )
    time_sent = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=254)
    message = CKEditor5Field(blank=False, config_name="extends")
    message_head = models.ForeignKey(
        to="self",
        blank=True,
        null=True,
        related_name="replies",
        on_delete=models.CASCADE,
    )
    is_read = models.BooleanField(default=False)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_recipient = models.BooleanField(default=False)

    objects: ClassVar[PersonalMessageManager] = PersonalMessageManager()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("personal message")
        verbose_name_plural = _("personal messages")

    def __str__(self) -> str:
        """
        Return a string representation of this object

        :return:
        :rtype:
        """

        return f'"{self.subject}" from {self.sender} to {self.recipient}'

    @transaction.atomic()
    def save(self, *args, **kwargs) -> None:
        """
        Saving

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        # See if it's a new message and set our status bit accordingly
        is_new_message = self._state.adding

        self.message = string_cleanup(string=self.message)

        super().save(*args, **kwargs)

        # Try to send a Discord PM when we have a new message
        if is_new_message is True:
            # Needs to be imported here, otherwise it's a circular import
            # AA Forum
            from aa_forum.helper.discord_messages import (  # pylint: disable=import-outside-toplevel
                send_new_personal_message_notification,
            )

            # Sending Discord PM for new personal message, if the user wants it
            send_new_personal_message_notification(message=self)


class Setting(SingletonModel):
    """
    Default forum settings
    """

    class Field(models.TextChoices):
        """
        Choices for Setting.Field
        """

        MESSAGESPERPAGE = "messages_per_page", _("Messages per page")
        TOPICSPERPAGE = "topics_per_page", _("Topics per page")
        USERSIGNATURELENGTH = "user_signature_length", _("User signature length")

    messages_per_page = models.IntegerField(
        default=15,
        verbose_name=Field.MESSAGESPERPAGE.label,  # pylint: disable=no-member
        help_text=_(
            "How many messages per page should be displayed in a forum topic? "
            "(Default: 15)"
        ),
    )
    topics_per_page = models.IntegerField(
        default=10,
        verbose_name=Field.TOPICSPERPAGE.label,  # pylint: disable=no-member
        help_text=_(
            "How many topics per page should be displayed in a forum category?"
            " (Default: 10)"
        ),
    )
    user_signature_length = models.IntegerField(
        default=750,
        verbose_name=Field.USERSIGNATURELENGTH.label,  # pylint: disable=no-member
        help_text=_(
            "How long (Number of characters) is a user's signature allowed to be? "
            "(Default: 750)"
        ),
    )

    objects: ClassVar[SettingManager] = SettingManager()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("setting")
        verbose_name_plural = _("settings")

    def __str__(self) -> str:
        """
        Return a string representation of this object

        :return:
        :rtype:
        """

        return str(_("Forum settings"))


class UserProfile(models.Model):
    """
    A users forum profile
    """

    user = models.OneToOneField(
        to=User,
        related_name="aa_forum_user_profile",
        on_delete=models.CASCADE,
        unique=True,
        primary_key=True,
    )
    signature = CKEditor5Field(blank=True, config_name="extends")
    website_title = models.CharField(max_length=254, blank=True)
    website_url = models.CharField(max_length=254, blank=True)
    discord_dm_on_new_personal_message = models.BooleanField(default=False)
    show_unread_topics_dashboard_widget = models.BooleanField(default=False)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self):
        """
        Return a string representation of this object

        :return:
        :rtype:
        """

        model_string_name = str(_("Forum user profile"))

        return f"{model_string_name}: {self.user}"

    def save(self, *args, **kwargs) -> None:
        """
        Saving

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        self.signature = string_cleanup(string=self.signature)

        super().save(*args, **kwargs)
