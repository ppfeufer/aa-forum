"""
Tests for the admin views
"""

# Standard Library
import json

# Django
from django.test import TestCase
from django.urls import reverse

# AA Forum
from aa_forum.models import Board, Category
from aa_forum.tests.utils import create_fake_user

VIEWS_PATH = "aa_forum.views.admin"


class TestAdminViews(TestCase):
    """
    Test the admin views
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_fake_user(
            1001,
            "Bruce Wayne",
            permissions=["aa_forum.basic_access", "aa_forum.manage_forum"],
        )

    def test_should_delete_category(self):
        """
        Test should delete a category
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        self.client.force_login(self.user)

        # when
        res = self.client.get(
            reverse("aa_forum:admin_category_delete", args=[category.pk])
        )

        # then
        self.assertRedirects(res, reverse("aa_forum:admin_categories_and_boards"))
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_should_raise_404_when_delete_category_not_found(self):
        """
        Test should raise 404 when category not found on delete
        :return:
        """

        # given
        Category.objects.create(name="Category")
        self.client.force_login(self.user)

        # when
        res = self.client.get(reverse("aa_forum:admin_category_delete", args=[0]))

        # then
        self.assertEqual(res.status_code, 404)

    def test_should_delete_board(self):
        """
        Test should delete board
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        board = Board.objects.create(name="Board", category=category)
        self.client.force_login(self.user)

        # when
        res = self.client.get(
            reverse("aa_forum:admin_board_delete", args=[category.pk, board.pk])
        )

        # then
        self.assertRedirects(res, reverse("aa_forum:admin_categories_and_boards"))
        self.assertFalse(Board.objects.filter(pk=board.pk).exists())

    def test_should_raise_404_when_delete_board_not_found(self):
        """
        Test should raise 404 when board not found on delete
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        Board.objects.create(name="Board", category=category)
        self.client.force_login(self.user)

        # when
        res = self.client.get(
            reverse("aa_forum:admin_board_delete", args=[category.pk, 0])
        )

        # then
        self.assertEqual(res.status_code, 404)

    def test_should_save_categories_order(self):
        """
        Test should save category order
        :return:
        """

        # given
        category_1 = Category.objects.create(name="Category 1")
        category_2 = Category.objects.create(name="Category 2")
        self.client.force_login(self.user)

        # when
        res = self.client.post(
            reverse("aa_forum:admin_ajax_category_order"),
            data={
                "categories": json.dumps(
                    [
                        {"catId": category_1.pk, "catOrder": 1},
                        {"catId": category_2.pk, "catOrder": 2},
                    ]
                )
            },
        )

        # then
        self.assertListEqual(res.json(), [{"success": True}])
        category_1.refresh_from_db()
        self.assertEqual(category_1.order, 1)
        category_2.refresh_from_db()
        self.assertEqual(category_2.order, 2)

    def test_should_save_categories_order_and_handle_errors(self):
        """
        Test should save categories order and handle errors
        :return:
        """

        # given
        category_1 = Category.objects.create(name="Category 1")
        self.client.force_login(self.user)

        # when
        res = self.client.post(
            reverse("aa_forum:admin_ajax_category_order"),
            data={
                "categories": json.dumps(
                    [
                        {"catId": category_1.pk, "catOrder": 1},
                        {"catId": 0, "catOrder": 2},
                    ]
                )
            },
        )

        # then
        self.assertListEqual(res.json(), [{"success": True}])
        category_1.refresh_from_db()
        self.assertEqual(category_1.order, 1)

    def test_should_save_boards_order(self):
        """
        Test should save board order
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        board_1 = Board.objects.create(name="Board 1", category=category)
        board_2 = Board.objects.create(name="Board 2", category=category)
        self.client.force_login(self.user)

        # when
        res = self.client.post(
            reverse("aa_forum:admin_ajax_board_order"),
            data={
                "boards": json.dumps(
                    [
                        {"boardId": board_1.pk, "boardOrder": 1},
                        {"boardId": board_2.pk, "boardOrder": 2},
                    ]
                )
            },
        )

        # then
        self.assertListEqual(res.json(), [{"success": True}])
        board_1.refresh_from_db()
        self.assertEqual(board_1.order, 1)
        board_2.refresh_from_db()
        self.assertEqual(board_2.order, 2)

    def test_should_create_child_board(self):
        """
        Test shoulod create child board
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        board_1 = Board.objects.create(name="Board 1", category=category)
        self.client.force_login(self.user)

        # when
        res = self.client.get(
            reverse("aa_forum:admin_board_create_child", args=[category.pk, board_1.pk])
        )
        child_board = Board.objects.create(
            name="Child Board 1", category=category, parent_board=board_1
        )

        # then
        self.assertTrue(Board.objects.filter(pk=child_board.pk).exists())
        self.assertRedirects(res, reverse("aa_forum:admin_categories_and_boards"))

    def test_should_save_boards_order_and_handle_errors(self):
        """
        Test should save board order and handle errors
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        board_1 = Board.objects.create(name="Board 1", category=category)
        self.client.force_login(self.user)

        # when
        res = self.client.post(
            reverse("aa_forum:admin_ajax_board_order"),
            data={
                "boards": json.dumps(
                    [
                        {"boardId": board_1.pk, "boardOrder": 1},
                        {"boardId": 0, "boardOrder": 2},
                    ]
                )
            },
        )

        # then
        self.assertListEqual(res.json(), [{"success": True}])
        board_1.refresh_from_db()
        self.assertEqual(board_1.order, 1)
