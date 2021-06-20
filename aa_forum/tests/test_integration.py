from django_webtest import WebTest

from django.urls import reverse

from ..models import Board, Category, Message, Topic
from .utils import create_fake_user


class TestForumUI(WebTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_fake_user(
            1001, "Bruce Wayne", permissions=["aa_forum.basic_access"]
        )
        cls.category = Category.objects.create(name="Science")
        cls.board = Board.objects.create(name="Physics", category=cls.category)

    def test_should_create_new_topic(self):
        # given
        self.app.set_user(self.user)
        page = self.app.get(
            reverse("aa_forum:forum_board", args=[self.category.slug, self.board.slug])
        )
        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")
        # then
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

    def test_should_cancel_new_topic(self):
        # given
        self.app.set_user(self.user)
        page = self.app.get(
            reverse("aa_forum:forum_board", args=[self.category.slug, self.board.slug])
        )
        # when
        page = page.click(linkid="aa-forum-btn-new-topic-above-list")
        # then
        page = page.click(linkid="aa-forum-btn-cancel")
        # then
        self.assertEqual(self.board.topics.count(), 0)
        self.assertTemplateUsed(page, "aa_forum/view/forum/board.html")

    def test_should_create_reply_to_message(self):
        # given
        topic = Topic.objects.create(subject="Mysteries", board=self.board)
        Message.objects.create(
            topic=topic, user_created=self.user, message="What is dark energy?"
        )
        self.app.set_user(self.user)
        page = self.app.get(
            reverse(
                "aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, topic.slug],
            )
        )
        # when
        form = page.forms["aa-forum-form-message-reply"]
        form["message"] = "What is dark matter?"
        page = form.submit().follow().follow()
        # then
        self.assertEqual(topic.messages.count(), 2)
        self.assertTemplateUsed(page, "aa_forum/view/forum/topic.html")
        new_message = Message.objects.last()
        self.assertEqual(new_message.message, "What is dark matter?")
