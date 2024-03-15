"""
Test signals for the aa_forum app
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
    Test signals for Board
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
        cls.group = Group.objects.create(name="Superhero")

    def setUp(self) -> None:
        """
        Setup

        :return:
        :rtype:
        """

        self.category = Category.objects.create(name="Science")

    def test_should_set_parent_board_access_restriction(self):
        """
        Test that a child board inherits the groups from its parent board on creation

        :return:
        :rtype:
        """

        board = Board.objects.create(name="Physics", category=self.category)
        board.groups.add(self.group)
        board_2 = Board.objects.create(
            name="Thermal Theories", category=self.category, parent_board=board
        )

        self.assertEqual(first=list(board_2.groups.all()), second=[self.group])

    def test_should_set_child_board_access_restriction(self):
        """
        Test that a child parent board passes down its group restriction to
        its child on save

        :return:
        :rtype:
        """

        board = Board.objects.create(name="Physics", category=self.category)
        board_2 = Board.objects.create(
            name="Thermal Theories", category=self.category, parent_board=board
        )
        board.groups.add(self.group)
        board.save()

        self.assertEqual(first=list(board_2.groups.all()), second=[self.group])
