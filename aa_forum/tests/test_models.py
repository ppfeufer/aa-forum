"""
Tests for our models
"""

# Standard Library
import datetime as dt
from unittest.mock import patch

# Django
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

# AA Forum
from aa_forum.models import Board, get_sentinel_user
from aa_forum.tests.utils import (
    create_board,
    create_category,
    create_fake_messages,
    create_fake_user,
    create_last_message_seen,
    create_message,
    create_personal_message,
    create_setting,
    create_topic,
    my_get_setting,
)

MODELS_PATH = "aa_forum.models"


class TestGetSentinelUser(TestCase):
    def test_should_create_user_when_it_does_not_exist(self):
        # when
        user = get_sentinel_user()
        # then
        self.assertEqual(user.username, "deleted")

    def test_should_return_user_when_it_does(self):
        # given
        User.objects.create_user(username="deleted")
        # when
        user = get_sentinel_user()
        # then
        self.assertEqual(user.username, "deleted")


class TestBoard(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")
        cls.group = Group.objects.create(name="Superhero")

    def setUp(self) -> None:
        self.category = create_category(name="Science")

    def test_model_string_names(self):
        board = create_board(name="Physics", category=self.category)

        self.assertEqual(str(board), "Physics")

    def test_should_update_last_message_when_message_created(self):
        # given
        board = create_board(category=self.category)
        topic = create_topic(board=board)

        # when
        message = create_message(topic=topic, user_created=self.user)

        # then
        board.refresh_from_db()
        self.assertEqual(board.last_message, message)

    def test_should_update_last_message_when_message_created_in_child_board(self):
        # given
        board = create_board(category=self.category)
        child_board = create_board(category=self.category, parent_board=board)
        topic_board = create_topic(board=board)
        topic_child_board = create_topic(board=child_board)
        create_message(topic=topic_board, user_created=self.user)

        # when
        message_child_board = create_message(
            topic=topic_child_board, user_created=self.user
        )

        # then
        board.refresh_from_db()
        self.assertEqual(board.last_message, message_child_board)

    def test_should_return_url(self):
        # given
        board = create_board(category=self.category, name="Physics")

        # when
        url = board.get_absolute_url()

        # then
        self.assertURLEqual(
            url,
            reverse("aa_forum:forum_board", args=["science", "physics"]),
        )

    def test_should_return_board_with_no_groups(self):
        # given
        board = create_board(category=self.category)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board.pk)

        # then
        self.assertTrue(result)

    def test_should_return_board_for_group_member(self):
        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)

        self.user.groups.add(self.group)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board.pk)

        # then
        self.assertTrue(result)

    def test_should_return_child_board_for_group_member(self):
        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)

        self.user.groups.add(self.group)

        child_board = create_board(category=self.category, parent_board=board)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=child_board.pk)

        # then
        self.assertTrue(result)

    def test_should_not_return_board_for_non_group_member(self):
        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)

        with self.assertRaises(Board.DoesNotExist):
            Board.objects.user_has_access(self.user).get(pk=board.pk)

    def test_should_not_return_child_board_for_non_group_member(self):
        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)
        board_2 = create_board(category=self.category, parent_board=board)

        with self.assertRaises(Board.DoesNotExist):
            Board.objects.user_has_access(self.user).get(pk=board_2.pk)

    def test_should_generate_new_slug_when_slug_already_exists(self):
        # given
        board = create_board(category=self.category)
        board.slug = "dummy"  # we are faking the same slug here
        board.save()

        # when
        board = create_board(name="Dummy", category=self.category)

        # then
        self.assertEqual(board.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        # when
        board = create_board(name="Dummy", category=self.category, slug="-")

        # then
        self.assertEqual(board.slug, "dummy")

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_should_create_slug_with_name_matching_internal_url_prefix(self):
        # when
        category = create_board(name="-", category=self.category)

        # then
        self.assertEqual(category.slug, "hyphen")

    def test_should_handle_empty_board_slug(self):
        """
        Handling an empty slug that is returned by Board.save() when the board name is
        just special characters, which are getting stripped by slug generation
        :return:
        """

        # when
        board = create_board(name="@#$%", category=self.category)

        # then
        expected_slug = f"{board.__class__.__name__}-{board.pk}".lower()
        self.assertEqual(board.slug, expected_slug)


class TestCategory(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")

    def test_model_string_names(self):
        category = create_category(name="Science")

        self.assertEqual(str(category), "Science")

    def test_should_create_new_category_with_slug(self):
        # when
        category = create_category(name="Science")

        # then
        self.assertEqual(category.slug, "science")

    def test_should_keep_existing_slug_when_changing_name(self):
        category = create_category(name="Science")

        # when
        category.name = "Politics"
        category.save()

        # then
        category.refresh_from_db()
        self.assertEqual(category.slug, "science")

    def test_should_generate_new_slug_when_slug_already_exists(self):
        # given
        category = create_category(name="Science")
        category.slug = "dummy"  # we are faking the same slug here
        category.save()

        # when
        category = create_category(name="Dummy")

        # then
        self.assertEqual(category.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        # when
        category = create_category(name="Science", slug="-")

        # then
        self.assertEqual(category.slug, "science")

    def test_should_not_allow_to_update_slug_to_hyphen(self):
        # given
        category = create_category(name="Science")

        # when
        category.slug = "-"
        category.save()

        # then
        category.refresh_from_db()
        self.assertEqual(category.slug, "science-1")

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_should_create_new_category_with_name_matching_internal_url_prefix(self):
        # when
        category = create_category(name="-")

        # then
        self.assertEqual(category.slug, "hyphen")

    def test_should_handle_empty_category_slug(self):
        """
        Handling an empty slug that is returned by Category.save() when the category
        name is just special characters, which are getting stripped by slug generation
        :return:
        """

        # when
        category = create_category(name="@#$%")

        # then
        expected_slug = f"{category.__class__.__name__}-{category.pk}".lower()
        self.assertEqual(category.slug, expected_slug)


@patch(MODELS_PATH + ".Setting.objects.get_setting", new=my_get_setting)
class TestMessage(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")

    def setUp(self) -> None:
        category = create_category()

        self.board = create_board(category=category)
        self.child_board = create_board(category=category, parent_board=self.board)
        self.topic = create_topic(board=self.board)
        self.child_topic = create_topic(board=self.child_board)

    def test_model_string_names(self):
        # when
        message = create_message(topic=self.topic, user_created=self.user)

        # then
        self.assertEqual(str(message), str(message.pk))

    def test_should_update_first_and_last_messages_when_saving_1(self):
        # when
        message = create_message(topic=self.topic, user_created=self.user)

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.topic.last_message, message)
        self.assertEqual(self.topic.first_message, message)
        self.assertEqual(self.board.last_message, message)
        self.assertEqual(self.board.first_message, message)

    def test_should_update_first_and_last_messages_when_saving_2(self):
        # given
        message_1 = create_message(topic=self.topic, user_created=self.user)

        # when
        message_2 = create_message(topic=self.topic, user_created=self.user)

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.topic.last_message, message_2)
        self.assertEqual(self.topic.first_message, message_1)
        self.assertEqual(self.board.last_message, message_2)
        self.assertEqual(self.board.first_message, message_1)

    def test_should_update_first_and_last_messages_when_saving_3(self):
        # when
        message = create_message(topic=self.child_topic, user_created=self.user)

        # then
        self.child_topic.refresh_from_db()
        self.child_board.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.child_topic.last_message, message)
        self.assertEqual(self.child_topic.first_message, message)
        self.assertEqual(self.child_board.last_message, message)
        self.assertEqual(self.child_board.first_message, message)
        self.assertEqual(self.board.last_message, message)
        self.assertEqual(self.board.first_message, message)

    def test_should_update_first_and_last_messages_when_saving_4(self):
        # given
        message = create_message(topic=self.topic, user_created=self.user)

        # when
        child_message = create_message(topic=self.child_topic, user_created=self.user)

        # then
        self.child_topic.refresh_from_db()
        self.child_board.refresh_from_db()
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.child_topic.last_message, child_message)
        self.assertEqual(self.child_topic.first_message, child_message)
        self.assertEqual(self.child_board.last_message, child_message)
        self.assertEqual(self.child_board.first_message, child_message)
        self.assertEqual(self.topic.last_message, message)
        self.assertEqual(self.topic.last_message, message)
        self.assertEqual(self.board.last_message, child_message)
        self.assertEqual(self.board.first_message, child_message)

    def test_should_update_first_and_last_messages_when_saving_5(self):
        # given
        message_1 = create_message(topic=self.topic, user_created=self.user)
        message_2 = create_message(topic=self.topic, user_created=self.user)

        # when
        child_message_1 = create_message(topic=self.child_topic, user_created=self.user)
        child_message_2 = create_message(topic=self.child_topic, user_created=self.user)

        # then
        self.child_topic.refresh_from_db()
        self.child_board.refresh_from_db()
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.child_topic.first_message, child_message_1)
        self.assertEqual(self.child_topic.last_message, child_message_2)
        self.assertEqual(self.child_board.first_message, child_message_1)
        self.assertEqual(self.child_board.last_message, child_message_2)
        self.assertEqual(self.topic.first_message, message_1)
        self.assertEqual(self.topic.last_message, message_2)
        self.assertEqual(self.board.first_message, child_message_1)
        self.assertEqual(self.board.last_message, child_message_2)

    def test_should_update_message_references_when_deleting_last_message_1(self):
        # given
        message_1 = create_message(topic=self.topic, user_created=self.user)
        message_2 = create_message(topic=self.topic, user_created=self.user)

        # when
        message_2.delete()

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.topic.last_message, message_1)
        self.assertEqual(self.topic.first_message, message_1)
        self.assertEqual(self.board.last_message, message_1)
        self.assertEqual(self.board.first_message, message_1)

    def test_should_update_message_references_when_deleting_last_message_2(self):
        # given
        message_1 = create_message(topic=self.topic, user_created=self.user)
        message_2 = create_message(topic=self.topic, user_created=self.user)

        # when
        message_1.delete()

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.topic.last_message, message_2)
        self.assertEqual(self.topic.first_message, message_2)
        self.assertEqual(self.board.last_message, message_2)
        self.assertEqual(self.board.first_message, message_2)

    def test_should_update_message_references_when_deleting_last_message_3(self):
        # given
        message = create_message(topic=self.topic, user_created=self.user)
        child_message = create_message(topic=self.child_topic, user_created=self.user)

        # when
        child_message.delete()

        # then
        self.topic.refresh_from_db()
        self.child_topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(self.topic.last_message, message)
        self.assertEqual(self.topic.first_message, message)
        self.assertIsNone(self.child_topic.last_message)
        self.assertIsNone(self.child_topic.first_message)
        self.assertEqual(self.board.last_message, message)
        self.assertEqual(self.board.first_message, message)

    def test_should_update_message_references_when_deleting_last_message_4(self):
        # given
        message = create_message(topic=self.topic, user_created=self.user)
        child_message = create_message(topic=self.child_topic, user_created=self.user)

        # when
        message.delete()

        # then
        self.topic.refresh_from_db()
        self.child_topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertIsNone(self.topic.last_message)
        self.assertIsNone(self.topic.first_message)
        self.assertEqual(self.child_topic.last_message, child_message)
        self.assertEqual(self.child_topic.first_message, child_message)
        self.assertEqual(self.board.last_message, child_message)
        self.assertEqual(self.board.first_message, child_message)

    def test_should_reset_message_references_when_deleting_last_message_1(self):
        # given
        message = create_message(topic=self.topic, user_created=self.user)

        # when
        message.delete()

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertIsNone(self.topic.last_message)
        self.assertIsNone(self.topic.first_message)
        self.assertIsNone(self.board.last_message)
        self.assertIsNone(self.board.first_message)

    def test_should_return_url_first_page(self):
        # given
        message = create_message(topic=self.topic, user_created=self.user)
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
        category = create_category(name="Science")

        self.board = create_board(category=category, name="Physics")
        self.child_board = create_board(category=category, parent_board=self.board)

    def test_model_string_names(self):
        topic = create_topic(subject="Mysteries", board=self.board)

        self.assertEqual(str(topic), "Mysteries")

    def test_should_update_last_message_when_message_is_created(self):
        # given
        topic = create_topic(subject="Mysteries", board=self.board)

        # when
        message = create_message(topic=topic, user_created=self.user)

        # then
        topic.refresh_from_db()
        self.assertEqual(topic.last_message, message)

    def test_should_update_last_message_when_message_is_created_child_board(self):
        # given
        child_topic = create_topic(board=self.child_board)

        # when
        child_message = create_message(topic=child_topic, user_created=self.user)

        # then
        child_topic.refresh_from_db()
        self.assertEqual(child_topic.last_message, child_message)

    def test_should_update_last_message_after_topic_deletion(self):
        # given
        topic_1 = create_topic(board=self.board)
        topic_2 = create_topic(board=self.board)
        my_now = now() - dt.timedelta(hours=1)

        with patch("django.utils.timezone.now", lambda: my_now):
            message_1 = create_message(topic=topic_1, user_created=self.user)

        message_2 = create_message(topic=topic_2, user_created=self.user)

        self.board.refresh_from_db()
        self.assertEqual(self.board.last_message, message_2)

        # when
        topic_2.delete()

        # then
        self.board.refresh_from_db()
        self.assertEqual(self.board.last_message, message_1)

    def test_should_not_update_last_message_after_topic_deletion(self):
        # given
        topic_1 = create_topic(board=self.board)
        topic_2 = create_topic(board=self.board)
        my_now = now() - dt.timedelta(hours=1)

        with patch("django.utils.timezone.now", lambda: my_now):
            create_message(topic=topic_1, user_created=self.user)

        message_2 = create_message(topic=topic_2, user_created=self.user)

        self.board.refresh_from_db()
        self.assertEqual(self.board.last_message, message_2)

        # when
        topic_1.delete()

        # then
        self.board.refresh_from_db()
        self.assertEqual(self.board.last_message, message_2)

    def test_should_return_url(self):
        # given
        topic = create_topic(subject="Mysteries", board=self.board)

        # when
        url = topic.get_absolute_url()

        # then
        self.assertURLEqual(
            url,
            reverse("aa_forum:forum_topic", args=["science", "physics", "mysteries"]),
        )

    def test_should_generate_new_slug_when_slug_already_exists(self):
        # given
        topic = create_topic(board=self.board)
        topic.slug = "dummy"  # we are faking the same slug here
        topic.save()

        # when
        topic = create_topic(subject="Dummy", board=self.board)

        # then
        self.assertEqual(topic.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        # when
        topic = create_topic(subject="Dummy", board=self.board, slug="-")

        # then
        self.assertEqual(topic.slug, "dummy")

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_should_create_slug_with_name_matching_internal_url_prefix(self):
        # when
        topic = create_topic(subject="-", board=self.board)

        # then
        self.assertEqual(topic.slug, "hyphen")

    def test_should_handle_empty_topic_slug(self):
        """
        Handling an empty slug that is returned by Topic.save() when the topic
        name is just special characters, which are getting stripped by slug generation
        :return:
        """

        # when
        topic = create_topic(subject="@#$%", board=self.board)

        # then
        expected_slug = f"{topic.__class__.__name__}-{topic.pk}".lower()
        self.assertEqual(topic.slug, expected_slug)


class TestPersonalMessage(TestCase):
    def test_str(self):
        # with
        message = create_personal_message(subject="Subject")

        # then
        self.assertEqual(str(message), "Subject")

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_can_create_personal_message(self):
        # with
        message = create_personal_message(subject="subject")

        # then
        self.assertEqual(message.subject, "subject")

    def test_should_generate_new_slug_when_slug_already_exists(self):
        # given
        message_1 = create_personal_message()
        message_1.slug = "dummy"  # we are faking the same slug here
        message_1.save()

        # when
        message_2 = create_personal_message(subject="Dummy")

        # then
        self.assertEqual(message_2.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        # when
        message = create_personal_message(subject="Dummy", slug="-")

        # then
        self.assertEqual(message.slug, "dummy")

    def test_should_create_slug_with_name_matching_internal_url_prefix(self):
        # when
        message = create_personal_message(subject="-")

        # then
        self.assertEqual(message.slug, "hyphen")


class LastMessageSeen(TestCase):
    def test_str(self):
        # given
        topic = create_topic(subject="Alpha")
        user = create_fake_user(1001, "Bruce Wayne")
        message_time = dt.datetime(2022, 1, 12, 17, 30)
        message = create_last_message_seen(
            topic=topic, user=user, message_time=message_time
        )

        # when/then
        result = str(message)

        # then
        self.assertEqual(result, "Alpha-Bruce_Wayne-2022-01-12 17:30:00")


class TestSetting(TestCase):
    def test_str(self):
        # given
        setting = create_setting(variable="alpha", value=1)

        # when/then
        self.assertEqual(str(setting), "alpha")
