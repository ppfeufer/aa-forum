"""
Tests for the widgets views
"""

# Standard Library
from http import HTTPStatus

# Django
from django.test import RequestFactory
from django.urls import reverse

# AA Forum
from aa_forum.helper.user import get_user_profile
from aa_forum.models import LastMessageSeen
from aa_forum.tests import BaseTestCase
from aa_forum.tests.utils import (
    create_board,
    create_category,
    create_fake_messages,
    create_fake_user,
    create_topic,
    random_id,
)
from aa_forum.views.widgets import dashboard_widgets


class TestDashboardWidgets(BaseTestCase):
    """
    Tests for dashboard_widgets
    """

    def test_returns_empty_string_when_user_has_no_basic_access(self):
        """
        Test that the dashboard_widgets function returns empty string when user has no basic access

        :return:
        :rtype:
        """

        user = create_fake_user(character_id=random_id(), character_name="No Perm")

        request = RequestFactory().get("/")
        request.user = user

        result = dashboard_widgets(request)

        self.assertEqual(first=result, second="")

    def test_renders_dashboard_markup_when_user_has_basic_access(self):
        """
        Test that the dashboard_widgets function returns dashboard markup when user has basic access

        :return:
        :rtype:
        """

        user = create_fake_user(
            character_id=random_id(),
            character_name="With Perm",
            permissions=["aa_forum.basic_access"],
        )

        # ensure the user profile exists and toggle the unread topics widget on
        profile = get_user_profile(user=user)
        profile.show_unread_topics_dashboard_widget = True
        profile.save()

        request = RequestFactory().get("/")
        request.user = user

        result = dashboard_widgets(request)

        # outer container should always be present for permitted users
        self.assertIn('id="aa-forum-dashboard-widgets"', result)

        # when the profile flag is enabled the unread-topics widget container should be rendered
        self.assertIn('id="aa-forum-dashboard-widget-unread-topics"', result)


class TestAjaxUnreadTopics(BaseTestCase):
    """
    Tests for ajax_unread_topics
    """

    def test_returns_204_when_user_profile_flag_disabled_even_if_unread_exist(self):
        """
        Test returns HTTP204 when user profile flag is disabled even if unread exists

        :return:
        :rtype:
        """

        user = create_fake_user(
            character_id=random_id(),
            character_name="No Perm",
            permissions=["aa_forum.basic_access"],
        )
        category = create_category(name="Science")
        board = create_board(name="Physics", category=category)
        topic = create_topic(subject="Mysteries", board=board)
        create_fake_messages(topic=topic, amount=3)

        # Ensure profile flag remains False (default)
        self.client.force_login(user=user)
        response = self.client.get(
            path=reverse(viewname="aa_forum:widgets_ajax_unread_topics")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.NO_CONTENT)

    def test_returns_204_when_no_unread_boards_even_if_widget_enabled(self):
        """
        Test returns HTTP204 when no unread boards exist even if the widget is enabled

        :return:
        :rtype:
        """

        user = create_fake_user(
            character_id=random_id(),
            character_name="Reader",
            permissions=["aa_forum.basic_access"],
        )

        category = create_category(name="Math")
        board = create_board(name="Algebra", category=category)
        topic = create_topic(subject="Problems", board=board)
        create_fake_messages(topic=topic, amount=2)

        # Mark topic as seen by the user
        LastMessageSeen.objects.create(
            topic=topic,
            user=user,
            message_time=topic.messages.order_by("-time_posted")[0].time_posted,
        )

        profile = get_user_profile(user=user)
        profile.show_unread_topics_dashboard_widget = True
        profile.save()

        self.client.force_login(user=user)
        response = self.client.get(
            path=reverse(viewname="aa_forum:widgets_ajax_unread_topics")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.NO_CONTENT)

    def test_renders_unread_topics_fragment_when_unread_exist_and_widget_enabled(self):
        """
        Test renders unread topics fragment when unread exist and widget enabled

        :return:
        :rtype:
        """

        user = create_fake_user(
            character_id=random_id(),
            character_name="Watcher",
            permissions=["aa_forum.basic_access"],
        )

        category = create_category(name="History")
        board = create_board(name="Ancients", category=category)
        topic = create_topic(subject="Legends", board=board)
        create_fake_messages(topic=topic, amount=4)

        profile = get_user_profile(user=user)
        profile.show_unread_topics_dashboard_widget = True
        profile.save()

        self.client.force_login(user=user)
        response = self.client.get(
            path=reverse(viewname="aa_forum:widgets_ajax_unread_topics")
        )

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertContains(response=response, text=board.name)
