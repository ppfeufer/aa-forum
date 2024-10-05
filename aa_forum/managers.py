"""
Managers for AA Forum models
"""

# pylint: disable=cyclic-import

# Django
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Prefetch, Q, QuerySet


class SettingQuerySet(models.QuerySet):
    """
    SettingQuerySet
    """

    def delete(self):
        """
        Delete action

        Override :: We don't allow deletion here, so we make sure the object
                    is saved again and not deleted

        :return:
        :rtype:
        """

        return super().update()


class SettingManager(models.Manager):
    """
    SettingManager
    """

    def get_setting(self, setting_key: str) -> str:
        """
        Get a setting value

        :param setting_key:
        :type setting_key:
        :return:
        :rtype:
        """

        return getattr(self.first(), setting_key)

    def get_queryset(self):
        """
        Get a Setting queryset

        :return:
        :rtype:
        """

        return SettingQuerySet(self.model)


class BoardQuerySet(models.QuerySet):
    """
    BoardQuerySet
    """

    def user_has_access(self, user: User) -> models.QuerySet:
        """
        Filter boards that given user has access to.

        :param user:
        :type user:
        :return:
        :rtype:
        """

        # Forum manager always has access, so assign this permission wisely
        if user.has_perm(perm="aa_forum.manage_forum"):
            return self

        # If not a forum manager, check if the user has access to the board
        return self.filter(
            Q(groups__in=user.groups.all()) | Q(groups__isnull=True)
        ).distinct()


class BoardManagerBase(models.Manager):
    """
    BoardManagerBase
    """

    pass  # pylint: disable=unnecessary-pass


BoardManager = BoardManagerBase.from_queryset(BoardQuerySet)


class TopicQuerySet(models.QuerySet):
    """
    TopicQuerySet
    """

    def user_has_access(self, user: User) -> models.QuerySet:
        """
        Filter boards that given user has access to.

        :param user:
        :type user:
        :return:
        :rtype:
        """

        # Forum manager always has access, so assign this permission wisely
        if user.has_perm(perm="aa_forum.manage_forum"):
            return self

        # If not a forum manager, check if the user has access to the board
        return self.filter(
            Q(board__groups__in=user.groups.all()) | Q(board__groups__isnull=True)
        ).distinct()

    def get_from_slugs(
        self,
        category_slug: str,
        board_slug: str,
        topic_slug: str,
        user: User,
    ) -> models.Model:
        """
        Fetch a topic from slugs for user. Return None if not found or no access.

        :param category_slug:
        :type category_slug:
        :param board_slug:
        :type board_slug:
        :param topic_slug:
        :type topic_slug:
        :param user:
        :type user:
        :return:
        :rtype:
        """

        # AA Forum
        from aa_forum.models import Message  # pylint: disable=import-outside-toplevel

        try:
            topic = (
                self.select_related(
                    "board",
                    "board__category",
                    "first_message",
                    "first_message__topic",
                    "first_message__topic__board",
                    "first_message__topic__board__category",
                )
                .prefetch_related(
                    Prefetch(
                        lookup="messages",
                        queryset=Message.objects.select_related(
                            "user_created",
                            "user_created__profile__main_character",
                            "user_created__aa_forum_user_profile",
                        ).order_by("time_posted"),
                        to_attr="messages_sorted",
                    )
                )
                .filter(
                    board__category__slug=str(category_slug),
                    board__slug=str(board_slug),
                    slug=str(topic_slug),
                )
                .user_has_access(user=user)
                .distinct()
                .get()
            )
        except self.model.DoesNotExist:
            return None

        return topic


class TopicManagerBase(models.Manager):
    """
    TopicManagerBase
    """

    pass  # pylint: disable=unnecessary-pass


TopicManager = TopicManagerBase.from_queryset(TopicQuerySet)


class MessageQuerySet(models.QuerySet):
    """
    MessageQuerySet
    """

    def user_has_access(self, user: User) -> models.QuerySet:
        """
        Filter the topics a given user has access to.

        :param user:
        :type user:
        :return:
        :rtype:
        """

        # Forum manager always has access, so assign this permission wisely
        if user.has_perm(perm="aa_forum.manage_forum"):
            return self

        # If not a forum manager, check if the user has access to the board.
        return self.filter(
            Q(topic__board__groups__in=user.groups.all())
            | Q(topic__board__groups__isnull=True)
        ).distinct()

    def get_from_slugs(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        category_slug: str,
        board_slug: str,
        topic_slug: str,
        message_id: int,
        user: User,
    ) -> models.Model:
        """
        Fetch a message from slugs for user. Return None if not found or no access.

        :param category_slug:
        :type category_slug:
        :param board_slug:
        :type board_slug:
        :param topic_slug:
        :type topic_slug:
        :param message_id:
        :type message_id:
        :param user:
        :type user:
        :return:
        :rtype:
        """

        try:
            message = (
                self.select_related(
                    "topic",
                    "topic__board",
                    "topic__board__category",
                    "topic__first_message",
                    "topic__first_message__topic",
                    "topic__first_message__topic__board",
                    "topic__first_message__topic__board__category",
                )
                .filter(
                    topic__board__category__slug=str(category_slug),
                    topic__board__slug=str(board_slug),
                    topic__slug=str(topic_slug),
                    pk=message_id,
                )
                .user_has_access(user=user)
                .distinct()
                .get()
            )
        except self.model.DoesNotExist:
            return None

        return message


class MessageManagerBase(models.Manager):
    """
    MessageManagerBase
    """

    pass  # pylint: disable=unnecessary-pass


MessageManager = MessageManagerBase.from_queryset(MessageQuerySet)


class PersonalMessageQuerySet(models.QuerySet):
    """
    PersonalMessageQuerySet
    """

    def get_personal_messages_for_user(self, user: User) -> QuerySet:
        """
        Get a user's personal messages

        :param user:
        :type user:
        :return:
        :rtype:
        """

        messages = (
            self.filter(recipient=user, deleted_by_recipient=False)
            .select_related(
                "sender", "sender__profile", "sender__profile__main_character"
            )
            .order_by("-time_sent")
        )

        return messages

    def get_personal_messages_sent_for_user(self, user: User) -> QuerySet:
        """
        Get a user's personal messages sent

        :param user:
        :type user:
        :return:
        :rtype:
        """

        messages = (
            self.filter(sender=user, deleted_by_sender=False)
            .select_related(
                "recipient", "recipient__profile", "recipient__profile__main_character"
            )
            .order_by("-time_sent")
        )

        return messages

    def get_personal_message_unread_count_for_user(self, user: User) -> int:
        """
        Get a user's unread personal messages count

        :param user:
        :type user:
        :return:
        :rtype:
        """

        unread_count = self.filter(
            recipient=user, is_read=False, deleted_by_recipient=False
        ).count()

        return unread_count


class PersonalMessageManagerBase(models.Manager):
    """
    PersonalMessageManagerBase
    """

    pass  # pylint: disable=unnecessary-pass


PersonalMessageManager = PersonalMessageManagerBase.from_queryset(
    PersonalMessageQuerySet
)
