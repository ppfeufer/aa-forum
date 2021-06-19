"""
Managers for our models
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Prefetch, Q


class SettingsManager(models.Manager):
    """
    SettingsManager
    """

    def get_setting(self, setting_key: str) -> str:
        """
        Return the value for given setting key
        """

        return self.get(variable=setting_key).value


class TopicQuerySet(models.QuerySet):
    def get_for_user_from_slugs(
        self, user: User, category_slug: str, board_slug: str, topic_slug: str
    ) -> models.Model:
        """
        Fetch topic from slugs for user. Return None if not found or no access.
        """
        from .models import Board, Message

        try:
            Board.objects.filter(
                Q(groups__in=user.groups.all()) | Q(groups__isnull=True),
                category__slug__slug__exact=category_slug,
                slug__slug__exact=board_slug,
            ).distinct().get()
        except Board.DoesNotExist:
            return None

        try:
            topic = (
                self.select_related(
                    "slug",
                    "board",
                    "board__slug",
                    "board__category",
                    "board__category__slug",
                    "first_message",
                    "first_message__topic",
                    "first_message__topic__slug",
                    "first_message__topic__board",
                    "first_message__topic__board__slug",
                    "first_message__topic__board__category",
                    "first_message__topic__board__category__slug",
                )
                .prefetch_related(
                    Prefetch(
                        "messages",
                        queryset=Message.objects.select_related(
                            "user_created", "user_created__profile__main_character"
                        ).order_by("time_posted"),
                        to_attr="messages_sorted",
                    )
                )
                .get(slug__slug__exact=topic_slug)
            )
        except self.model.DoesNotExist:
            return None

        return topic


class TopicManagerBase(models.Manager):
    pass


TopicManager = TopicManagerBase.from_queryset(TopicQuerySet)
