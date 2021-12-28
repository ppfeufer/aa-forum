"""
Tests for our models
"""

# Standard Library
import datetime as dt
from unittest.mock import patch

# Django
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

# AA Forum
from aa_forum.models import Board, Category, Message, Topic
from aa_forum.tests.utils import create_fake_messages, create_fake_user, my_get_setting

MODELS_PATH = "aa_forum.models"


class TestBoard(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")
        cls.group = Group.objects.create(name="Superhero")

    def setUp(self) -> None:
        self.category = Category.objects.create(name="Science")

    def test_model_string_names(self):
        board = Board.objects.create(name="Physics", category=self.category)

        self.assertEqual(str(board), "Physics")

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

    def test_should_update_last_message_normal_from_child_board(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        child_board = Board.objects.create(
            name="Thermodynamics", category=self.category, parent_board=board
        )
        topic_board = Topic.objects.create(subject="Mysteries", board=board)
        topic_child_board = Topic.objects.create(
            subject="Solved Mysteries", board=child_board
        )
        message_board = Message.objects.create(
            topic=topic_board, user_created=self.user, message="What is dark energy?"
        )
        message_child_board = Message.objects.create(
            topic=topic_child_board,
            user_created=self.user,
            message="What is heat?",
        )
        board.last_message = None
        board.save()

        # when
        board.update_last_message()

        # then
        board.refresh_from_db()
        self.assertNotEqual(board.last_message, message_board)
        self.assertEqual(board.last_message, message_child_board)

    def test_should_update_last_message_empty(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)

        # when
        board.update_last_message()

        # then
        board.refresh_from_db()
        self.assertIsNone(board.last_message)

    def test_should_update_last_message_empty_from_child_board(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        Board.objects.create(
            name="Thermodynamics", category=self.category, parent_board=board
        )

        # when
        board.update_last_message()

        # then
        board.refresh_from_db()
        self.assertIsNone(board.last_message)

    def test_should_return_url(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)

        # when
        url = board.get_absolute_url()

        # then
        self.assertURLEqual(
            url,
            reverse("aa_forum:forum_board", args=["science", "physics"]),
        )

    def test_should_return_board_with_no_groups(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board.pk)

        # then
        self.assertTrue(result)

    def test_should_return_board_for_group_member(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)

        self.user.groups.add(self.group)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board.pk)

        # then
        self.assertTrue(result)

    def test_should_return_child_board_for_group_member(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)

        self.user.groups.add(self.group)

        board_2 = Board.objects.create(
            name="Thermal Theories", category=self.category, parent_board=board
        )

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board_2.pk)

        # then
        self.assertTrue(result)

    def test_should_not_return_board_for_non_group_member(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)

        with self.assertRaises(Board.DoesNotExist):
            Board.objects.user_has_access(self.user).get(pk=board.pk)

    def test_should_not_return_child_board_for_non_group_member(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)
        board_2 = Board.objects.create(
            name="Thermal Theories", category=self.category, parent_board=board
        )

        with self.assertRaises(Board.DoesNotExist):
            Board.objects.user_has_access(self.user).get(pk=board_2.pk)

    def test_should_generate_new_slug_when_slug_already_exists(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.slug = "dummy"  # we are faking the same slug here
        board.save()

        # when
        board = Board.objects.create(name="Dummy", category=self.category)

        # then
        self.assertEqual(board.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        # when
        board = Board.objects.create(name="Dummy", category=self.category, slug="-")

        # then
        self.assertEqual(board.slug, "dummy")


class TestCategory(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")

    def test_model_string_names(self):
        category = Category.objects.create(name="Science")

        self.assertEqual(str(category), "Science")

    def test_should_create_new_category_with_slug(self):
        # when
        category = Category.objects.create(name="Science")

        # then
        self.assertEqual(category.slug, "science")

    def test_should_keep_existing_slug_when_changing_name(self):
        category = Category.objects.create(name="Science")

        # when
        category.name = "Politics"
        category.save()

        # then
        category.refresh_from_db()
        self.assertEqual(category.slug, "science")

    def test_should_generate_new_slug_when_slug_already_exists(self):
        # given
        category = Category.objects.create(name="Science")
        category.slug = "dummy"  # we are faking the same slug here
        category.save()

        # when
        category = Category.objects.create(name="Dummy")

        # then
        self.assertEqual(category.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        # when
        category = Category.objects.create(name="Science", slug="-")

        # then
        self.assertEqual(category.slug, "science")

    def test_should_not_allow_to_update_slug_to_hyphen(self):
        # given
        category = Category.objects.create(name="Science")

        # when
        category.slug = "-"
        category.save()

        # then
        category.refresh_from_db()
        self.assertEqual(category.slug, "science-1")


@patch(MODELS_PATH + ".Setting.objects.get_setting", new=my_get_setting)
class TestMessage(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")

    def setUp(self) -> None:
        category = Category.objects.create(name="Science")

        self.board = Board.objects.create(name="Physics", category=category)
        self.child_board = Board.objects.create(
            name="Chemistry", category=category, parent_board=self.board
        )
        self.topic = Topic.objects.create(subject="Mysteries", board=self.board)

    def test_model_string_names(self):
        message = Message.objects.create(
            topic=self.topic, user_created=self.user, message="What is dark energy?"
        )

        self.assertEqual(str(message), str(message.pk))

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

    def test_should_return_url_first_page(self):
        # given
        message = Message.objects.create(
            topic=self.topic, user_created=self.user, message="What is dark energy?"
        )
        url = message.get_absolute_url()

        # then
        self.assertURLEqual(
            url,
            reverse(
                "aa_forum:forum_topic",
                args=(
                    self.topic.board.category.slug,
                    self.topic.board.slug,
                    self.topic.slug,
                ),
            )
            + f"#message-{message.pk}",
        )

    def test_should_return_url_other_pages(self):
        # given
        create_fake_messages(self.topic, 9)
        message = self.topic.messages.order_by("time_posted").last()
        url = message.get_absolute_url()

        # then
        self.assertURLEqual(
            url,
            reverse(
                "aa_forum:forum_topic",
                args=(
                    self.topic.board.category.slug,
                    self.topic.board.slug,
                    self.topic.slug,
                    2,
                ),
            )
            + f"#message-{message.pk}",
        )


class TestTopic(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")

    def setUp(self) -> None:
        category = Category.objects.create(name="Science")

        self.board = Board.objects.create(name="Physics", category=category)
        self.child_board = Board.objects.create(
            name="Chemistry", category=category, parent_board=self.board
        )

    def test_model_string_names(self):
        topic = Topic.objects.create(subject="Mysteries", board=self.board)

        self.assertEqual(str(topic), "Mysteries")

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

    def test_should_update_last_message_normal_from_child_board(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.child_board)
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

    def test_should_return_url(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)

        # when
        url = topic.get_absolute_url()

        # then
        self.assertURLEqual(
            url,
            reverse("aa_forum:forum_topic", args=["science", "physics", "mysteries"]),
        )

    def test_should_generate_new_slug_when_slug_already_exists(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        topic.slug = "dummy"  # we are faking the same slug here
        topic.save()

        # when
        topic = Topic.objects.create(subject="Dummy", board=self.board)

        # then
        self.assertEqual(topic.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        # when
        topic = Topic.objects.create(subject="Dummy", board=self.board, slug="-")

        # then
        self.assertEqual(topic.slug, "dummy")
