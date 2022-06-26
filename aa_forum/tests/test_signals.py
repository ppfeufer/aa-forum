"""
Test our signals
"""

# Django
from django.contrib.auth.models import Group
from django.test import TestCase

# AA Forum
from aa_forum.models import Board, Category
from aa_forum.tests.utils import create_fake_user

MODELS_PATH = "aa_forum.models"


class TestBoard(TestCase):
    """
    Test Board signals
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = create_fake_user(1001, "Bruce Wayne")
        cls.group = Group.objects.create(name="Superhero")

    def setUp(self) -> None:
        self.category = Category.objects.create(name="Science")

    def test_should_set_parent_board_access_restriction(self):
        """
        Test that a child board inherits the groups from its parent board on creation
        :return:
        """

        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)
        board_2 = Board.objects.create(
            name="Thermal Theories", category=self.category, parent_board=board
        )

        self.assertEqual(list(board_2.groups.all()), [self.group])

    def test_should_set_child_board_access_restriction(self):
        """
        Test that a child parent board passes down its group restriction to its child on save
        :return:
        """

        board = Board.objects.create(name="Physics", category=self.category)
        board_2 = Board.objects.create(
            name="Thermal Theories", category=self.category, parent_board=board
        )
        board.groups.add(self.group)
        board.save()

        # result_groups = [groups for group in board_2.get_groups()]

        self.assertEqual(list(board_2.groups.all()), [self.group])
