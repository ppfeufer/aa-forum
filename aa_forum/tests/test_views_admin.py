"""
Tests for the admin views
"""

# Standard Library
import json
from http import HTTPStatus

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
        """
        Set up user

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            permissions=["aa_forum.basic_access", "aa_forum.manage_forum"],
        )

    def test_should_delete_category(self):
        """
        Test should delete a category

        :return:
        :rtype:
        """

        # given
        category = Category.objects.create(name="Category")
        self.client.force_login(user=self.user)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:admin_category_delete", args=[category.pk])
        )

        # then
        self.assertRedirects(res, reverse("aa_forum:admin_categories_and_boards"))
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_should_raise_404_when_delete_category_not_found(self):
        """
        Test should raise 404 when category not found on delete

        :return:
        :rtype:
        """

        # given
        Category.objects.create(name="Category")
        self.client.force_login(user=self.user)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:admin_category_delete", args=[0])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.NOT_FOUND)

    def test_should_delete_board(self):
        """
        Test should delete board

        :return:
        :rtype:
        """

        # given
        category = Category.objects.create(name="Category")
        board = Board.objects.create(name="Board", category=category)
        self.client.force_login(user=self.user)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:admin_board_delete", args=[category.pk, board.pk]
            )
        )

        # then
        self.assertRedirects(
            response=res,
            expected_url=reverse(viewname="aa_forum:admin_categories_and_boards"),
        )
        self.assertFalse(expr=Board.objects.filter(pk=board.pk).exists())

    def test_should_raise_404_when_delete_board_not_found(self):
        """
        Test should raise 404 when board not found on delete

        :return:
        :rtype:
        """

        # given
        category = Category.objects.create(name="Category")
        Board.objects.create(name="Board", category=category)
        self.client.force_login(user=self.user)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:admin_board_delete", args=[category.pk, 0])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.NOT_FOUND)

    def test_should_save_categories_order(self):
        """
        Test should save category order

        :return:
        :rtype:
        """

        # given
        category_1 = Category.objects.create(name="Category 1")
        category_2 = Category.objects.create(name="Category 2")
        self.client.force_login(user=self.user)

        # when
        res = self.client.post(
            path=reverse(viewname="aa_forum:admin_ajax_category_order"),
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
        self.assertListEqual(list1=res.json(), list2=[{"success": True}])
        category_1.refresh_from_db()
        self.assertEqual(first=category_1.order, second=1)
        category_2.refresh_from_db()
        self.assertEqual(first=category_2.order, second=2)

    def test_should_save_categories_order_and_handle_errors(self):
        """
        Test should save the category order and handle errors

        :return:
        :rtype:
        """

        # given
        category_1 = Category.objects.create(name="Category 1")
        self.client.force_login(user=self.user)

        # when
        res = self.client.post(
            path=reverse(viewname="aa_forum:admin_ajax_category_order"),
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
        self.assertListEqual(list1=res.json(), list2=[{"success": True}])
        category_1.refresh_from_db()
        self.assertEqual(first=category_1.order, second=1)

    def test_should_save_boards_order(self):
        """
        Test should save board order

        :return:
        :rtype:
        """

        # given
        category = Category.objects.create(name="Category")
        board_1 = Board.objects.create(name="Board 1", category=category)
        board_2 = Board.objects.create(name="Board 2", category=category)
        self.client.force_login(user=self.user)

        # when
        res = self.client.post(
            path=reverse(viewname="aa_forum:admin_ajax_board_order"),
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
        self.assertListEqual(list1=res.json(), list2=[{"success": True}])
        board_1.refresh_from_db()
        self.assertEqual(first=board_1.order, second=1)
        board_2.refresh_from_db()
        self.assertEqual(first=board_2.order, second=2)

    def test_should_create_child_board(self):
        """
        Test should create child board

        :return:
        :rtype:
        """

        # given
        category = Category.objects.create(name="Category")
        board_1 = Board.objects.create(name="Board 1", category=category)
        self.client.force_login(user=self.user)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:admin_board_create_child",
                args=[category.pk, board_1.pk],
            )
        )
        child_board = Board.objects.create(
            name="Child Board 1", category=category, parent_board=board_1
        )

        # then
        self.assertTrue(Board.objects.filter(pk=child_board.pk).exists())
        self.assertRedirects(
            response=res,
            expected_url=reverse(viewname="aa_forum:admin_categories_and_boards"),
        )

    def test_should_save_boards_order_and_handle_errors(self):
        """
        Test should save board order and handle errors

        :return:
        :rtype:
        """

        # given
        category = Category.objects.create(name="Category")
        board_1 = Board.objects.create(name="Board 1", category=category)
        self.client.force_login(user=self.user)

        # when
        res = self.client.post(
            path=reverse(viewname="aa_forum:admin_ajax_board_order"),
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
        self.assertListEqual(list1=res.json(), list2=[{"success": True}])
        board_1.refresh_from_db()
        self.assertEqual(first=board_1.order, second=1)
