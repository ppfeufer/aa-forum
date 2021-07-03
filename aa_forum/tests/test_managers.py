from django.contrib.auth.models import Group
from django.test import TestCase

from ..models import Board, Category, Topic
from .utils import create_fake_message, create_fake_user


class TestBoard(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(name="Superhero")
        cls.category = Category.objects.create(name="Science")

    def setUp(self) -> None:
        self.user = create_fake_user(1001, "Bruce Wayne")

    def test_should_return_board_with_no_groups(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        # when
        result = Board.objects.user_has_access(self.user)
        # then
        self.assertIn(board, result)

    def test_should_return_board_for_group_member(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)
        self.user.groups.add(self.group)
        # when
        result = Board.objects.user_has_access(self.user)
        # then
        self.assertIn(board, result)

    def test_should_not_return_board_for_non_group_member(self):
        # given
        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)
        # when
        result = Board.objects.user_has_access(self.user)
        # then
        self.assertNotIn(board, result)


class TestTopic(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(name="Superhero")
        cls.category = Category.objects.create(name="Science")

    def setUp(self) -> None:
        self.user = create_fake_user(1001, "Bruce Wayne")
        self.board = Board.objects.create(name="Physics", category=self.category)

    def test_should_return_topic_normally_1(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic, self.user)
        # when
        result = Topic.objects.get_from_slugs(
            category_slug=str(self.category.slug),
            board_slug=str(self.board.slug),
            topic_slug=str(topic.slug),
            user=self.user,
        )
        # then
        self.assertEqual(result, topic)

    def test_should_return_topic_normally_2(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic, self.user)
        # when
        result = Topic.objects.get_from_slugs(
            self.category.slug,
            self.board.slug,
            topic.slug,
            self.user,
        )
        # then
        self.assertEqual(result, topic)

    def test_should_return_none_if_not_found_1(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic, self.user)
        # when
        result = Topic.objects.get_from_slugs(
            category_slug=self.category.slug,
            board_slug=self.board.slug,
            topic_slug="invalid",
            user=self.user,
        )
        # then
        self.assertIsNone(result)

    def test_should_return_none_if_not_found_2(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic, self.user)
        # when
        result = Topic.objects.get_from_slugs(
            category_slug=self.category.slug,
            board_slug="invalid",
            topic_slug=topic.slug,
            user=self.user,
        )
        # then
        self.assertIsNone(result)

    def test_should_return_none_if_not_found_3(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_message(topic, self.user)
        # when
        result = Topic.objects.get_from_slugs(
            category_slug="invalid",
            board_slug=self.board.slug,
            topic_slug=topic.slug,
            user=self.user,
        )
        # then
        self.assertIsNone(result)

    def test_should_return_restricted_topic_for_group_members(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        self.user.groups.add(self.group)
        self.board.groups.add(self.group)
        create_fake_message(topic, self.user)
        # when
        result = Topic.objects.get_from_slugs(
            self.category.slug,
            self.board.slug,
            topic.slug,
            self.user,
        )
        # then
        self.assertEqual(result, topic)

    def test_should_not_return_restricted_topic_for_non_group_members(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        self.board.groups.add(self.group)
        create_fake_message(topic, self.user)
        # when
        result = Topic.objects.get_from_slugs(
            self.category.slug,
            self.board.slug,
            topic.slug,
            self.user,
        )
        # then
        self.assertIsNone(result)
