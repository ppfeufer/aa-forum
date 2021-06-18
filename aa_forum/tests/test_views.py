from django.test import TestCase
from django.urls import reverse

from ..models import Board, Category, LastMessageSeen, Message, Topic
from .utils import create_fake_messages, create_fake_user


class TestIndexView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = create_fake_user(
            1001, "Bruce Wayne", permissions=["aa_forum.basic_access"]
        )
        cls.category = Category.objects.create(name="Science")
        cls.board = Board.objects.create(name="Physics", category=cls.category)
        cls.topic = Topic.objects.create(subject="Mysteries", board=cls.board)
        create_fake_messages(cls.topic, 10)

    def test_should_show_index(self):
        # given
        self.client.force_login(self.user)
        # when
        res = self.client.get(reverse("aa_forum:forum_index"))
        # then
        self.assertEqual(res.status_code, 200)


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
        create_fake_messages(self.topic, 3)
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
        last_message = Message.objects.order_by("-time_posted").first()
        self.assertEqual(last_message_seen.message_time, last_message.time_posted)
