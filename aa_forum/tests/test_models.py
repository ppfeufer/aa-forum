import datetime as dt
from unittest.mock import patch

from django.test import TestCase
from django.utils.timezone import now

from ..models import Board, Category, Message, Topic
from .utils import create_fake_user


class TestMessage(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = create_fake_user(1001, "Bruce Wayne")

    def setUp(self) -> None:
        category = Category.objects.create(name="Science")
        self.board = Board.objects.create(name="Physics", category=category)
        self.topic = Topic.objects.create(subject="Mysteries", board=self.board)

    def test_should_update_first_and_last_messages_when_saving_1(self):
        # when
        message = Message.objects.create(
            topic=self.topic, user_created=self.user, message="What is dark matter?"
        )
        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.topic.last_message, message)
        self.assertEqual(self.topic.first_message, message)
        self.assertEqual(self.board.last_message, message)
        self.assertEqual(self.board.first_message, message)

    def test_should_update_first_and_last_messages_when_saving_2(self):
        # given
        my_now = now() - dt.timedelta(hours=1)
        with patch("django.utils.timezone.now", lambda: my_now):
            message_1 = Message.objects.create(
                topic=self.topic, user_created=self.user, message="What is dark matter?"
            )
        # when
        message_2 = Message.objects.create(
            topic=self.topic, user_created=self.user, message="What is dark energy?"
        )
        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.topic.last_message, message_2)
        self.assertEqual(self.topic.first_message, message_1)
        self.assertEqual(self.board.last_message, message_2)
        self.assertEqual(self.board.first_message, message_1)

    def test_should_update_last_messages_when_deleting_last_message(self):
        # given
        my_now = now() - dt.timedelta(hours=1)
        with patch("django.utils.timezone.now", lambda: my_now):
            message_1 = Message.objects.create(
                topic=self.topic, user_created=self.user, message="What is dark matter?"
            )
        message_2 = Message.objects.create(
            topic=self.topic, user_created=self.user, message="What is dark energy?"
        )
        # when
        message_2.delete()
        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.topic.last_message, message_1)
        self.assertEqual(self.topic.first_message, message_1)
        self.assertEqual(self.board.last_message, message_1)
        self.assertEqual(self.board.first_message, message_1)


class TestTopic(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = create_fake_user(1001, "Bruce Wayne")

    def setUp(self) -> None:
        category = Category.objects.create(name="Science")
        self.board = Board.objects.create(name="Physics", category=category)

    def test_should_update_last_message_normal(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        message = Message.objects.create(
            topic=topic, user_created=self.user, message="What is dark energy?"
        )
        topic.last_message = None
        topic.save()
        # when
        topic.update_last_message()
        # then
        topic.refresh_from_db()
        self.assertEqual(topic.last_message, message)

    def test_should_return_none_as_last_message(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        # when
        topic.update_last_message()
        # then
        topic.refresh_from_db()
        self.assertIsNone(topic.last_message)

    def test_should_update_last_message_after_topic_deletion(self):
        # given
        topic_1 = Topic.objects.create(subject="Mysteries", board=self.board)
        topic_2 = Topic.objects.create(subject="Recent Discoveries", board=self.board)
        my_now = now() - dt.timedelta(hours=1)
        with patch("django.utils.timezone.now", lambda: my_now):
            message_1 = Message.objects.create(
                topic=topic_1, user_created=self.user, message="What is dark matter?"
            )
        message_2 = Message.objects.create(
            topic=topic_2, user_created=self.user, message="Energy of the Higgs boson"
        )
        self.board.refresh_from_db()
        self.assertEqual(self.board.last_message, message_2)
        # when
        topic_2.delete()
        # then
        self.board.refresh_from_db()
        self.assertEqual(self.board.last_message, message_1)

    def test_should_not_update_last_message_after_topic_deletion(self):
        # given
        topic_1 = Topic.objects.create(subject="Mysteries", board=self.board)
        topic_2 = Topic.objects.create(subject="Recent Discoveries", board=self.board)
        my_now = now() - dt.timedelta(hours=1)
        with patch("django.utils.timezone.now", lambda: my_now):
            Message.objects.create(
                topic=topic_1, user_created=self.user, message="What is dark matter?"
            )
        message_2 = Message.objects.create(
            topic=topic_2, user_created=self.user, message="Energy of the Higgs boson"
        )
        self.board.refresh_from_db()
        self.assertEqual(self.board.last_message, message_2)
        # when
        topic_1.delete()
        # then
        self.board.refresh_from_db()
        self.assertEqual(self.board.last_message, message_2)


class TestBoard(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = create_fake_user(1001, "Bruce Wayne")

    def setUp(self) -> None:
        self.category = Category.objects.create(name="Science")

    def test_should_update_last_message_normal(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        topic = Topic.objects.create(subject="Mysteries", board=board)
        message = Message.objects.create(
            topic=topic, user_created=self.user, message="What is dark energy?"
        )
        board.last_message = None
        board.save()
        # when
        board.update_last_message()
        # then
        board.refresh_from_db()
        self.assertEqual(board.last_message, message)

    def test_should_update_last_message_empty(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        # when
        board.update_last_message()
        # then
        board.refresh_from_db()
        self.assertIsNone(board.last_message)
