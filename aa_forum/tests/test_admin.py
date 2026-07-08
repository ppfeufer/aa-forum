"""
Test for admin.py
"""

# Django
from django.test import RequestFactory

# Alliance Auth
from allianceauth.groupmanagement.models import Group

# AA Forum
from aa_forum.admin import (
    BaseReadOnlyAdminMixin,
    BoardAdmin,
    CategoryAdmin,
    TopicAdmin,
)
from aa_forum.models import Board, Category, Topic
from aa_forum.tests import BaseTestCase
from aa_forum.tests.utils import create_fake_messages, create_fake_user, random_id


class TestBaseReadOnlyAdminMixin(BaseTestCase):
    """
    Test the BaseReadOnlyAdminMixin class
    """

    def test_add_permission_is_denied(self):
        """
        Test if admin.BaseReadOnlyAdminMixin.has_add_permission returns False

        :return:
        :rtype:
        """

        request = RequestFactory().get(path="/")

        mixin = BaseReadOnlyAdminMixin()

        self.assertFalse(mixin.has_add_permission(request))

    def test_change_permission_is_denied(self):
        """
        Test if admin.BaseReadOnlyAdminMixin.has_change_permission returns False

        :return:
        :rtype:
        """

        request = RequestFactory().get(path="/")

        mixin = BaseReadOnlyAdminMixin()

        self.assertFalse(mixin.has_change_permission(request))

    def test_delete_permission_is_denied(self):
        """
        Test if admin.BaseReadOnlyAdminMixin.has_delete_permission returns False

        :return:
        :rtype:
        """

        request = RequestFactory().get(path="/")

        mixin = BaseReadOnlyAdminMixin()

        self.assertFalse(mixin.has_delete_permission(request))


class TestCategoryAdmin(BaseTestCase):
    """
    Test the CategoryAdmin class
    """

    def test_board_count_returns_zero_when_no_boards(self):
        """
        Ensure CategoryAdmin._board_count returns 0 when a category has no boards
        """

        category = Category.objects.create(name="Empty Category")

        admin_instance = CategoryAdmin(model=Category, admin_site=None)

        self.assertEqual(admin_instance._board_count(category), 0)

    def test_board_count_returns_number_of_boards(self):
        """
        Ensure CategoryAdmin._board_count returns correct number of boards
        """

        category = Category.objects.create(name="Filled Category")

        # create multiple boards attached to category
        Board.objects.create(category=category, name="Board 1")
        Board.objects.create(category=category, name="Board 2")

        admin_instance = CategoryAdmin(model=Category, admin_site=None)

        self.assertEqual(admin_instance._board_count(category), 2)


class TestBoardAdmin(BaseTestCase):
    """
    Test the BoardAdmin class
    """

    def test_groups_returns_empty_string_when_no_groups(self):
        """
        Ensure BoardAdmin._groups returns empty string when board has no groups
        """

        category = Category.objects.create(name="No Groups")
        board = Board.objects.create(name="Lonely Board", category=category)

        admin_instance = BoardAdmin(model=Board, admin_site=None)

        self.assertEqual(admin_instance._groups(board), "")

    def test_groups_returns_html_with_group_names(self):
        """
        Ensure BoardAdmin._groups returns HTML with group names separated by <br>
        """

        category = Category.objects.create(name="With Groups")
        board = Board.objects.create(name="Social Board", category=category)

        group_a = Group.objects.create(name="Alpha")
        group_b = Group.objects.create(name="Beta")

        board.groups.add(group_a)
        board.groups.add(group_b)

        admin_instance = BoardAdmin(model=Board, admin_site=None)

        result = admin_instance._groups(board)

        self.assertIn("Alpha", str(result))
        self.assertIn("Beta", str(result))
        self.assertIn("<br>", str(result))

    def test_topics_count_returns_zero_when_no_topics(self):
        """
        Ensure BoardAdmin._topics_count returns 0 when a board has no topics
        """

        category = Category.objects.create(name="No Topics")
        board = Board.objects.create(name="Quiet Board", category=category)

        admin_instance = BoardAdmin(model=Board, admin_site=None)

        self.assertEqual(admin_instance._topics_count(board), 0)

    def test_topics_count_returns_number_of_topics(self):
        """
        Ensure BoardAdmin._topics_count returns correct number of topics
        """

        category = Category.objects.create(name="Topicful")
        board = Board.objects.create(name="Active Board", category=category)

        Topic.objects.create(subject="One", board=board)
        Topic.objects.create(subject="Two", board=board)
        Topic.objects.create(subject="Three", board=board)

        admin_instance = BoardAdmin(model=Board, admin_site=None)

        self.assertEqual(admin_instance._topics_count(board), 3)


class TestTopicAdmin(BaseTestCase):
    """
    Test the TopicAdmin class
    """

    def test_messages_count_returns_zero_when_no_messages(self):
        """
        Ensure TopicAdmin._messages_count returns 0 when a topic has no messages
        """

        category = Category.objects.create(name="No Messages")
        board = Board.objects.create(name="Empty Board", category=category)
        topic = Topic.objects.create(subject="Silent", board=board)

        admin_instance = TopicAdmin(model=Topic, admin_site=None)

        self.assertEqual(admin_instance._messages_count(topic), 0)

    def test_messages_count_returns_number_of_messages(self):
        """
        Ensure TopicAdmin._messages_count returns correct number of messages
        """

        category = Category.objects.create(name="Messages")
        board = Board.objects.create(name="Loud Board", category=category)
        topic = Topic.objects.create(subject="Chatter", board=board)

        # ensure at least one valid user exists for message creation
        create_fake_user(character_id=random_id(), character_name="Poster")

        # create messages via helper which assigns valid users
        create_fake_messages(topic=topic, amount=2)

        admin_instance = TopicAdmin(model=Topic, admin_site=None)

        self.assertEqual(admin_instance._messages_count(topic), 2)
