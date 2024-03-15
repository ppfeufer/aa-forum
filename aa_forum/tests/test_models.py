"""
Tests for the models
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
from aa_forum.models import Board, Setting, Topic, get_sentinel_user
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
    Tests for the get_sentinel_user function
    """

    def test_should_create_user_when_it_does_not_exist(self):
        """
        Test should create the sentinel user when it doesn't exist

        :return:
        :rtype:
        """

        # when
        user = get_sentinel_user()

        # then
        self.assertEqual(first=user.username, second="deleted")

    def test_should_return_user_when_it_does(self):
        """
        Test should return the sentinel user when it does exist

        :return:
        :rtype:
        """

        # given
        User.objects.create_user(username="deleted")

        # when
        user = get_sentinel_user()

        # then
        self.assertEqual(first=user.username, second="deleted")


class TestBoard(TestCase):
    """
    Tests for Board
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.user = create_fake_user(character_id=1001, character_name="Bruce Wayne")
        cls.group = Group.objects.create(name="Superhero")

    def setUp(self) -> None:
        """
        Set up category

        :return:
        :rtype:
        """

        self.category = create_category(name="Science")

    def test_model_string_names(self):
        """
        Test model string names

        :return:
        :rtype:
        """

        board = create_board(name="Physics", category=self.category)

        self.assertEqual(first=str(board), second="Physics")

    def test_should_update_last_message_when_message_created(self):
        """
        Test should update last message when message created

        :return:
        :rtype:
        """

        # given
        board = create_board(category=self.category)
        topic = create_topic(board=board)

        # when
        message = create_message(topic=topic, user_created=self.user)

        # then
        board.refresh_from_db()
        self.assertEqual(first=board.last_message, second=message)

    def test_should_update_last_message_when_message_created_in_child_board(self):
        """
        Test should update last message when message created in child board

        :return:
        :rtype:
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
        self.assertEqual(first=board.last_message, second=message_child_board)

    def test_should_return_url(self):
        """
        Test should return board URL

        :return:
        :rtype:
        """

        # given
        board = create_board(category=self.category, name="Physics")

        # when
        url = board.get_absolute_url()

        # then
        self.assertURLEqual(
            url1=url,
            url2=reverse(viewname="aa_forum:forum_board", args=["science", "physics"]),
        )

    def test_should_return_board_with_no_groups(self):
        """
        Test should return board with no groups

        :return:
        :rtype:
        """

        # given
        board = create_board(category=self.category)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board.pk)

        # then
        self.assertTrue(expr=result)

    def test_should_return_board_for_group_member(self):
        """
        Test should return board for group member

        :return:
        :rtype:
        """

        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)

        self.user.groups.add(self.group)

        # when
        result = Board.objects.user_has_access(self.user).get(pk=board.pk)

        # then
        self.assertTrue(expr=result)

    def test_should_return_child_board_for_group_member(self):
        """
        Test should return restricted child board for group member

        :return:
        :rtype:
        """

        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)

        self.user.groups.add(self.group)

        child_board = create_board(category=self.category, parent_board=board)

        # when
        result = Board.objects.user_has_access(user=self.user).get(pk=child_board.pk)

        # then
        self.assertTrue(expr=result)

    def test_should_not_return_board_for_non_group_member(self):
        """
        Test should not return restricted board for non group member

        :return:
        :rtype:
        """

        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)

        with self.assertRaises(expected_exception=Board.DoesNotExist):
            Board.objects.user_has_access(user=self.user).get(pk=board.pk)

    def test_should_not_return_child_board_for_non_group_member(self):
        """
        Test should not return restricted child board for non group member

        :return:
        :rtype:
        """

        # given
        board = create_board(category=self.category)
        board.groups.add(self.group)
        board_2 = create_board(category=self.category, parent_board=board)

        with self.assertRaises(expected_exception=Board.DoesNotExist):
            Board.objects.user_has_access(user=self.user).get(pk=board_2.pk)

    def test_should_generate_new_slug_when_slug_already_exists(self):
        """
        Test should generate a new slug when board-slug already exists

        :return:
        :rtype:
        """

        # given
        board = create_board(category=self.category)
        board.slug = "dummy"  # we are faking the same slug here
        board.save()

        # when
        board = create_board(name="Dummy", category=self.category)

        # then
        self.assertEqual(first=board.slug, second="dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        """
        Test should not allow creation with hyphen slugs (reserved for admin pages)

        :return:
        :rtype:
        """

        # when
        board = create_board(name="Dummy", category=self.category, slug="-")

        # then
        self.assertEqual(first=board.slug, second="dummy")

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_should_create_slug_with_name_matching_internal_url_prefix(self):
        """
        Test should create slug with name matching internal URL prefix

        :return:
        :rtype:
        """

        # when
        category = create_board(name="-", category=self.category)

        # then
        self.assertEqual(first=category.slug, second="hyphen")

    def test_should_handle_empty_board_slug(self):
        """
        Handling an empty slug returned by Board.save() when the board
        name is just special characters, which are getting stripped by slug generation

        :return:
        :rtype:
        """

        # when
        board = create_board(name="@#$%", category=self.category)

        # then
        expected_slug = f"{board.__class__.__name__}-{board.pk}".lower()
        self.assertEqual(first=board.slug, second=expected_slug)

    def test_should_translate_nonlatin_letters_in_slug(self):
        """
        Test that non latin letters in a slug are translated

        :return:
        :rtype:
        """

        board = create_board(name="дрифтерке, рорки в док", category=self.category)

        expected_slug = "drifterke-rorki-v-dok"

        self.assertEqual(first=board.slug, second=expected_slug)

    def test_should_create_topic_in_board(self):
        """
        Test that a new topic is created in a given board

        :return:
        :rtype:
        """

        board = create_board(name="Test Board", category=self.category)
        topic = board.new_topic(subject="Foobar", message="Foobar", user=self.user)

        topic_last_created = Topic.objects.last()

        self.assertEqual(first=topic.subject, second=topic_last_created.subject)
        self.assertEqual(first=topic.board_id, second=topic_last_created.board_id)

    def test_should_raise_topic_already_exists_exception(self):
        """
        Test that the Board.TopicAlreadyExists exception is raised

        :return:
        :rtype:
        """

        board = create_board(name="Test Board", category=self.category)
        existing_topic = board.new_topic(
            subject="Foobar", message="Foobar", user=self.user
        )

        expected_exception = Board.TopicAlreadyExists

        existing_topic_url = reverse(
            viewname="aa_forum:forum_topic",
            kwargs={
                "category_slug": board.category.slug,
                "board_slug": board.slug,
                "topic_slug": existing_topic.slug,
            },
        )

        expected_message = f'<h4>Warning!</h4><p>There is already a topic with the exact same subject in this board.</p><p>See here: <a href="{existing_topic_url}">{existing_topic.subject}</a></p>'  # pylint: disable=line-too-long

        with self.assertRaises(expected_exception=expected_exception):
            board.new_topic(subject="Foobar", message="Foobar", user=self.user)

        with self.assertRaisesMessage(
            expected_exception=expected_exception, expected_message=expected_message
        ):
            board.new_topic(subject="Foobar", message="Foobar", user=self.user)


class TestCategory(TestCase):
    """
    Tests for Category
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = create_fake_user(character_id=1001, character_name="Bruce Wayne")

    def test_model_string_names(self):
        """
        Test model string names

        :return:
        :rtype:
        """

        category = create_category(name="Science")

        self.assertEqual(first=str(category), second="Science")

    def test_should_create_new_category_with_slug(self):
        """
        Test should create a new category with slug

        :return:
        :rtype:
        """

        # when
        category = create_category(name="Science")

        # then
        self.assertEqual(first=category.slug, second="science")

    def test_should_keep_existing_slug_when_changing_name(self):
        """
        Test should keep existing slug when changing name

        :return:
        :rtype:
        """

        category = create_category(name="Science")

        # when
        category.name = "Politics"
        category.save()

        # then
        category.refresh_from_db()
        self.assertEqual(first=category.slug, second="science")

    def test_should_generate_new_slug_when_slug_already_exists(self):
        """
        Test should generate a new slug when slug already exists

        :return:
        :rtype:
        """

        # given
        category = create_category(name="Science")
        category.slug = "dummy"  # we are faking the same slug here
        category.save()

        # when
        category = create_category(name="Dummy")

        # then
        self.assertEqual(first=category.slug, second="dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        """
        Test should not allow creation with hyphen slugs (reserved for admin pages)

        :return:
        :rtype:
        """

        # when
        category = create_category(name="Science", slug="-")

        # then
        self.assertEqual(first=category.slug, second="science")

    def test_should_not_allow_to_update_slug_to_hyphen(self):
        """
        Test should not allow updating slug to hyphen (reserved for admin pages)

        :return:
        :rtype:
        """

        # given
        category = create_category(name="Science")

        # when
        category.slug = "-"
        category.save()

        # then
        category.refresh_from_db()
        self.assertEqual(first=category.slug, second="science-1")

    def test_should_translate_nonlatin_letters_in_slug(self):
        """
        Test that non latin letters in a slug are translated

        :return:
        :rtype:
        """

        category = create_category(name="дрифтерке, рорки в док")

        expected_slug = "drifterke-rorki-v-dok"

        self.assertEqual(first=category.slug, second=expected_slug)

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_should_create_new_category_with_name_matching_internal_url_prefix(self):
        """
        Test should create a new category with name matching internal URL prefix

        :return:
        :rtype:
        """

        # when
        category = create_category(name="-")

        # then
        self.assertEqual(first=category.slug, second="hyphen")

    def test_should_handle_empty_category_slug(self):
        """
        Handling an empty slug returned by Category.save() when the category
        name is just special characters, which are getting stripped by slug generation

        :return:
        :rtype:
        """

        # when
        category = create_category(name="@#$%")

        # then
        expected_slug = f"{category.__class__.__name__}-{category.pk}".lower()
        self.assertEqual(first=category.slug, second=expected_slug)


@patch(MODELS_PATH + ".Setting.objects.get_setting", new=my_get_setting)
class TestMessage(TestCase):
    """
    Tests for Message
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup

        :return:
        :rtype:
        """
        super().setUpClass()

        cls.user = create_fake_user(character_id=1001, character_name="Bruce Wayne")

    def setUp(self) -> None:
        """
        Setup

        :return:
        :rtype:
        """

        category = create_category()

        self.board = create_board(category=category)
        self.child_board = create_board(category=category, parent_board=self.board)
        self.topic = create_topic(board=self.board)
        self.child_topic = create_topic(board=self.child_board)

    def test_model_string_names(self):
        """
        Test model string names

        :return:
        :rtype:
        """

        # when
        message = create_message(topic=self.topic, user_created=self.user)

        # then
        self.assertEqual(first=str(message), second=str(message.pk))

    def test_should_update_first_and_last_messages_when_saving_1(self):
        """
        Test should update the first and last message when saving

        :return:
        :rtype:
        """

        # when
        message = create_message(topic=self.topic, user_created=self.user)

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(first=self.topic.last_message, second=message)
        self.assertEqual(first=self.topic.first_message, second=message)
        self.assertEqual(first=self.board.last_message, second=message)
        self.assertEqual(first=self.board.first_message, second=message)

    def test_should_update_first_and_last_messages_when_saving_2(self):
        """
        Test should update the first and last message when saving multiple messages

        :return:
        :rtype:
        """

        # given
        message_1 = create_message(topic=self.topic, user_created=self.user)

        # when
        message_2 = create_message(topic=self.topic, user_created=self.user)

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(first=self.topic.last_message, second=message_2)
        self.assertEqual(first=self.topic.first_message, second=message_1)
        self.assertEqual(first=self.board.last_message, second=message_2)
        self.assertEqual(first=self.board.first_message, second=message_1)

    def test_should_update_first_and_last_messages_when_saving_3(self):
        """
        Test should update the first and last message when saving

        :return:
        :rtype:
        """

        # when
        message = create_message(topic=self.child_topic, user_created=self.user)

        # then
        self.child_topic.refresh_from_db()
        self.child_board.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(first=self.child_topic.last_message, second=message)
        self.assertEqual(first=self.child_topic.first_message, second=message)
        self.assertEqual(first=self.child_board.last_message, second=message)
        self.assertEqual(first=self.child_board.first_message, second=message)
        self.assertEqual(first=self.board.last_message, second=message)
        self.assertEqual(first=self.board.first_message, second=message)

    def test_should_update_first_and_last_messages_when_saving_4(self):
        """
        Test should update the first and last message when saving

        :return:
        :rtype:
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
        self.assertEqual(first=self.child_topic.last_message, second=child_message)
        self.assertEqual(first=self.child_topic.first_message, second=child_message)
        self.assertEqual(first=self.child_board.last_message, second=child_message)
        self.assertEqual(first=self.child_board.first_message, second=child_message)
        self.assertEqual(first=self.topic.last_message, second=message)
        self.assertEqual(first=self.topic.last_message, second=message)
        self.assertEqual(first=self.board.last_message, second=child_message)
        self.assertEqual(first=self.board.first_message, second=child_message)

    def test_should_update_first_and_last_messages_when_saving_5(self):
        """
        Test should update the first and last message when saving

        :return:
        :rtype:
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
        self.assertEqual(first=self.child_topic.first_message, second=child_message_1)
        self.assertEqual(first=self.child_topic.last_message, second=child_message_2)
        self.assertEqual(first=self.child_board.first_message, second=child_message_1)
        self.assertEqual(first=self.child_board.last_message, second=child_message_2)
        self.assertEqual(first=self.topic.first_message, second=message_1)
        self.assertEqual(first=self.topic.last_message, second=message_2)
        self.assertEqual(first=self.board.first_message, second=child_message_1)
        self.assertEqual(first=self.board.last_message, second=child_message_2)

    def test_should_update_message_references_when_deleting_last_message_1(self):
        """
        Test should updat thee first and last message when deleting the last message

        :return:
        :rtype:
        """

        # given
        message_1 = create_message(topic=self.topic, user_created=self.user)
        message_2 = create_message(topic=self.topic, user_created=self.user)

        # when
        message_2.delete()

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(first=self.topic.last_message, second=message_1)
        self.assertEqual(first=self.topic.first_message, second=message_1)
        self.assertEqual(first=self.board.last_message, second=message_1)
        self.assertEqual(first=self.board.first_message, second=message_1)

    def test_should_update_message_references_when_deleting_last_message_2(self):
        """
        Test should update the first and last message when deleting the last message

        :return:
        :rtype:
        """

        # given
        message_1 = create_message(topic=self.topic, user_created=self.user)
        message_2 = create_message(topic=self.topic, user_created=self.user)

        # when
        message_1.delete()

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertEqual(first=self.topic.last_message, second=message_2)
        self.assertEqual(first=self.topic.first_message, second=message_2)
        self.assertEqual(first=self.board.last_message, second=message_2)
        self.assertEqual(first=self.board.first_message, second=message_2)

    def test_should_update_message_references_when_deleting_last_message_3(self):
        """
        Test should update the first and last message when deleting the last message

        :return:
        :rtype:
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
        self.assertEqual(first=self.topic.last_message, second=message)
        self.assertEqual(first=self.topic.first_message, second=message)
        self.assertIsNone(obj=self.child_topic.last_message)
        self.assertIsNone(obj=self.child_topic.first_message)
        self.assertEqual(first=self.board.last_message, second=message)
        self.assertEqual(first=self.board.first_message, second=message)

    def test_should_update_message_references_when_deleting_last_message_4(self):
        """
        Test should update the first and last message when deleting the last message

        :return:
        :rtype:
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
        self.assertIsNone(obj=self.topic.last_message)
        self.assertIsNone(obj=self.topic.first_message)
        self.assertEqual(first=self.child_topic.last_message, second=child_message)
        self.assertEqual(first=self.child_topic.first_message, second=child_message)
        self.assertEqual(first=self.board.last_message, second=child_message)
        self.assertEqual(first=self.board.first_message, second=child_message)

    def test_should_reset_message_references_when_deleting_last_message_1(self):
        """
        Test should reset message references when deleting the last message

        :return:
        :rtype:
        """

        # given
        message = create_message(topic=self.topic, user_created=self.user)

        # when
        message.delete()

        # then
        self.topic.refresh_from_db()
        self.board.refresh_from_db()
        self.assertIsNone(obj=self.topic.last_message)
        self.assertIsNone(obj=self.topic.first_message)
        self.assertIsNone(obj=self.board.last_message)
        self.assertIsNone(obj=self.board.first_message)

    def test_should_return_url_first_page(self):
        """
        Test should return URL to the first page

        :return:
        :rtype:
        """

        # given
        message = create_message(topic=self.topic, user_created=self.user)
        url = message.get_absolute_url()

        # then
        self.assertURLEqual(
            url1=url,
            url2=reverse(
                viewname="aa_forum:forum_topic",
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
        :rtype:
        """

        # given
        create_fake_messages(topic=self.topic, amount=9)
        message = self.topic.messages.order_by("time_posted").last()
        url = message.get_absolute_url()

        # then
        self.assertURLEqual(
            url1=url,
            url2=reverse(
                viewname="aa_forum:forum_topic",
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
    Tests for Topic
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.user = create_fake_user(character_id=1001, character_name="Bruce Wayne")

    def setUp(self) -> None:
        """
        Setup

        :return:
        :rtype:
        """

        category = create_category(name="Science")

        self.board = create_board(category=category, name="Physics")
        self.child_board = create_board(category=category, parent_board=self.board)

    def test_model_string_names(self):
        """
        Test model string names

        :return:
        :rtype:
        """

        topic = create_topic(subject="Mysteries", board=self.board)

        self.assertEqual(first=str(topic), second="Mysteries")

    def test_should_update_last_message_when_message_is_created(self):
        """
        Test should update the last message when a message is created

        :return:
        :rtype:
        """

        # given
        topic = create_topic(subject="Mysteries", board=self.board)

        # when
        message = create_message(topic=topic, user_created=self.user)

        # then
        topic.refresh_from_db()
        self.assertEqual(first=topic.last_message, second=message)

    def test_should_update_last_message_when_message_is_created_child_board(self):
        """
        Test should update the last message when a message is created in child board

        :return:
        :rtype:
        """

        # given
        child_topic = create_topic(board=self.child_board)

        # when
        child_message = create_message(topic=child_topic, user_created=self.user)

        # then
        child_topic.refresh_from_db()
        self.assertEqual(first=child_topic.last_message, second=child_message)

    def test_should_update_last_message_after_topic_deletion(self):
        """
        Test should update last message when the topic is deleted

        :return:
        :rtype:
        """

        # given
        topic_1 = create_topic(board=self.board)
        topic_2 = create_topic(board=self.board)
        my_now = now() - dt.timedelta(hours=1)

        with patch("django.utils.timezone.now", lambda: my_now):
            message_1 = create_message(topic=topic_1, user_created=self.user)

        message_2 = create_message(topic=topic_2, user_created=self.user)

        self.board.refresh_from_db()
        self.assertEqual(first=self.board.last_message, second=message_2)

        # when
        topic_2.delete()

        # then
        self.board.refresh_from_db()
        self.assertEqual(first=self.board.last_message, second=message_1)

    def test_should_not_update_last_message_after_topic_deletion(self):
        """
        Test should not update the last message when the topic is deleted

        :return:
        :rtype:
        """

        # given
        topic_1 = create_topic(board=self.board)
        topic_2 = create_topic(board=self.board)
        my_now = now() - dt.timedelta(hours=1)

        with patch("django.utils.timezone.now", lambda: my_now):
            create_message(topic=topic_1, user_created=self.user)

        message_2 = create_message(topic=topic_2, user_created=self.user)

        self.board.refresh_from_db()
        self.assertEqual(first=self.board.last_message, second=message_2)

        # when
        topic_1.delete()

        # then
        self.board.refresh_from_db()
        self.assertEqual(first=self.board.last_message, second=message_2)

    def test_should_return_url(self):
        """
        Test should return topic URL

        :return:
        :rtype:
        """

        # given
        topic = create_topic(subject="Mysteries", board=self.board)

        # when
        url = topic.get_absolute_url()

        # then
        self.assertURLEqual(
            url1=url,
            url2=reverse(
                viewname="aa_forum:forum_topic",
                args=["science", "physics", "mysteries"],
            ),
        )

    def test_should_generate_new_slug_when_slug_already_exists(self):
        """
        Test should generate a new slug when slug already exists

        :return:
        :rtype:
        """

        # given
        topic = create_topic(board=self.board)
        topic.slug = "dummy"  # we are faking the same slug here
        topic.save()

        # when
        topic = create_topic(subject="Dummy", board=self.board)

        # then
        self.assertEqual(first=topic.slug, second="dummy-1")

    def test_should_not_allow_creation_with_hyphen_slugs(self):
        """
        Test should not allow creation with hyphen slugs

        :return:
        :rtype:
        """

        # when
        topic = create_topic(subject="Dummy", board=self.board, slug="-")

        # then
        self.assertEqual(first=topic.slug, second="dummy")

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_should_create_slug_with_name_matching_internal_url_prefix(self):
        """
        Test should create slug with name matching internal URL prefix

        :return:
        :rtype:
        """

        # when
        topic = create_topic(subject="-", board=self.board)

        # then
        self.assertEqual(first=topic.slug, second="hyphen")

    def test_should_handle_empty_topic_slug(self):
        """
        Handling an empty slug returned by Topic.save() when the topic
        name is just special characters, which are getting stripped by slug generation

        :return:
        :rtype:
        """

        # when
        topic = create_topic(subject="@#$%", board=self.board)

        # then
        expected_slug = f"{topic.__class__.__name__}-{topic.pk}".lower()
        self.assertEqual(first=topic.slug, second=expected_slug)

    def test_should_translate_nonlatin_letters_in_slug(self):
        """
        Test that non latin letters in a slug are translated to latin

        :return:
        :rtype:
        """

        topic = create_topic(subject="дрифтерке, рорки в док", board=self.board)

        expected_slug = "drifterke-rorki-v-dok"

        self.assertEqual(first=topic.slug, second=expected_slug)


class TestPersonalMessage(TestCase):
    """
    Tests for PersonalMessage
    """

    def test_str(self):
        """
        Test model string names

        :return:
        :rtype:
        """

        # with
        message = create_personal_message(subject="Subject")

        # then
        self.assertEqual(
            first=str(message), second='"Subject" from Bruce_Wayne to Lex_Luthor'
        )

    @patch(MODELS_PATH + ".INTERNAL_URL_PREFIX", "-")
    def test_can_create_personal_message(self):
        """
        Test can create a personal message

        :return:
        :rtype:
        """

        # with
        message = create_personal_message(subject="subject")

        # then
        self.assertEqual(first=message.subject, second="subject")


class LastMessageSeen(TestCase):
    """
    Tests for LastMessageSeen
    """

    def test_str(self):
        """
        Test model string names

        :return:
        :rtype:
        """

        # given
        topic = create_topic(subject="Alpha")
        user = create_fake_user(character_id=1001, character_name="Bruce Wayne")
        message_time = dt.datetime(year=2022, month=1, day=12, hour=17, minute=30)
        message = create_last_message_seen(
            topic=topic, user=user, message_time=message_time
        )

        # when/then
        result = str(message)

        # then
        self.assertEqual(first=result, second="Alpha-Bruce_Wayne-2022-01-12 17:30:00")


class TestSetting(TestCase):
    """
    Tests for Setting
    """

    def test_model_string_name(self):
        """
        Test model string name

        :return:
        :rtype:
        """

        # given
        setting = Setting.objects.get(pk=1)

        # when/then
        self.assertEqual(first=str(setting), second="Forum settings")

    def test_setting_save(self):
        """
        Test if there can't be another setting created
        and the existing setting is changed instead

        :return:
        :rtype:
        """

        # given
        messages_per_page = 25
        topics_per_page = 25
        setting = Setting(
            pk=2, messages_per_page=messages_per_page, topics_per_page=topics_per_page
        )
        setting.save()

        # then
        self.assertEqual(first=setting.pk, second=1)
        self.assertEqual(first=setting.messages_per_page, second=messages_per_page)
        self.assertEqual(first=setting.topics_per_page, second=topics_per_page)

    def test_setting_create(self):
        """
        Test that create method throwing the following exception
        django.db.utils.IntegrityError: (1062, "Duplicate entry '1' for key 'PRIMARY'")

        :return:
        :rtype:
        """

        # No pk given
        # with self.assertRaisesMessage(
        #     IntegrityError, "(1062, \"Duplicate entry '1' for key 'PRIMARY'\")"
        # ):
        with self.assertRaises(expected_exception=IntegrityError):
            create_setting()

    def test_setting_create_with_pk(self):
        """
        Test that create method throwing the following exception no matter the given pk
        django.db.utils.IntegrityError: (1062, "Duplicate entry '1' for key 'PRIMARY'")

        :return:
        :rtype:
        """

        # Set pk=2
        # with self.assertRaisesMessage(
        #     IntegrityError, "(1062, \"Duplicate entry '1' for key 'PRIMARY'\")"
        # ):
        with self.assertRaises(expected_exception=IntegrityError):
            create_setting(pk=2)

    def test_cannot_be_deleted(self):
        """
        Test that the settings object cannot be deleted

        :return:
        :rtype:
        """

        # given
        settings_old = Setting.objects.get(pk=1)

        # when
        Setting.objects.all().delete()

        # then
        settings = Setting.objects.all()
        settings_first = settings.first()

        # See that there is still only ONE Setting object
        self.assertEqual(first=settings.count(), second=1)

        # Check that both of our objects are identical
        self.assertEqual(first=settings_old, second=settings_first)
