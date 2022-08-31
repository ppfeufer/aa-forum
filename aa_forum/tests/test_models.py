"""
Tests for our models
"""

# Standard Library
import datetime as dt
from unittest.mock import patch

# Django
from django.contrib.auth.models import Group, User
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

# AA Forum
from aa_forum.models import Board, Setting, get_sentinel_user
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
    """
    Tests for the sentinel user
    """

    def test_should_create_user_when_it_does_not_exist(self):
        """
        Test should create sentinel user when it doesn't exist
        :return:
        """

        # when
        user = get_sentinel_user()

        # then
        self.assertEqual(user.username, "deleted")

    def test_should_return_user_when_it_does(self):
        """
        Test should return sentinel user when it exists
        :return:
        """

        # given
        User.objects.create_user(username="deleted")

        # when
        user = get_sentinel_user()

        # then
        self.assertEqual(user.username, "deleted")


class TestBoard(TestCase):
    """
    Tests for the board model
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")
        cls.group = Group.objects.create(name="Superhero")

    def setUp(self) -> None:
        self.category = create_category(name="Science")

    def test_model_string_names(self):
        """
        Test model string names
        :return:
        """

        board = create_board(name="Physics", category=self.category)

        self.assertEqual(str(board), "Physics")

    def test_should_update_last_message_when_message_created(self):
        """
        Test should update last message when message created
        :return:
        """

        # given
        board = create_board(category=self.category)
        topic = create_topic(board=board)

        # when
        message = create_message(topic=topic, user_created=self.user)

        # then
        board.refresh_from_db()
        self.assertEqual(board.last_message, message)

    def test_should_update_last_message_when_message_created_in_child_board(self):
        """
        Test should update last message when message created in child board
        :return:
        """

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
        """
        Test should return board URL
        :return:
        """

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
        """
        Test should return board with no group restrictions
        :return:
        """

        # given
        board = create_board(category=self.category)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board.pk)

        # then
        self.assertTrue(result)

    def test_should_return_board_for_group_member(self):
        """
        Test should return restricted board for group member
        :return:
        """

        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)

        self.user.groups.add(self.group)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board.pk)

        # then
        self.assertTrue(result)

    def test_should_return_child_board_for_group_member(self):
        """
        Test should return restricted child board for group member
        :return:
        """

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
        """
        Test should not return restricted biard for non group member
        :return:
        """

        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)

        with self.assertRaises(Board.DoesNotExist):
            Board.objects.user_has_access(self.user).get(pk=board.pk)

    def test_should_not_return_child_board_for_non_group_member(self):
        """
        Test should nopt return restricted child board for none group member
        :return:
        """

        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)
        board_2 = create_board(category=self.category, parent_board=board)

        with self.assertRaises(Board.DoesNotExist):
            Board.objects.user_has_access(self.user).get(pk=board_2.pk)

    def test_should_generate_new_slug_when_slug_already_exists(self):
        """
        Test should generate new slug when board-slug already exists
        :return:
        """

        # given
        board = create_board(category=self.category)
        board.slug = "dummy"  # we are faking the same slug here
        board.save()

        # when
        board = create_board(name="Dummy", category=self.category)

        # then
        self.assertEqual(board.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        """
        Test should not allow creation with hyphen slugs (reserved for admin pages)
        :return:
        """

        # when
        board = create_board(name="Dummy", category=self.category, slug="-")

        # then
        self.assertEqual(board.slug, "dummy")

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_should_create_slug_with_name_matching_internal_url_prefix(self):
        """
        Test should create slug with name matching internal URL prefix
        :return:
        """

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
    """
    Tests for Category
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")

    def test_model_string_names(self):
        """
        Test model string names
        :return:
        """

        category = create_category(name="Science")

        self.assertEqual(str(category), "Science")

    def test_should_create_new_category_with_slug(self):
        """
        Tests should create new category with slug
        :return:
        """

        # when
        category = create_category(name="Science")

        # then
        self.assertEqual(category.slug, "science")

    def test_should_keep_existing_slug_when_changing_name(self):
        """
        Test should keep existing slug when changing category name
        :return:
        """

        category = create_category(name="Science")

        # when
        category.name = "Politics"
        category.save()

        # then
        category.refresh_from_db()
        self.assertEqual(category.slug, "science")

    def test_should_generate_new_slug_when_slug_already_exists(self):
        """
        Test should generate new slug when category slug already exists
        :return:
        """

        # given
        category = create_category(name="Science")
        category.slug = "dummy"  # we are faking the same slug here
        category.save()

        # when
        category = create_category(name="Dummy")

        # then
        self.assertEqual(category.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        """
        Test should not allow creation with hyphen slug
        :return:
        """

        # when
        category = create_category(name="Science", slug="-")

        # then
        self.assertEqual(category.slug, "science")

    def test_should_not_allow_to_update_slug_to_hyphen(self):
        """
        Test should not allow to update slug to hyphen
        :return:
        """

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
        """
        Test should create new category with name matching internal URL prefix
        :return:
        """

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
    """
    Tests for Message model
    """

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
        """
        Test model string names
        :return:
        """

        # when
        message = create_message(topic=self.topic, user_created=self.user)

        # then
        self.assertEqual(str(message), str(message.pk))

    def test_should_update_first_and_last_messages_when_saving_1(self):
        """
        Test should update first and last message when saving
        :return:
        """

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
        """
        Test should update first and last message when saving multiple messages
        :return:
        """

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
        """
        Test should update first and last message when saving
        :return:
        """

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
        """
        Test should update first and last message when saving
        :return:
        """

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
        """
        Test should update first and last message when saving
        :return:
        """

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
        """
        Test should update first and last message when deleting last message
        :return:
        """

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
        """
        Test should update first and last message when deleting last message
        :return:
        """

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
        """
        Test should update first and last message when deleting last message
        :return:
        """

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
        """
        Test should update first and last message when deleting last message
        :return:
        """

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
        """
        Test should reset message references when deleting last message
        :return:
        """

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
        """
        Test should return URL to first page
        :return:
        """

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
        """
        Test should return URL to other pages
        :return:
        """

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
    """
    Test for the Topic model
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(1001, "Bruce Wayne")

    def setUp(self) -> None:
        category = create_category(name="Science")

        self.board = create_board(category=category, name="Physics")
        self.child_board = create_board(category=category, parent_board=self.board)

    def test_model_string_names(self):
        """
        Test model string names
        :return:
        """

        topic = create_topic(subject="Mysteries", board=self.board)

        self.assertEqual(str(topic), "Mysteries")

    def test_should_update_last_message_when_message_is_created(self):
        """
        Test should update last message when message is created
        :return:
        """

        # given
        topic = create_topic(subject="Mysteries", board=self.board)

        # when
        message = create_message(topic=topic, user_created=self.user)

        # then
        topic.refresh_from_db()
        self.assertEqual(topic.last_message, message)

    def test_should_update_last_message_when_message_is_created_child_board(self):
        """
        Test should update last message when message is created in child board
        :return:
        """

        # given
        child_topic = create_topic(board=self.child_board)

        # when
        child_message = create_message(topic=child_topic, user_created=self.user)

        # then
        child_topic.refresh_from_db()
        self.assertEqual(child_topic.last_message, child_message)

    def test_should_update_last_message_after_topic_deletion(self):
        """
        Test should update last message when topic is deleted
        :return:
        """

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
        """
        Test should not update last message when topic is deleted
        :return:
        """

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
        """
        Test should return topic URL
        :return:
        """

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
        """
        Test should generate new slug when slug already exists
        :return:
        """

        # given
        topic = create_topic(board=self.board)
        topic.slug = "dummy"  # we are faking the same slug here
        topic.save()

        # when
        topic = create_topic(subject="Dummy", board=self.board)

        # then
        self.assertEqual(topic.slug, "dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        """
        Test should not allow creation with hyphen slugs
        :return:
        """

        # when
        topic = create_topic(subject="Dummy", board=self.board, slug="-")

        # then
        self.assertEqual(topic.slug, "dummy")

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_should_create_slug_with_name_matching_internal_url_prefix(self):
        """
        Test should create slug with name matching internel URL prefix
        :return:
        """

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
    """
    Tests for PersonalMessage model
    """

    def test_str(self):
        """
        Test model string names
        :return:
        """

        # with
        message = create_personal_message(subject="Subject")

        # then
        self.assertEqual(str(message), '"Subject" from Bruce_Wayne to Lex_Luthor')

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_can_create_personal_message(self):
        """
        Test can create personal message
        :return:
        """

        # with
        message = create_personal_message(subject="subject")

        # then
        self.assertEqual(message.subject, "subject")


class LastMessageSeen(TestCase):
    """
    Test for LastMessageSeen model
    """

    def test_str(self):
        """
        Test model string names
        :return:
        """

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
    """
    Tests for Settings model
    """

    def test_model_string_name(self):
        """
        Test model string name
        :return:
        """

        # given
        setting = Setting.objects.get(pk=1)

        # when/then
        self.assertEqual(str(setting), "Forum Settings")

    def test_setting_save(self):
        """
        Test if there can't be another setting created
        and the existing setting is changed instead
        :return:
        """

        # given
        messages_per_page = 25
        topics_per_page = 25
        setting = Setting(
            pk=2, messages_per_page=messages_per_page, topics_per_page=topics_per_page
        )
        setting.save()

        # then
        self.assertEqual(setting.pk, 1)
        self.assertEqual(setting.messages_per_page, messages_per_page)
        self.assertEqual(setting.topics_per_page, topics_per_page)

    def test_setting_create(self):
        """
        Test that create method throwing the following exception
        django.db.utils.IntegrityError: (1062, "Duplicate entry '1' for key 'PRIMARY'")
        :return:
        """

        # No pk given
        # with self.assertRaisesMessage(
        #     IntegrityError, "(1062, \"Duplicate entry '1' for key 'PRIMARY'\")"
        # ):
        with self.assertRaises(IntegrityError):
            create_setting()

    def test_setting_create_with_pk(self):
        """
        Test that create method throwing the following exception no matter the given pk
        django.db.utils.IntegrityError: (1062, "Duplicate entry '1' for key 'PRIMARY'")
        :return:
        """

        # Set pk=2
        # with self.assertRaisesMessage(
        #     IntegrityError, "(1062, \"Duplicate entry '1' for key 'PRIMARY'\")"
        # ):
        with self.assertRaises(IntegrityError):
            create_setting(pk=2)

    def test_cannot_be_deleted(self):
        """
        Test that the settings object cannot be deleted
        :return:
        """

        # given
        settings_old = Setting.objects.get(pk=1)

        # when
        Setting.objects.all().delete()

        # then
        settings = Setting.objects.all()
        settings_first = settings.first()

        # See if there is still only ONE Setting object
        self.assertEqual(settings.count(), 1)

        # Check if both of our objects are identical
        self.assertEqual(settings_old, settings_first)
