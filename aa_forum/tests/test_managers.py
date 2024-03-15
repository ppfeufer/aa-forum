"""
Test managers
"""

# Django
from django.contrib.auth.models import Group
from django.test import TestCase

# AA Forum
from aa_forum.models import Board, Category, Topic
from aa_forum.tests.utils import create_fake_message, create_fake_user


class TestBoard(TestCase):
    """
    Tests for board manager
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and categories

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.group = Group.objects.create(name="Superhero")
        cls.category = Category.objects.create(name="Science")

    def setUp(self) -> None:
        """
        Set up user

        :return:
        :rtype:
        """

        self.user = create_fake_user(character_id=1001, character_name="Bruce Wayne")

    def test_should_return_board_with_no_groups(self):
        """
        Test should return board with no groups

        :return:
        :rtype:
        """

        # given
        board = Board.objects.create(name="Physics", category=self.category)

        # when
        result = Board.objects.user_has_access(user=self.user)

        # then
        self.assertIn(member=board, container=result)

    def test_should_return_board_for_group_member(self):
        """
        Test should return board for group member

        :return:
        :rtype:
        """

        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)
        self.user.groups.add(self.group)

        # when
        result = Board.objects.user_has_access(user=self.user)

        # then
        self.assertIn(member=board, container=result)

    def test_should_not_return_board_for_non_group_member(self):
        """
        Test should not return board for non group member

        :return:
        :rtype:
        """

        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)

        # when
        result = Board.objects.user_has_access(user=self.user)

        # then
        self.assertNotIn(member=board, container=result)


class TestTopic(TestCase):
    """
    Tests for topic manager
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and categories

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.group = Group.objects.create(name="Superhero")
        cls.category = Category.objects.create(name="Science")

    def setUp(self) -> None:
        """
        Set up user and board

        :return:
        :rtype:
        """

        self.user = create_fake_user(character_id=1001, character_name="Bruce Wayne")
        self.board = Board.objects.create(name="Physics", category=self.category)

    def test_should_return_topic_normally_1(self):
        """
        Test should return a topic normally (test with keyword arguments)

        :return:
        :rtype:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic=topic, user=self.user)

        # when
        result = Topic.objects.get_from_slugs(
            category_slug=str(self.category.slug),
            board_slug=str(self.board.slug),
            topic_slug=str(topic.slug),
            user=self.user,
        )

        # then
        self.assertEqual(first=result, second=topic)

    def test_should_return_topic_normally_2(self):
        """
        Test should return a topic normally (test with positional arguments)

        :return:
        :rtype:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic=topic, user=self.user)

        # when
        result = Topic.objects.get_from_slugs(
            self.category.slug,
            self.board.slug,
            topic.slug,
            self.user,
        )

        # then
        self.assertEqual(first=result, second=topic)

    def test_should_return_none_if_not_found_1(self):
        """
        Test should return None if not found (invalid topic slug)

        :return:
        :rtype:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic=topic, user=self.user)

        # when
        result = Topic.objects.get_from_slugs(
            category_slug=self.category.slug,
            board_slug=self.board.slug,
            topic_slug="invalid",
            user=self.user,
        )

        # then
        self.assertIsNone(obj=result)

    def test_should_return_none_if_not_found_2(self):
        """
        Test should return None if not found (invalid board slug)

        :return:
        :rtype:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic=topic, user=self.user)

        # when
        result = Topic.objects.get_from_slugs(
            category_slug=self.category.slug,
            board_slug="invalid",
            topic_slug=topic.slug,
            user=self.user,
        )

        # then
        self.assertIsNone(obj=result)

    def test_should_return_none_if_not_found_3(self):
        """
        Test should return None if not found (invalid category slug)

        :return:
        :rtype:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic=topic, user=self.user)

        # when
        result = Topic.objects.get_from_slugs(
            category_slug="invalid",
            board_slug=self.board.slug,
            topic_slug=topic.slug,
            user=self.user,
        )

        # then
        self.assertIsNone(obj=result)

    def test_should_return_restricted_topic_for_group_members(self):
        """
        Test should return a restricted topic for group members

        :return:
        :rtype:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        self.user.groups.add(self.group)
        self.board.groups.add(self.group)
        create_fake_message(topic=topic, user=self.user)

        # when
        result = Topic.objects.get_from_slugs(
            category_slug=self.category.slug,
            board_slug=self.board.slug,
            topic_slug=topic.slug,
            user=self.user,
        )

        # then
        self.assertEqual(first=result, second=topic)

    def test_should_not_return_restricted_topic_for_non_group_members(self):
        """
        Test should not return a restricted topic for non group members

        :return:
        :rtype:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        self.board.groups.add(self.group)
        create_fake_message(topic=topic, user=self.user)

        # when
        result = Topic.objects.get_from_slugs(
            category_slug=self.category.slug,
            board_slug=self.board.slug,
            topic_slug=topic.slug,
            user=self.user,
        )

        # then
        self.assertIsNone(obj=result)
