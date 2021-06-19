from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from ..models import Board, Category, LastMessageSeen, Message, Topic
from .utils import create_fake_messages, create_fake_user, my_get_setting

VIEWS_PATH = "aa_forum.views.forum"


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
        create_fake_messages(cls.topic, 14)
        cls.topic.update_last_message()
        cls.board.update_last_message()

    def test_should_show_index(self):
        # given
        self.client.force_login(self.user)
        # when
        res = self.client.get(reverse("aa_forum:forum_index"))
        # then
        self.assertEqual(res.status_code, 200)


class TestBoardViews(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_1001 = create_fake_user(
            1001, "Bruce Wayne", permissions=["aa_forum.basic_access"]
        )
        cls.user_1002 = create_fake_user(
            1002, "Peter Parker", permissions=["aa_forum.basic_access"]
        )
        cls.category = Category.objects.create(name="Science")
        cls.board = Board.objects.create(name="Physics", category=cls.category)
        # topic 1 is completely new
        cls.topic_1 = Topic.objects.create(subject="Mysteries", board=cls.board)
        create_fake_messages(cls.topic_1, 15)
        cls.topic_1.update_last_message()
        # topic 2 is read
        cls.topic_2 = Topic.objects.create(subject="Off Topic", board=cls.board)
        create_fake_messages(cls.topic_2, 9)
        cls.topic_2.update_last_message()
        cls.board.update_last_message()
        LastMessageSeen.objects.create(
            topic=cls.topic_2,
            user=cls.user_1001,
            message_time=cls.topic_2.messages.order_by("-time_posted")[0].time_posted,
        )

    def test_should_show_new_indicator_when_topic_not_seen_yet(self):
        # given
        self.client.force_login(self.user_1001)
        # when
        res = self.client.get(
            reverse("aa_forum:forum_board", args=[self.category.slug, self.board.slug])
        )
        # then
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, f"aa-forum-link-new-{self.topic_1.id}")

    def test_should_show_new_indicator_when_seen_first_page_only(self):
        # given
        self.client.force_login(self.user_1001)
        last_message_seen = self.topic_1.messages.order_by("time_posted")[4]
        LastMessageSeen.objects.create(
            topic=self.topic_1,
            user=self.user_1001,
            message_time=last_message_seen.time_posted,
        )
        # when
        res = self.client.get(
            reverse("aa_forum:forum_board", args=[self.category.slug, self.board.slug])
        )
        # then
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, f"aa-forum-link-new-{self.topic_1.id}")

    def test_should_show_new_indicator_when_seen_second_page_only(self):
        # given
        self.client.force_login(self.user_1001)
        last_message_seen = self.topic_1.messages.order_by("time_posted")[9]
        LastMessageSeen.objects.create(
            topic=self.topic_1,
            user=self.user_1001,
            message_time=last_message_seen.time_posted,
        )
        # when
        res = self.client.get(
            reverse("aa_forum:forum_board", args=[self.category.slug, self.board.slug])
        )
        # then
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, f"aa-forum-link-new-{self.topic_1.id}")

    def test_should_not_show_new_indicator_when_seen_last_page(self):
        # given
        self.client.force_login(self.user_1001)
        last_message_seen = self.topic_1.messages.order_by("time_posted")[14]
        LastMessageSeen.objects.create(
            topic=self.topic_1,
            user=self.user_1001,
            message_time=last_message_seen.time_posted,
        )
        # when
        res = self.client.get(
            reverse("aa_forum:forum_board", args=[self.category.slug, self.board.slug])
        )
        # then
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, f"aa-forum-link-new-{self.topic_1.id}")

    def test_should_show_new_indicator_when_new_posts_are_made(self):
        # given
        self.client.force_login(self.user_1001)
        # when
        Message.objects.create(
            topic=self.topic_2, user_created=self.user_1002, message="new message"
        )
        res = self.client.get(
            reverse("aa_forum:forum_board", args=[self.category.slug, self.board.slug])
        )
        # then
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, f"aa-forum-link-new-{self.topic_2.id}")


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
        last_message = self.topic.messages.order_by("time_posted")[4]
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

    def test_should_redirect_to_first_message_when_topic_not_seen_yet(self):
        # given
        self.client.force_login(self.user)
        first_message = self.topic.messages.order_by("time_posted").first()
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_topic_unread",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )
        # then
        self.assertRedirects(res, first_message.get_absolute_url())

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
        self.assertRedirects(res, first_unseen_message.get_absolute_url())

    def test_should_redirect_to_newest_message_when_seen_full_topic(self):
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
        self.assertRedirects(res, last_seen_message.get_absolute_url())

    def test_should_redirect_to_message_by_id_first_page(self):
        # given
        self.client.force_login(self.user)
        my_message = self.topic.messages.order_by("time_posted")[3]
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_message_entry_point_in_topic",
                args=[my_message.id],
            ),
        )
        # then
        self.assertRedirects(res, my_message.get_absolute_url())

    def test_should_redirect_to_message_by_id_middle_page_1(self):
        # given
        self.client.force_login(self.user)
        my_message = self.topic.messages.order_by("time_posted")[5]
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_message_entry_point_in_topic",
                args=[my_message.id],
            ),
        )
        # then
        self.assertRedirects(res, my_message.get_absolute_url())

    def test_should_redirect_to_message_by_id_middle_page_2(self):
        # given
        self.client.force_login(self.user)
        my_message = self.topic.messages.order_by("time_posted")[9]
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_message_entry_point_in_topic",
                args=[my_message.id],
            ),
        )
        # then
        self.assertRedirects(res, my_message.get_absolute_url())

    def test_should_redirect_to_message_by_id_last_page(self):
        # given
        self.client.force_login(self.user)
        my_message = self.topic.messages.order_by("time_posted")[12]
        # when
        res = self.client.get(
            reverse(
                "aa_forum:forum_message_entry_point_in_topic",
                args=[my_message.id],
            ),
        )
        # then
        self.assertRedirects(res, my_message.get_absolute_url())
