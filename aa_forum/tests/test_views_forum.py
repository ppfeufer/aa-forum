"""
Tests for the forum views
"""

# Standard Library
from http import HTTPStatus
from unittest.mock import patch

# Django
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

# AA Forum
from aa_forum.models import Board, Category, LastMessageSeen, Message, Topic
from aa_forum.tests.utils import create_fake_messages, create_fake_user, my_get_setting

VIEWS_PATH = "aa_forum.views.forum"


class TestIndexViews(TestCase):
    """
    Test the forum views
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up users and categories

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.user_1001 = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            permissions=["aa_forum.basic_access"],
        )
        cls.user_1002 = create_fake_user(
            character_id=1002,
            character_name="Peter Parker",
            permissions=["aa_forum.basic_access"],
        )
        cls.category = Category.objects.create(name="Science")

    def setUp(self) -> None:
        """
        Set up boards and topics

        :return:
        :rtype:
        """

        # board 1 has an unread topic
        self.board_1 = Board.objects.create(name="Physics", category=self.category)
        topic_1 = Topic.objects.create(subject="Mysteries", board=self.board_1)
        create_fake_messages(topic=topic_1, amount=4)
        topic_2 = Topic.objects.create(subject="Recent Discoveries", board=self.board_1)
        create_fake_messages(topic=topic_2, amount=2)
        LastMessageSeen.objects.create(
            topic=topic_2,
            user=self.user_1001,
            message_time=topic_2.messages.order_by("-time_posted")[0].time_posted,
        )

        # board 2 has no unread topics
        self.board_2 = Board.objects.create(name="Math", category=self.category)
        topic = Topic.objects.create(subject="Unsolved Problems", board=self.board_2)
        create_fake_messages(topic=topic, amount=2)
        LastMessageSeen.objects.create(
            topic=topic,
            user=self.user_1001,
            message_time=topic.messages.order_by("-time_posted")[0].time_posted,
        )

    def test_should_show_index(self):
        """
        Test should show forum index

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="aa_forum:forum_index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_show_new_indicator_when_one_topic_not_seen_yet(self):
        """
        Test should show new indicator when a topic has not been seen yet

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="aa_forum:forum_index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text=f"aa-forum-unread-in-{self.board_1.id}")
        self.assertNotContains(
            response=res, text=f"aa-forum-unread-in-{self.board_2.id}"
        )

    def test_should_show_new_indicator_when_new_posts_are_made(self):
        """
        Test should show new indicator when new posts are made

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        Message.objects.create(
            topic=self.board_2.topics.first(),
            user_created=self.user_1002,
            message="new message",
        )
        res = self.client.get(path=reverse(viewname="aa_forum:forum_index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text=f"aa-forum-unread-in-{self.board_2.id}")

    def test_should_show_counts(self):
        """
        Test should show counts

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="aa_forum:forum_index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text="6 Posts")
        self.assertContains(response=res, text="2 Topics")

    def test_should_show_empty_counts_after_all_topics_are_deleted(self):
        """
        Test should show empty counts after all topics are deleted

        :return:
        :rtype:
        """

        # given
        Topic.objects.all().delete()
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="aa_forum:forum_index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text="0 Posts")
        self.assertContains(response=res, text="0 Topics")


class TestIndexViewsSpecial(TestCase):
    """
    Test some special views
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up users and categories

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.user_1001 = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            permissions=["aa_forum.basic_access"],
        )
        cls.user_1002 = create_fake_user(
            character_id=1002,
            character_name="Peter Parker",
            permissions=["aa_forum.basic_access"],
        )
        cls.category = Category.objects.create(name="Science")

    def test_should_show_empty_counts_after_all_topics_are_deleted_with_child_board(
        self,
    ):
        """
        Test should show empty counts after all topics are deleted with child board

        :return:
        :rtype:
        """

        # given
        board = Board.objects.create(name="Physics", category=self.category)
        topic = Topic.objects.create(subject="alpha", board=board)
        create_fake_messages(topic=topic, amount=1)
        child_board = Board.objects.create(
            name="Thermodynamics", category=self.category, parent_board=board
        )
        child_topic = Topic.objects.create(subject="bravo", board=child_board)
        create_fake_messages(topic=child_topic, amount=1)
        child_topic.delete()
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(path=reverse(viewname="aa_forum:forum_index"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text="1 Posts")
        self.assertContains(response=res, text="1 Topics")


class TestBoardViews(TestCase):
    """
    Test board views
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up users and categories

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.user_1001 = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            permissions=["aa_forum.basic_access"],
        )
        cls.user_1002 = create_fake_user(
            character_id=1002,
            character_name="Peter Parker",
            permissions=["aa_forum.basic_access"],
        )
        cls.user_1003 = create_fake_user(
            character_id=1003,
            character_name="Clark Kent",
            permissions=["aa_forum.basic_access", "aa_forum.manage_forum"],
        )
        cls.category = Category.objects.create(name="Science")
        cls.board = Board.objects.create(name="Physics", category=cls.category)

    def setUp(self) -> None:
        """
        Set up topics

        :return:
        :rtype:
        """

        # topic 1 is completely new
        self.topic_1 = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_messages(topic=self.topic_1, amount=15)
        # topic 2 is read
        self.topic_2 = Topic.objects.create(subject="Off Topic", board=self.board)
        create_fake_messages(topic=self.topic_2, amount=9)
        LastMessageSeen.objects.create(
            topic=self.topic_2,
            user=self.user_1001,
            message_time=self.topic_2.messages.order_by("-time_posted")[0].time_posted,
        )

    def test_should_show_new_indicator_when_topic_not_seen_yet(self):
        """
        Test should show new indicator when topic has not been seen yet

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board",
                args=[self.category.slug, self.board.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text=f"aa-forum-link-new-{self.topic_1.id}")

    def test_should_show_new_indicator_when_seen_first_page_only(self):
        """
        Test should show new indicator when first page seen only

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        last_message_seen = self.topic_1.messages.order_by("time_posted")[4]
        LastMessageSeen.objects.create(
            topic=self.topic_1,
            user=self.user_1001,
            message_time=last_message_seen.time_posted,
        )

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board",
                args=[self.category.slug, self.board.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text=f"aa-forum-link-new-{self.topic_1.id}")

    def test_should_show_new_indicator_when_seen_second_page_only(self):
        """
        Test should show new indicator when only second page been seen

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        last_message_seen = self.topic_1.messages.order_by("time_posted")[9]
        LastMessageSeen.objects.create(
            topic=self.topic_1,
            user=self.user_1001,
            message_time=last_message_seen.time_posted,
        )

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board",
                args=[self.category.slug, self.board.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text=f"aa-forum-link-new-{self.topic_1.id}")

    def test_should_not_show_new_indicator_when_seen_last_page(self):
        """
        Test should show new indicator when only last page been seen

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        last_message_seen = self.topic_1.messages.order_by("time_posted")[14]
        LastMessageSeen.objects.create(
            topic=self.topic_1,
            user=self.user_1001,
            message_time=last_message_seen.time_posted,
        )

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board",
                args=[self.category.slug, self.board.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertNotContains(
            response=res, text=f"aa-forum-link-new-{self.topic_1.id}"
        )

    def test_should_show_new_indicator_when_new_posts_are_made(self):
        """
        Test should show new indicator when new posts are made

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        Message.objects.create(
            topic=self.topic_2, user_created=self.user_1002, message="new message"
        )
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board",
                args=[self.category.slug, self.board.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertContains(response=res, text=f"aa-forum-link-new-{self.topic_2.id}")

    def test_should_delete_topic(self):
        """
        Test should delete a topic

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:forum_topic_delete", args=[self.topic_1.pk])
        )

        # then
        self.assertRedirects(
            response=res,
            expected_url=reverse(
                viewname="aa_forum:forum_board",
                args=[self.board.category.slug, self.board.slug],
            ),
        )
        self.assertFalse(expr=self.board.topics.filter(pk=self.topic_1.pk).exists())

    def test_should_return_404_when_delete_topic_not_found(self):
        """
        Test should return 404 when a topic not found on delete

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:forum_topic_delete", args=[0])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.NOT_FOUND)

    def test_should_lock_topic(self):
        """
        Test should lock a topic

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_change_lock_state",
                args=[self.topic_1.pk],
            )
        )

        # then
        self.assertRedirects(
            response=res,
            expected_url=reverse(
                viewname="aa_forum:forum_board",
                args=[self.board.category.slug, self.board.slug],
            ),
        )
        self.topic_1.refresh_from_db()
        self.assertTrue(expr=self.topic_1.is_locked)

    def test_should_unlock_topic(self):
        """
        Test should unlock a topic

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)
        self.topic_1.is_locked = True
        self.topic_1.save()

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_change_lock_state",
                args=[self.topic_1.pk],
            )
        )

        # then
        self.assertRedirects(
            response=res,
            expected_url=reverse(
                viewname="aa_forum:forum_board",
                args=[self.board.category.slug, self.board.slug],
            ),
        )
        self.topic_1.refresh_from_db()
        self.assertFalse(expr=self.topic_1.is_locked)

    def test_should_return_404_when_lock_topic_not_found(self):
        """
        Test should return 404 when a topic not found on lock

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:forum_topic_change_lock_state", args=[0])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.NOT_FOUND)

    def test_should_make_topic_sticky(self):
        """
        Test should make topic sticky

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_change_sticky_state",
                args=[self.topic_1.pk],
            )
        )

        # then
        self.assertRedirects(
            response=res,
            expected_url=reverse(
                viewname="aa_forum:forum_board",
                args=[self.board.category.slug, self.board.slug],
            ),
        )
        self.topic_1.refresh_from_db()
        self.assertTrue(expr=self.topic_1.is_sticky)

    def test_should_reverse_topic_sticky(self):
        """
        Test should reverse topic sticky

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)
        self.topic_1.is_sticky = True
        self.topic_1.save()

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_change_sticky_state",
                args=[self.topic_1.pk],
            )
        )

        # then
        self.assertRedirects(
            response=res,
            expected_url=reverse(
                viewname="aa_forum:forum_board",
                args=[self.board.category.slug, self.board.slug],
            ),
        )
        self.topic_1.refresh_from_db()
        self.assertFalse(expr=self.topic_1.is_sticky)

    def test_should_return_404_when_sticky_topic_not_found(self):
        """
        Test should return 404 when a topic not found on sticky change

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:forum_topic_change_sticky_state", args=[0])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.NOT_FOUND)

    def test_should_return_board_does_not_exist_for_wrong_board_on_board_view(self):
        """
        Test should return "Board does not exist" for wrong board

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board",
                args=["foo", "bar"],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertRaises(expected_exception=Board.DoesNotExist)
        self.assertEqual(
            first=response.url, second=reverse(viewname="aa_forum:forum_index")
        )
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The board you were trying to visit does "
                "either not exist, or you don't have access to it.</p>"
            ),
        )

    def test_should_return_category_does_not_exists_on_new_topic(self):
        """
        Test should return "Category does not exist" on new topic

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board_new_topic",
                args=["foo", "bar"],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertRaises(expected_exception=Category.DoesNotExist)
        self.assertEqual(
            first=response.url, second=reverse(viewname="aa_forum:forum_index")
        )
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The category you were trying to post in does "
                "not exist.</p>"
            ),
        )

    def test_should_return_board_does_not_exists_on_new_topic(self):
        """
        Test should return "Board does not exist" on new topic

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board_new_topic",
                args=[self.category.slug, "bar"],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertRaises(expected_exception=Board.DoesNotExist)
        self.assertEqual(
            first=response.url, second=reverse(viewname="aa_forum:forum_index")
        )
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The board you were trying to post in does "
                "either not exist, or you don't have access to it.</p>"
            ),
        )


@patch(VIEWS_PATH + ".Setting.objects.get_setting", new=my_get_setting)
class TestTopicViews(TestCase):
    """
    Test topic views
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up users and categories

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.user_1001 = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            permissions=["aa_forum.basic_access"],
        )
        cls.user_1003 = create_fake_user(
            character_id=1003,
            character_name="Clark Lent",
            permissions=["aa_forum.basic_access", "aa_forum.manage_forum"],
        )
        cls.group = Group.objects.create(name="Superhero")
        cls.announcement_group = Group.objects.create(name="Justice League")

        cls.user_1004 = create_fake_user(
            character_id=1004,
            character_name="Luke Skywalker",
            permissions=["aa_forum.basic_access"],
        )
        cls.user_1004.groups.add(cls.announcement_group)

    def setUp(self) -> None:
        """
        Set up categories, boards and topics

        :return:
        :rtype:
        """

        self.category = Category.objects.create(name="Science")
        self.board = Board.objects.create(name="Physics", category=self.category)
        self.announcement_board = Board.objects.create(
            name="Chemistry", category=self.category, is_announcement_board=True
        )
        self.topic = Topic.objects.create(subject="Mysteries", board=self.board)
        create_fake_messages(topic=self.topic, amount=15)

    def test_should_remember_last_message_seen_by_user_page_1(self):
        """
        Test should remember the last message seen by user on page 1

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        last_message_seen = LastMessageSeen.objects.get(
            topic=self.topic, user=self.user_1001
        )

        # View has 2 pages á 5 messages. This is last message on 1st page
        last_message = self.topic.messages.order_by("time_posted")[4]
        self.assertEqual(
            first=last_message_seen.message_time, second=last_message.time_posted
        )

    def test_should_remember_last_message_seen_by_user_page_2(self):
        """
        Test should remember the last message seen by user on page 2

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, self.topic.slug, 2],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        last_message_seen = LastMessageSeen.objects.get(
            topic=self.topic, user=self.user_1001
        )

        # View has 2 pages á 5 messages. This is last message on 2nd page
        last_message = Message.objects.order_by("time_posted")[9]
        self.assertEqual(
            first=last_message_seen.message_time, second=last_message.time_posted
        )

    def test_should_remember_last_message_seen_by_user_when_opening_previous_pages(
        self,
    ):
        """
        Test should remember the last message seen by user when opening previous pages

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, self.topic.slug, 2],
            )
        )

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, self.topic.slug, 1],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)
        last_message_seen = LastMessageSeen.objects.get(
            topic=self.topic, user=self.user_1001
        )

        # View has 2 pages á 5 messages. This is last message on 2nd page
        last_message = Message.objects.order_by("time_posted")[9]
        self.assertEqual(
            first=last_message_seen.message_time, second=last_message.time_posted
        )

    def test_should_redirect_to_first_message_when_topic_not_seen_yet(self):
        """
        Test should redirect to the first message when the topic not seen yet

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        first_message = self.topic.messages.order_by("time_posted").first()

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_first_unread_message",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertRedirects(
            response=res, expected_url=first_message.get_absolute_url()
        )

    def test_should_redirect_to_first_new_message_normal(self):
        """
        Test should normally redirect to the first new message

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        messages_sorted = list(self.topic.messages.order_by("time_posted"))
        last_seen_message = messages_sorted[2]
        first_unseen_message = messages_sorted[3]
        LastMessageSeen.objects.create(
            topic=self.topic,
            user=self.user_1001,
            message_time=last_seen_message.time_posted,
        )

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_first_unread_message",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertRedirects(
            response=res, expected_url=first_unseen_message.get_absolute_url()
        )

    def test_should_redirect_to_first_unseen_message_when_last_seen_message_deleted(
        self,
    ):
        """
        Test should redirect to the first unseen message when the last seen message is deleted

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        messages_sorted = list(self.topic.messages.order_by("time_posted"))
        last_seen_message = messages_sorted[2]
        first_unseen_message = messages_sorted[3]
        LastMessageSeen.objects.create(
            topic=self.topic,
            user=self.user_1001,
            message_time=last_seen_message.time_posted,
        )
        last_seen_message.delete()

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_first_unread_message",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertRedirects(
            response=res, expected_url=first_unseen_message.get_absolute_url()
        )

    def test_should_redirect_to_newest_message_when_seen_full_topic(self):
        """
        Test should redirect to the newest message

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        last_seen_message = self.topic.messages.order_by("-time_posted")[0]
        LastMessageSeen.objects.create(
            topic=self.topic,
            user=self.user_1001,
            message_time=last_seen_message.time_posted,
        )

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_first_unread_message",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertRedirects(
            response=res, expected_url=last_seen_message.get_absolute_url()
        )

    def test_should_redirect_to_message_by_id_first_page(self):
        """
        Test should redirect to message by ID on the first page

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        my_message = self.topic.messages.order_by("time_posted")[3]
        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_message",
                args=[
                    my_message.topic.board.category.slug,
                    my_message.topic.board.slug,
                    my_message.topic.slug,
                    my_message.pk,
                ],
            ),
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertRedirects(response=res, expected_url=my_message.get_absolute_url())

    def test_should_redirect_to_message_by_id_middle_page_1(self):
        """
        Test should redirect to message by ID on page 1

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        my_message = self.topic.messages.order_by("time_posted")[5]

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_message",
                args=[
                    my_message.topic.board.category.slug,
                    my_message.topic.board.slug,
                    my_message.topic.slug,
                    my_message.pk,
                ],
            ),
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertRedirects(response=res, expected_url=my_message.get_absolute_url())

    def test_should_redirect_to_message_by_id_middle_page_2(self):
        """
        Test should redirect to message by ID on page 2

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        my_message = self.topic.messages.order_by("time_posted")[9]

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_message",
                args=[
                    my_message.topic.board.category.slug,
                    my_message.topic.board.slug,
                    my_message.topic.slug,
                    my_message.pk,
                ],
            ),
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertRedirects(response=res, expected_url=my_message.get_absolute_url())

    def test_should_redirect_to_message_by_id_last_page(self):
        """
        Test should redirect to message by ID on the last page

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        my_message = self.topic.messages.order_by("time_posted")[12]

        # when
        res = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_message",
                args=[
                    my_message.topic.board.category.slug,
                    my_message.topic.board.slug,
                    my_message.topic.slug,
                    my_message.pk,
                ],
            ),
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertRedirects(response=res, expected_url=my_message.get_absolute_url())

    def test_should_delete_regular_message(self):
        """
        Test should delete a regular message

        :return:
        :rtype:

        """

        # given
        self.client.force_login(user=self.user_1003)
        my_message = self.topic.messages.last()

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:forum_message_delete", args=[my_message.pk])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=res.url, second=self.topic.get_absolute_url())
        self.assertFalse(expr=self.topic.messages.filter(pk=my_message.pk).exists())

    def test_should_not_delete_message_because_missing_permissions(self):
        """
        Test should not delete a message because of insufficient permissions

        :return:
        :rtype:

        """

        # given
        message = Message(
            message="Lorem Ipsum", topic=self.topic, user_created=self.user_1003
        )
        message.save()

        # when
        self.client.force_login(user=self.user_1001)
        response = self.client.get(
            path=reverse(viewname="aa_forum:forum_message_delete", args=[message.pk])
        )

        # then
        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)

        expected_message = (
            "<h4>Error!</h4><p>You are not allowed to delete this message!</p>"
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(first=str(messages[0]), second=expected_message)

    def test_should_delete_first_message(self):
        """
        Test should delete the first message

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)
        my_message = self.topic.messages.first()

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:forum_message_delete", args=[my_message.pk])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=res.url, second=self.topic.board.get_absolute_url())
        self.assertFalse(expr=self.topic.messages.filter(pk=my_message.pk).exists())
        self.assertFalse(expr=self.board.topics.filter(pk=self.topic.pk).exists())

    def test_should_delete_last_message_in_topic(self):
        """
        Test should delete the last message in a topic

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)
        my_message = self.topic.messages.first()
        self.topic.messages.exclude(pk=my_message.pk).delete()

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:forum_message_delete", args=[my_message.pk])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=res.url, second=self.topic.board.get_absolute_url())
        self.assertFalse(expr=self.topic.messages.filter(pk=my_message.pk).exists())
        self.assertFalse(expr=self.board.topics.filter(pk=self.topic.pk).exists())

    def test_should_return_404_when_delete_message_not_found(self):
        """
        Test should return 404 when a message not found on delete

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        res = self.client.get(
            path=reverse(viewname="aa_forum:forum_message_delete", args=[0])
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.NOT_FOUND)

    @patch(VIEWS_PATH + ".messages")
    def test_should_not_edit_message_from_others(self, messages):
        """
        Test should not be able to edit messages from others

        :param messages:
        :type messages:
        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)
        alien_message = Message.objects.create(
            topic=self.topic, user_created=self.user_1003, message="old text"
        )

        # when
        res = self.client.post(
            path=reverse(
                viewname="aa_forum:forum_message_modify",
                args=[
                    self.category.slug,
                    self.board.slug,
                    self.topic.slug,
                    alien_message.pk,
                ],
            ),
            data={"message": "new text"},
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=res.url, second=self.topic.get_absolute_url())

        alien_message.refresh_from_db()
        self.assertEqual(first=alien_message.message, second="old text")
        self.assertTrue(expr=messages.error.called)

    @patch(VIEWS_PATH + ".messages")
    def test_should_not_edit_message_from_board_with_no_access(self, messages):
        """
        Test should not be able to edit messages from boards with no access

        :param messages:
        :type messages:
        :return:
        :rtype:
        """

        # given
        self.board.groups.add(self.group)
        self.client.force_login(user=self.user_1001)
        alien_message = Message.objects.create(
            topic=self.topic, user_created=self.user_1001, message="old text"
        )

        # when
        res = self.client.post(
            path=reverse(
                viewname="aa_forum:forum_message_modify",
                args=[
                    self.category.slug,
                    self.board.slug,
                    self.topic.slug,
                    alien_message.pk,
                ],
            ),
            data={"message": "new text"},
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=res.url, second=reverse("aa_forum:forum_index"))

        alien_message.refresh_from_db()
        self.assertEqual(first=alien_message.message, second="old text")
        self.assertTrue(expr=messages.error.called)

    def test_should_return_redirect_to_forum_index_if_topic_does_not_exist_on_topic_view(  # pylint: disable=line-too-long
        self,
    ):
        """
        Test should redirect to forum index when the topic does not exist on topic view

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic",
                args=["foo", "bar", "foobar"],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=response.url, second=reverse("aa_forum:forum_index"))
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The topic you were trying to view does not "
                "exist or you do not have access to it.</p>"
            ),
        )

    def test_should_return_redirect_to_forum_index_if_topic_does_not_exist_on_topic_modify_view(  # pylint: disable=line-too-long
        self,
    ):
        """
        Test should redirect to forum index when topic does not exist on topic modify

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_modify",
                args=["foo", "bar", "foobar"],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=response.url, second=reverse("aa_forum:forum_index"))
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The topic you were trying to modify does not "
                "exist or you do not have access to it.</p>"
            ),
        )

    def test_should_return_redirect_to_forum_index_if_topic_does_not_exist_on_topic_reply(  # pylint: disable=line-too-long
        self,
    ):
        """
        Test should redirect to forum index if a topic does not exist on reply

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_reply",
                args=["foo", "bar", "foobar"],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=response.url, second=reverse("aa_forum:forum_index"))
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The topic you were trying to reply does not "
                "exist or you do not have access to it.</p>"
            ),
        )

    def test_should_return_redirect_to_forum_index_if_message_does_not_exist_on_message_view(  # pylint: disable=line-too-long
        self,
    ):
        """
        Test should redirect to forum index if a message does not exist

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_message",
                args=["foo", "bar", "foobar", 0],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=response.url, second=reverse("aa_forum:forum_index"))
        self.assertRaises(expected_exception=Message.DoesNotExist)
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second="<h4>Error!</h4><p>The message doesn't exist.</p>",
        )

    def test_should_show_all_unread_messages_view(self):
        """
        Test should show all unread messages

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(viewname="aa_forum:forum_topic_show_all_unread"),
        )

        # then
        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)

    def test_should_return_to_forum_index_on_topic_modify_when_no_topic_found(self):
        """
        Test should redirect to forum index if a topic not found on modify

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_modify",
                args=["foo", "bar", "foobar"],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(first=response.url, second=reverse("aa_forum:forum_index"))
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The topic you were trying to modify does not "
                "exist or you do not have access to it.</p>"
            ),
        )

    def test_should_redirect_to_topic_view_for_user_without_rights_to_modify_topic(
        self,
    ):
        """
        Test should redirect to forum index for user without rights to modify topic

        :return:
        :rtype:
        """

        # given
        user_without_modify_perms = create_fake_user(
            character_id=1002,
            character_name="Peter Parker",
            permissions=["aa_forum.basic_access"],
        )
        self.client.force_login(user=user_without_modify_perms)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_modify",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            ),
        )

        # then
        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(
            first=response.url,
            second=reverse(
                "aa_forum:forum_topic",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            ),
        )
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second="<h4>Error!</h4><p>You are not allowed to modify this topic!</p>",
        )

    def test_should_show_modify_topic_view(self):
        """
        Test should show modify topic view

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_topic_modify",
                args=[self.category.slug, self.board.slug, self.topic.slug],
            ),
        )

        # then
        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)

    def test_can_create_new_topic_in_announcement_board_with_permission(self):
        """
        Test should create a new topic in announcement board with permissions

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1003)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board_new_topic",
                args=[self.category.slug, self.announcement_board.slug],
            ),
        )

        # then
        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)

    def test_can_create_new_topic_in_announcement_board_with_group(self):
        """
        Test should create a new topic in announcement board with groups

        :return:
        :rtype:
        """

        # given
        self.announcement_board.announcement_groups.add(self.announcement_group)
        self.client.force_login(user=self.user_1004)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board_new_topic",
                args=[self.category.slug, self.announcement_board.slug],
            ),
        )

        # then
        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)

    def test_cannot_create_new_topic_in_announcement_board_without_permission(self):
        """
        Test should create a new topic in announcement board without permissions

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1004)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board_new_topic",
                args=[self.category.slug, self.announcement_board.slug],
            ),
        )

        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(
            first=response.url,
            second=reverse(
                viewname="aa_forum:forum_board",
                args=[self.category.slug, self.announcement_board.slug],
            ),
        )
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The board you were trying to post in is an "
                "announcement board and you don't have the permissions to start a "
                "topic there.</p>"
            ),
        )

    def test_cannot_create_new_topic_in_announcement_board(self):
        """
        Test cannot create a new topic in announcement board

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_1001)

        # when
        response = self.client.get(
            path=reverse(
                viewname="aa_forum:forum_board_new_topic",
                args=[self.category.slug, self.announcement_board.slug],
            ),
        )

        messages = list(get_messages(request=response.wsgi_request))

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.assertEqual(
            first=response.url,
            second=reverse(
                viewname="aa_forum:forum_board",
                args=[self.category.slug, self.announcement_board.slug],
            ),
        )
        self.assertEqual(first=len(messages), second=1)
        self.assertEqual(
            first=str(messages[0]),
            second=(
                "<h4>Error!</h4><p>The board you were trying to post in is an "
                "announcement board and you don't have the permissions to start a "
                "topic there.</p>"
            ),
        )
