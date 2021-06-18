from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from aa_forum.constants import SETTING_MESSAGESPERPAGE

from ..models import Board, Category, LastMessageSeen, Message, Setting, Topic
from .utils import create_fake_messages, create_fake_user

VIEWS_PATH = "aa_forum.views.forum"


def my_get_setting(setting_key: str) -> str:
    """Overload settings for tests."""
    if setting_key == SETTING_MESSAGESPERPAGE:
        return "5"
    return Setting.objects.get_setting(setting_key=setting_key)


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
        cls.topic.update_last_message()
        cls.board.update_last_message()

    def test_should_show_index(self):
        # given
        self.client.force_login(self.user)
        # when
        res = self.client.get(reverse("aa_forum:forum_index"))
        # then
        self.assertEqual(res.status_code, 200)


@patch(VIEWS_PATH + ".Setting.objects.get_setting", new=my_get_setting)
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
        create_fake_messages(cls.topic, 15)
        cls.topic.update_last_message()
        cls.board.update_last_message()

    def test_should_remember_last_message_seen_by_user_page_1(self):
        # given
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
        # view has 2 pages á 5 messages. this is last message on 1st page
        last_message = Message.objects.order_by("time_posted")[4]
        self.assertEqual(last_message_seen.message_time, last_message.time_posted)

    def test_should_remember_last_message_seen_by_user_page_2(self):
        # given
        self.client.force_login(self.user)
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, self.topic.slug, 2],
            )
        )
        # then
        self.assertEqual(res.status_code, 200)
        last_message_seen = LastMessageSeen.objects.get(
            topic=self.topic, user=self.user
        )
        # view has 2 pages á 5 messages. this is last message on 1st page
        last_message = Message.objects.order_by("time_posted")[9]
        self.assertEqual(last_message_seen.message_time, last_message.time_posted)

    def test_should_redirect_to_topic_when_no_last_seen_entry(self):
        # given
        self.client.force_login(self.user)
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_topic_unread",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )
        # then
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res.url,
            reverse(
                "aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            ),
        )

    def test_should_redirect_to_first_new_message(self):
        # given
        self.client.force_login(self.user)
        messages_sorted = list(self.topic.messages.order_by("time_posted"))
        last_seen_message = messages_sorted[2]
        first_unseen_message = messages_sorted[3]
        LastMessageSeen.objects.create(
            topic=self.topic,
            user=self.user,
            message_time=last_seen_message.time_posted,
        )
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_topic_unread",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )
        # then
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res.url,
            reverse(
                "aa_forum:forum_message_entry_point_in_topic",
                args=[first_unseen_message.id],
            ),
        )

    def test_should_redirect_to_newest_message(self):
        # given
        self.client.force_login(self.user)
        last_seen_message = self.topic.messages.order_by("-time_posted")[0]
        LastMessageSeen.objects.create(
            topic=self.topic,
            user=self.user,
            message_time=last_seen_message.time_posted,
        )
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_topic_unread",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )
        # then
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res.url,
            reverse(
                "aa_forum:forum_message_entry_point_in_topic",
                args=[last_seen_message.id],
            ),
        )
