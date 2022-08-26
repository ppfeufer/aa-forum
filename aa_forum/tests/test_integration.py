"""
Integration and UI tests
"""

# Standard Library
import json
from unittest.mock import patch

# Third Party
import requests
from django_webtest import WebTest
from faker import Faker

# Django
from django.contrib.messages import get_messages
from django.urls import reverse

# AA Forum
from aa_forum.helper.text import string_cleanup
from aa_forum.models import Board, Category, Message, Setting, Topic, UserProfile
from aa_forum.tests.utils import (
    create_fake_message,
    create_fake_messages,
    create_fake_user,
)

fake = Faker()


class TestForumUI(WebTest):
    """
    Tests for the Forum UI
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_1001 = create_fake_user(
            1001, "Bruce Wayne", permissions=["aa_forum.basic_access"]
        )
        cls.user_1002 = create_fake_user(
            1002, "Peter Parker", permissions=["aa_forum.basic_access"]
        )
        cls.user_1003 = create_fake_user(1003, "Lex Luthor", permissions=[])

        cls.category = Category.objects.create(name="Science")
        cls.board = Board.objects.create(name="Physics", category=cls.category)
        cls.board_with_webhook = Board.objects.create(
            name="Chemistry",
            category=cls.category,
            discord_webhook="https://discord.com/webhook/",
        )
        cls.board_with_webhook_for_replies = Board.objects.create(
            name="Biology",
            category=cls.category,
            discord_webhook="https://discord.com/webhook/",
            use_webhook_for_replies=True,
        )

    def test_should_show_forum_index(self):
        """
        Test should show forum index
        :return:
        """

        # given
        self.app.set_user(self.user_1001)

        # when
        page = self.app.get(reverse("aa_forum:forum_index"))

        # then
        self.assertTemplateUsed(page, "aa_forum/view/forum/index.html")

    def test_should_not_show_forum_index(self):
        """
        Test should not show forum index
        :return:
        """

        # given
        self.app.set_user(self.user_1003)

        # when
        page = self.app.get(reverse("aa_forum:forum_index"))

        # then
        self.assertRedirects(page, "/account/login/?next=/forum/")

    def test_should_create_new_topic(self):
        """
        Test should create new topic
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(self.board.get_absolute_url())

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")
        form = page.forms["aa-forum-form-new-topic"]
        form["subject"] = "Recent Discoveries"
        form["message"] = "Energy of the Higgs boson"
        page = form.submit().follow()

        # then
        self.assertEqual(self.board.topics.count(), 1)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        new_topic = Topic.objects.last()
        self.assertEqual(new_topic.subject, "Recent Discoveries")
        new_message = Message.objects.last()
        self.assertEqual(new_message.message, "Energy of the Higgs boson")

    def test_should_return_cleaned_message_string_on_topic_creation(self):
        """
        Test should return a clean/sanitized message string when new topic is created
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(self.board.get_absolute_url())
        dirty_message = (
            'this is a script test. <script type="text/javascript">alert('
            "'test')</script>and this is style test. <style>.MathJax, "
            ".MathJax_Message, .MathJax_Preview{display: none}</style>end tests."
        )
        cleaned_message = string_cleanup(dirty_message)

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")
        form = page.forms["aa-forum-form-new-topic"]
        form["subject"] = "Message Cleanup Test"
        form["message"] = dirty_message
        page = form.submit().follow()

        # then
        new_message = Message.objects.last()
        self.assertEqual(new_message.message, cleaned_message)

    def test_should_not_create_new_topic_doe_to_subject_missing(self):
        """
        Test should not create new topic due to missing/empty subject
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(self.board.get_absolute_url())

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")
        form = page.forms["aa-forum-form-new-topic"]
        form["subject"] = ""  # Omitting mandatory field
        form["message"] = "Energy of the Higgs boson"
        page = form.submit()

        # then
        self.assertEqual(self.board.topics.count(), 0)  # No topic created
        self.assertTemplateUsed(page, "aa_forum/view/forum/new-topic.html")

        expected_message = (
            "<h4>Error!</h4>"
            "<p>Either subject or message is missing. "
            "Please make sure you enter both fields, "
            "as both fields are mandatory.</p>"
        )
        messages = list(page.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    def test_should_not_create_new_topic_doe_to_message_missing(self):
        """
        Test should not create new topic due to missing/empty message
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(self.board.get_absolute_url())

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")
        form = page.forms["aa-forum-form-new-topic"]
        form["subject"] = "Recent Discoveries"
        form["message"] = ""  # Omitting mandatory field
        page = form.submit()

        # then
        self.assertEqual(self.board.topics.count(), 0)  # No topic created
        self.assertTemplateUsed(page, "aa_forum/view/forum/new-topic.html")

        expected_message = (
            "<h4>Error!</h4>"
            "<p>Either subject or message is missing. "
            "Please make sure you enter both fields, "
            "as both fields are mandatory.</p>"
        )
        messages = list(page.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    def test_should_not_create_topic_that_already_exists(self):
        """
        Test should not re-create an existing topic
        :return:
        """

        # given
        board = Board.objects.create(name="Space", category=self.category)
        existing_topic = Topic.objects.create(subject="Mysteries", board=board)
        create_fake_messages(existing_topic, 15)

        existing_topic_url = reverse(
            "aa_forum:forum_topic",
            kwargs={
                "category_slug": existing_topic.board.category.slug,
                "board_slug": existing_topic.board.slug,
                "topic_slug": existing_topic.slug,
            },
        )

        self.app.set_user(self.user_1001)
        page = self.app.get(board.get_absolute_url())

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")
        form = page.forms["aa-forum-form-new-topic"]
        form["subject"] = "Mysteries"
        form["message"] = "Energy of the Higgs boson"
        page = form.submit()

        # then
        self.assertEqual(self.board.topics.count(), 0)
        self.assertTemplateUsed(page, "aa_forum/view/forum/new-topic.html")

        messages = list(page.context["messages"])
        expected_message = (
            "<h4>Warning!</h4>"
            "<p>There is already a topic with the exact same "
            "subject in this board.</p><p>See here: "
            f'<a href="{existing_topic_url}">'
            f"{existing_topic.subject}</a>"
            "</p>"
        )

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    @patch("requests.post")
    def test_should_post_to_webhook_on_create_reply_in_topic(self, mock_post):
        """
        Test should post to Discord webhook when reply in topic
        :return:
        """

        # given
        topic = Topic.objects.create(
            subject="Mysteries", board=self.board_with_webhook_for_replies
        )
        create_fake_messages(topic=topic, amount=5)
        self.app.set_user(self.user_1001)
        page = self.app.get(topic.get_absolute_url())

        # when
        form = page.forms["aa-forum-form-message-reply"]
        form["message"] = "What is dark matter?"
        page = form.submit().follow().follow()

        # then
        self.assertEqual(topic.messages.count(), 6)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        new_message = Message.objects.last()
        self.assertEqual(new_message.message, "What is dark matter?")

        info = {"test1": "value1", "test2": "value2"}
        requests.post(self.board_with_webhook.discord_webhook, data=json.dumps(info))
        mock_post.assert_called_with(
            self.board_with_webhook.discord_webhook, data=json.dumps(info)
        )

    @patch("requests.post")
    def test_should_post_to_discord_webhook_on_create_new_topic(self, mock_post):
        """
        Test should post to Discord webhook when new topic is created
        :param mock_post:
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(self.board_with_webhook.get_absolute_url())

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")

        form = page.forms["aa-forum-form-new-topic"]
        form["subject"] = "Recent Discoveries"
        form["message"] = "Energy of the Higgs boson"
        page = form.submit().follow()

        # then
        self.assertEqual(self.board_with_webhook.topics.count(), 1)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        new_topic = Topic.objects.last()
        self.assertEqual(new_topic.subject, "Recent Discoveries")
        new_message = Message.objects.last()
        self.assertEqual(new_message.message, "Energy of the Higgs boson")

        info = {"test1": "value1", "test2": "value2"}
        requests.post(self.board_with_webhook.discord_webhook, data=json.dumps(info))
        mock_post.assert_called_with(
            self.board_with_webhook.discord_webhook, data=json.dumps(info)
        )

    @patch("requests.post")
    def test_should_post_to_discord_webhook_with_image_on_create_new_topic(
        self, mock_post
    ):
        """
        Test should post to Discord webhook when new topic with image is created
        :param mock_post:
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(self.board_with_webhook.get_absolute_url())

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")

        form = page.forms["aa-forum-form-new-topic"]
        form["subject"] = "Recent Discoveries"
        form[
            "message"
        ] = "Energy of the Higgs boson <img src='/images/images/038/929/227/large/marc-bell-2a.jpg'>"  # , pylint: disable=line-too-long
        page = form.submit().follow()

        # then
        self.assertEqual(self.board_with_webhook.topics.count(), 1)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")

        new_topic = Topic.objects.last()
        self.assertEqual(new_topic.subject, "Recent Discoveries")

        new_message = Message.objects.last()
        self.assertEqual(
            new_message.message,
            "Energy of the Higgs boson <img src='/images/images/038/929/227/large/marc-bell-2a.jpg'>",  # , pylint: disable=line-too-long
        )

        info = {"test1": "value1", "test2": "value2"}
        requests.post(self.board_with_webhook.discord_webhook, data=json.dumps(info))
        mock_post.assert_called_with(
            self.board_with_webhook.discord_webhook, data=json.dumps(info)
        )

    @patch("requests.post")
    def test_should_post_to_discord_webhook_with_image_with_full_url_on_create_new_topic(  # , pylint: disable=line-too-long
        self, mock_post
    ):
        """
        Test should post to Discord webhook when new topic
        with image (full url) is created
        :param mock_post:
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(self.board_with_webhook.get_absolute_url())

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")

        form = page.forms["aa-forum-form-new-topic"]
        form["subject"] = "Recent Discoveries"
        form[
            "message"
        ] = "Energy of the Higgs boson <img src='https://cdnb.artstation.com/p/assets/images/images/038/929/227/large/marc-bell-2a.jpg'>"  # , pylint: disable=line-too-long
        page = form.submit().follow()

        # then
        self.assertEqual(self.board_with_webhook.topics.count(), 1)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        new_topic = Topic.objects.last()
        self.assertEqual(new_topic.subject, "Recent Discoveries")
        new_message = Message.objects.last()
        self.assertEqual(
            new_message.message,
            "Energy of the Higgs boson <img src='https://cdnb.artstation.com/p/assets/images/images/038/929/227/large/marc-bell-2a.jpg'>",  # , pylint: disable=line-too-long
        )

        info = {"test1": "value1", "test2": "value2"}
        requests.post(self.board_with_webhook.discord_webhook, data=json.dumps(info))
        mock_post.assert_called_with(
            self.board_with_webhook.discord_webhook, data=json.dumps(info)
        )

    def test_should_cancel_new_topic(self):
        """
        Test should cancel new topic creation
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(self.board.get_absolute_url())

        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")
        page = page.click(linkid="aa-forum-btn-cancel")

        # then
        self.assertEqual(self.board.topics.count(), 0)
        self.assertTemplateUsed(page, "aa_forum/view/forum/board.html")

    def test_should_create_reply_in_topic(self):
        """
        Test should create reply in topic
        :return:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_messages(topic=topic, amount=5)
        self.app.set_user(self.user_1001)
        page = self.app.get(topic.get_absolute_url())

        # when
        form = page.forms["aa-forum-form-message-reply"]
        form["message"] = "What is dark matter?"
        page = form.submit().follow().follow()

        # then
        self.assertEqual(topic.messages.count(), 6)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        new_message = Message.objects.last()
        self.assertEqual(new_message.message, "What is dark matter?")

    def test_should_return_cleaned_message_string_on_topic_reply(self):
        """
        Test should return a clean/sanitized message string on reply in topic
        :return:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_messages(topic=topic, amount=5)
        self.app.set_user(self.user_1001)
        page = self.app.get(topic.get_absolute_url())
        dirty_message = (
            'this is a script test. <script type="text/javascript">alert('
            "'test')</script>and this is style test. <style>.MathJax, "
            ".MathJax_Message, .MathJax_Preview{display: none}</style>end tests."
        )
        cleaned_message = string_cleanup(dirty_message)

        # when
        form = page.forms["aa-forum-form-message-reply"]
        form["message"] = dirty_message
        page = form.submit().follow().follow()

        # then
        new_message = Message.objects.last()
        self.assertEqual(new_message.message, cleaned_message)

    def test_should_not_create_reply_in_topic_due_to_missing_message(self):
        """
        Test should not create reply in topic, because message field is empty
        :return:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        topic_messages = create_fake_messages(topic=topic, amount=5)
        self.app.set_user(self.user_1001)
        page = self.app.get(topic.get_absolute_url())

        # when
        form = page.forms["aa-forum-form-message-reply"]
        form["message"] = ""  # Omit mandatory field
        page = form.submit().follow()

        # then
        self.assertEqual(topic.messages.count(), 5)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        self.assertEqual(topic.last_message.message, topic_messages[-1].message)

        expected_message = (
            "<h4>Error!</h4><p>Message field is mandatory and cannot be empty.</p>"
        )
        messages = list(page.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    def test_should_trigger_error_message_when_trying_to_access_message_reply_directly(
        self,
    ):
        """
        Test should trigger an error message when trying to access
        the reply endpoint of a topic directly
        :return:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_messages(topic=topic, amount=5)
        self.client.force_login(self.user_1001)

        # when
        response = self.client.get(
            reverse(
                "aa_forum:forum_topic_reply",
                args=[topic.board.category.slug, topic.board.slug, topic.slug],
            ),
        )

        # then
        expected_message = (
            "<h4>Error!</h4><p>Something went wrong, please try again.</p>"
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    def test_should_update_own_message(self):
        """
        Test should update own message
        :return:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        own_message = create_fake_message(topic=topic, user=self.user_1001)
        self.app.set_user(self.user_1001)
        page = self.app.get(topic.get_absolute_url())

        # when
        page = page.click(linkid=f"aa-forum-btn-modify-message-{own_message.pk}")
        form = page.forms["aa-forum-form-message-modify"]
        form["message"] = "What is dark matter?"
        page = form.submit().follow().follow()

        # then
        self.assertEqual(topic.messages.count(), 1)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        own_message.refresh_from_db()
        self.assertEqual(own_message.message, "What is dark matter?")

    def test_should_return_cleaned_message_string_on_update_own_message(self):
        """
        Test should return a clean/sanitized message string when updating own message
        :return:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        own_message = create_fake_message(topic=topic, user=self.user_1001)
        self.app.set_user(self.user_1001)
        page = self.app.get(topic.get_absolute_url())
        dirty_message = (
            'this is a script test. <script type="text/javascript">alert('
            "'test')</script>and this is style test. <style>.MathJax, "
            ".MathJax_Message, .MathJax_Preview{display: none}</style>end tests."
        )
        cleaned_message = string_cleanup(dirty_message)

        # when
        page = page.click(linkid=f"aa-forum-btn-modify-message-{own_message.pk}")
        form = page.forms["aa-forum-form-message-modify"]
        form["message"] = dirty_message
        page = form.submit().follow().follow()

        # then
        own_message.refresh_from_db()
        self.assertEqual(own_message.message, cleaned_message)

    def test_should_trigger_error_on_message_edit_due_to_invalid_form_data(self):
        """
        Test should trigger an error message when updating a message
        due to invalid form data
        :return:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        own_message = create_fake_message(topic=topic, user=self.user_1001)
        self.app.set_user(self.user_1001)
        page = self.app.get(topic.get_absolute_url())

        # when
        page = page.click(linkid=f"aa-forum-btn-modify-message-{own_message.pk}")
        form = page.forms["aa-forum-form-message-modify"]
        form["message"] = ""  # Omit mandatory field
        page = form.submit()

        # then
        self.assertEqual(topic.messages.count(), 1)
        self.assertTemplateUsed(page, "aa_forum/view/forum/modify-message.html")

        expected_message = "<h4>Error!</h4><p>Mandatory form field is empty.</p>"
        messages = list(page.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    def test_should_not_be_able_to_edit_messages_from_others(self):
        """
        Test should not be able to edit messages from others
        :return:
        """

        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        alien_message = create_fake_message(topic=topic, user=self.user_1002)
        self.app.set_user(self.user_1001)

        # when
        page = self.app.get(topic.get_absolute_url())

        # then
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        self.assertNotContains(page, f"aa-forum-btn-modify-message-{alien_message.pk}")

    def test_should_find_message_by_key_word(self):
        """
        Test should find message by keyword
        :return:
        """

        # given
        topic_1 = Topic.objects.create(subject="Topic 1", board=self.board)
        create_fake_messages(topic=topic_1, amount=5)
        topic_2 = Topic.objects.create(subject="Topic 2", board=self.board)
        create_fake_messages(topic=topic_2, amount=5)
        message = Message.objects.create(
            topic=topic_1, user_created=self.user_1001, message="xyz dummy123 abc"
        )
        self.app.set_user(self.user_1001)
        page = self.app.get(reverse("aa_forum:forum_index"))

        # when
        form = page.forms["aa-forum-form-search-menu"]
        form["q"] = "dummy123"
        res = form.submit()

        # then
        self.assertTemplateUsed(res, "aa_forum/view/search/results.html")
        self.assertContains(
            res,
            reverse(
                "aa_forum:forum_message",
                args=[
                    message.topic.board.category.slug,
                    message.topic.board.slug,
                    message.topic.slug,
                    message.pk,
                ],
            ),
        )


class TestAdminCategoriesAndBoardsUI(WebTest):
    """
    Tests for the Admin UI
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_fake_user(
            1001,
            "Bruce Wayne",
            permissions=["aa_forum.basic_access", "aa_forum.manage_forum"],
        )

    def test_should_create_category(self):
        """
        Test should create a category
        :return:
        """

        # given
        self.app.set_user(self.user)
        page = self.app.get(reverse("aa_forum:admin_categories_and_boards"))

        # when
        form = page.forms["aa-forum-form-admin-new-category"]
        form["new-category-name"] = "Category"
        page = form.submit().follow()

        # then
        self.assertTemplateUsed(
            page, "aa_forum/view/administration/categories-and-boards.html"
        )
        new_category = Category.objects.last()
        self.assertEqual(new_category.name, "Category")

    def test_should_edit_category(self):
        """
        Test should edit category
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        self.app.set_user(self.user)
        page = self.app.get(reverse("aa_forum:admin_categories_and_boards"))

        # when
        form = page.forms[f"aa-forum-form-admin-edit-category-{category.pk}"]
        form[f"edit-category-{category.pk}-name"] = "Dummy"
        page = form.submit().follow()

        # then
        self.assertTemplateUsed(
            page, "aa_forum/view/administration/categories-and-boards.html"
        )
        category.refresh_from_db()
        self.assertEqual(category.name, "Dummy")

    def test_should_add_board_to_category(self):
        """
        Test should add board to category
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        self.app.set_user(self.user)
        page = self.app.get(reverse("aa_forum:admin_categories_and_boards"))

        # when
        form = page.forms[f"aa-forum-form-admin-add-board-{category.id}"]
        form[f"new-board-in-category-{category.id}-name"] = "Board"
        page = form.submit().follow()

        # then
        self.assertTemplateUsed(
            page, "aa_forum/view/administration/categories-and-boards.html"
        )
        new_board = category.boards.last()
        self.assertEqual(new_board.name, "Board")

    def test_should_edit_board(self):
        """
        Test should edit board
        :return:
        """

        # given
        category = Category.objects.create(name="Category")
        board = Board.objects.create(name="Board", category=category)
        self.app.set_user(self.user)
        page = self.app.get(reverse("aa_forum:admin_categories_and_boards"))

        # when
        form = page.forms[f"aa-forum-form-edit-board-{board.pk}"]
        form[f"edit-board-{board.pk}-name"] = "Dummy"
        page = form.submit().follow()

        # then
        self.assertTemplateUsed(
            page, "aa_forum/view/administration/categories-and-boards.html"
        )
        board.refresh_from_db()
        self.assertEqual(board.name, "Dummy")


class TestProfileUI(WebTest):
    """
    Tests for the Forum UI
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_1001 = create_fake_user(
            1001, "Bruce Wayne", permissions=["aa_forum.basic_access"]
        )
        cls.user_1002 = create_fake_user(
            1002, "Peter Parker", permissions=["aa_forum.basic_access"]
        )
        cls.user_1003 = create_fake_user(1003, "Lex Luthor", permissions=[])

    def test_should_show_profile_index(self):
        """
        Test should show profile index
        :return:
        """

        # given
        self.app.set_user(self.user_1001)

        # when
        page = self.app.get(reverse("aa_forum:profile_index"))

        # then
        self.assertTemplateUsed(page, "aa_forum/view/profile/index.html")

    def test_should_not_show_profile_index(self):
        """
        Test should not show profile index
        :return:
        """

        # given
        self.app.set_user(self.user_1003)

        # when
        page = self.app.get(reverse("aa_forum:profile_index"))

        # then
        self.assertRedirects(page, "/account/login/?next=/forum/-/profile/")

    def test_should_create_user_profile(self):
        """
        Test should create a user profile, since they are only
        created when a user opens their profile page
        :return:
        """

        # given (Should raise a DoesNotExist exception)
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(pk=self.user_1002.pk)

        # when (User loggs in and opens the profile page)
        self.app.set_user(self.user_1002)
        page = self.app.get(reverse("aa_forum:profile_index"))

        # then (Right template should be loaded and UserProfile object created)
        self.assertTemplateUsed(page, "aa_forum/view/profile/index.html")

        user_profile = UserProfile.objects.get(pk=self.user_1002.pk)
        self.assertEqual(user_profile.pk, self.user_1002.pk)

    def test_should_update_user_profile(self):
        """
        Test should update the user profile
        :return:
        """

        # given
        self.app.set_user(self.user_1002)
        page = self.app.get(reverse("aa_forum:profile_index"))
        user_profile = UserProfile.objects.get(pk=self.user_1002.pk)

        # when
        form = page.forms["aa-forum-form-userprofile-modify"]
        form["signature"] = "What is dark matter?"
        page = form.submit().follow()

        # then
        self.assertTemplateUsed(page, "aa_forum/view/profile/index.html")

        user_profile_updated = UserProfile.objects.get(pk=self.user_1002.pk)

        self.assertEqual(user_profile.signature, "")
        self.assertEqual(user_profile_updated.signature, "What is dark matter?")

    def test_should_throw_error_for_too_long_signature(self):
        """
        Test should throw an error because the signature is too long
        :return:
        """

        # given
        max_signature_length = Setting.objects.get_setting(
            setting_key=Setting.USERSIGNATURELENGTH
        )
        signature = fake.text(max_signature_length * 2)

        self.app.set_user(self.user_1002)
        page = self.app.get(reverse("aa_forum:profile_index"))

        # when
        form = page.forms["aa-forum-form-userprofile-modify"]
        form["signature"] = signature

        # then
        self.assertEqual(max_signature_length, 750)
        self.assertGreater(len(signature), max_signature_length)

        page = form.submit()
        messages = list(page.context["messages"])

        expected_message = (
            "<h4>Error!</h4><p>Something went wrong, please check your input<p>"
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    def test_should_throw_error_for_invalid_url(self):
        """
        Test should throw an error because the url is not valid
        :return:
        """

        # given
        self.app.set_user(self.user_1002)
        page = self.app.get(reverse("aa_forum:profile_index"))

        # when
        form = page.forms["aa-forum-form-userprofile-modify"]
        form["website_url"] = "foobar"

        # then
        page = form.submit()
        messages = list(page.context["messages"])

        expected_message = (
            "<h4>Error!</h4><p>Something went wrong, please check your input<p>"
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    def test_should_return_valid_url(self):
        """
        Test should the validated URL
        :return:
        """

        # given
        self.app.set_user(self.user_1002)
        page = self.app.get(reverse("aa_forum:profile_index"))

        # when
        form = page.forms["aa-forum-form-userprofile-modify"]
        form["website_url"] = "https://test.com"
        page = form.submit().follow()

        # then
        self.assertTemplateUsed(page, "aa_forum/view/profile/index.html")
        user_profile_updated = UserProfile.objects.get(pk=self.user_1002.pk)
        self.assertEqual(user_profile_updated.website_url, "https://test.com")

    def test_should_return_correct_model_string(self):
        """
        Test should return the correct model string
        :return:
        """

        # given
        self.app.set_user(self.user_1002)
        self.app.get(reverse("aa_forum:profile_index"))
        user_profile = UserProfile.objects.get(pk=self.user_1002.pk)

        # then
        self.assertEqual(str(user_profile), f"Forum User Profile: {self.user_1002}")


class TestAdminForumSettingsUI(WebTest):
    """
    Tests for the Admin UI
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1001 = create_fake_user(
            1001,
            "Bruce Wayne",
            permissions=["aa_forum.basic_access", "aa_forum.manage_forum"],
        )
        cls.user_1002 = create_fake_user(
            1002, "Peter Parker", permissions=["aa_forum.basic_access"]
        )

    def test_should_show_forum_settings(self):
        """
        Test should show forum settings
        :return:
        """

        # given
        self.app.set_user(self.user_1001)

        # when
        page = self.app.get(reverse("aa_forum:admin_forum_settings"))

        # then
        self.assertTemplateUsed(
            page, "aa_forum/view/administration/forum-settings.html"
        )

    def test_should_not_show_forum_settings(self):
        """
        Test should not show forum settings
        :return:
        """

        # given
        self.app.set_user(self.user_1002)

        # when
        page = self.app.get(reverse("aa_forum:admin_forum_settings"))

        # then
        self.assertRedirects(
            page, "/account/login/?next=/forum/-/admin/forum-settings/"
        )

    def test_should_update_forum_settings(self):
        """
        Test should update forum settings
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(reverse("aa_forum:admin_forum_settings"))
        forum_settings = Setting.objects.get(pk=1)

        # when
        form = page.forms["aa-forum-form-settings-modify"]
        form["user_signature_length"] = 500
        page = form.submit().follow()

        # then
        self.assertTemplateUsed(
            page, "aa_forum/view/administration/forum-settings.html"
        )

        forum_settings_updated = Setting.objects.get(pk=1)

        self.assertEqual(forum_settings.user_signature_length, 750)
        self.assertEqual(forum_settings_updated.user_signature_length, 500)

    def test_should_not_update_forum_settings_on_empty_value(self):
        """
        Test should update forum settings because of an empty value in a mandatory field
        :return:
        """

        # given
        self.app.set_user(self.user_1001)
        page = self.app.get(reverse("aa_forum:admin_forum_settings"))
        forum_settings = Setting.objects.get(pk=1)

        # when
        form = page.forms["aa-forum-form-settings-modify"]
        form["user_signature_length"] = ""
        page = form.submit()

        # then
        self.assertTemplateUsed(
            page, "aa_forum/view/administration/forum-settings.html"
        )

        forum_settings_updated = Setting.objects.get(pk=1)

        self.assertEqual(
            forum_settings.user_signature_length,
            forum_settings_updated.user_signature_length,
        )

        messages = list(page.context["messages"])

        expected_message = (
            "<h4>Error!</h4><p>Something went wrong, please check your input<p>"
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), expected_message)

    def test_should_return_correct_model_string(self):
        """
        Test should return the correct model string
        :return:
        """

        # given
        forum_settings = Setting.objects.get(pk=1)

        # then
        self.assertEqual(str(forum_settings), "Forum Settings")
