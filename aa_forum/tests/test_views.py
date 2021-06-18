import datetime as dt
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from ..models import Board, Category, LastMessageSeen, Message, Topic
from .utils import create_fake_user


class TestTopicViews(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = create_fake_user(
            1001, "Bruce Wayne", permissions=["aa_forum.basic_access"]
        )
        cls.category = Category.objects.create(name="Science")
        cls.board = Board.objects.create(name="Physics", category=cls.category)
        cls.topic = Topic.objects.create(subject="Mysteries", board=cls.board)

    def test_should_remember_last_seen_message_for_user(self):
        # given
        my_now = now() - dt.timedelta(hours=2)
        with patch("django.utils.timezone.now", lambda: my_now):
            Message.objects.create(
                topic=self.topic, user_created=self.user, message="What is dark matter?"
            )
        my_now = now() - dt.timedelta(hours=1)
        with patch("django.utils.timezone.now", lambda: my_now):
            Message.objects.create(
                topic=self.topic, user_created=self.user, message="What is dark energy?"
            )
        message = Message.objects.create(
            topic=self.topic, user_created=self.user, message="What is gravity?"
        )

        self.client.force_login(self.user)
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )
        # then
        self.assertEqual(res.status_code, 200)
        last_message_seen = LastMessageSeen.objects.get(
            topic=self.topic, user=self.user
        )
        self.assertEqual(last_message_seen.message_time, message.time_posted)
