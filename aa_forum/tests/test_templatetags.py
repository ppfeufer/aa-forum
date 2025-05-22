"""
Tests for the template tags
"""

# Standard Library
from datetime import datetime

# Third Party
from dateutil import parser

# Django
from django.template import TemplateSyntaxError
from django.test import TestCase, modify_settings

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# Alliance Auth (External Libs)
from app_utils.urls import reverse as reverse_url

# AA Forum
from aa_forum.models import PersonalMessage, get_sentinel_user
from aa_forum.templatetags.aa_forum import personal_message_unread_count
from aa_forum.tests.utils import create_fake_user, render_template


class TestMainCharacterName(TestCase):
    """
    Tests for main_character_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up template

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.template = "{% load aa_forum %}{{ user|aa_forum_main_character_name }}"

    def test_should_contain_character_name_for_users_with_main(self):
        """
        Test should contain a character name for user with a main set

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(character_id=1001, character_name="Bruce Wayne")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="Bruce Wayne")

    def test_should_contain_user_character_name_for_users_without_main(self):
        """
        Should return username for users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="john")

    def test_should_return_deleted_user_for_sentinel_user(self):
        """
        Should return "deleted" for sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="deleted")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty

        :return:
        :rtype:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="")


class TestMainCharacterId(TestCase):
    """
    Tests for aa_forum_main_character_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up template

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.template = "{% load aa_forum %}{{ user|aa_forum_main_character_id }}"

    def test_should_contain_character_id_for_users_with_main(self):
        """
        Test should contain main character ID for users with main

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(character_id=1001, character_name="Bruce Wayne")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1001")

    def test_should_contain_dummy_id_for_users_without_main(self):
        """
        Test should contain dummy ID (1) for users without main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return dummy ID (1) for None

        :return:
        :rtype:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")


class TestMainCharacterCorporationName(TestCase):
    """
    Tests for aa_forum_main_character_corporation_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up template

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.template = (
            "{% load aa_forum %}{{ user|aa_forum_main_character_corporation_name }}"
        )

    def test_should_contain_corp_name_for_users_with_main(self):
        """
        Test should return corporation name for users with a main character

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
        )
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="Wayne Tech Inc.")

    def test_should_be_empty_for_users_without_main(self):
        """
        Test should be empty for users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_for_sentinel_user(self):
        """
        Test should be empty for sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty for None

        :return:
        :rtype:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="")


class TestMainCorporationId(TestCase):
    """
    Tests for aa_forum_main_character_corporation_id template tag

    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up template

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.template = (
            "{% load aa_forum %}{{ user|aa_forum_main_character_corporation_id }}"
        )

    def test_should_contain_corporation_id_for_users_with_main(self):
        """
        Test should return the main character corp ID for users with a main character

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
        )
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="2001")

    def test_should_be_dummy_id_for_users_without_main(self):
        """
        Test should return dummy ID (1) for users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user(username="john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)
        # then

        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return dummy ID (1) for None

        :return:
        :rtype:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")


class TestMainCharacterAllianceName(TestCase):
    """
    Tests for aa_forum_main_character_alliance_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up template

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.template = (
            "{% load aa_forum %}{{ user|aa_forum_main_character_alliance_name }}"
        )

    def test_should_contain_alliance_name_for_users_with_main(self):
        """
        Test should return the main character alliance name for users with a main character

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprices",
        )

        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="Wayne Enterprices")

    def test_should_be_empty_for_users_without_main(self):
        """
        Test should be empty for users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_when_main_is_not_in_an_alliance(self):
        """
        Test should be empty when the main character is not in an alliance

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=2012,
            character_name="William Riker",
            corporation_id=2012,
            corporation_name="Starfleet",
            corporation_ticker="SF",
            alliance_id=None,
        )

        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_for_sentinel_user(self):
        """
        Test should be empty for sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty for None

        :return:
        :rtype:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="")


class TestMainAllianceId(TestCase):
    """
    Tests for aa_forum_main_character_alliance_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up template

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.template = (
            "{% load aa_forum %}{{ user|aa_forum_main_character_alliance_id }}"
        )

    def test_should_contain_alliance_id_for_users_with_main(self):
        """
        Test should return main character alliance ID for user with a main character

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="3001")

    def test_should_be_dummy_id_for_users_without_main(self):
        """
        Test should return dummy ID (1) for user without main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_dummy_id_when_main_is_not_in_an_alliance(self):
        """
        Test should dummy ID (1) when the main character is not in an alliance

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=2012,
            character_name="William Riker",
            corporation_id=2012,
            corporation_name="Starfleet",
            corporation_ticker="SF",
            alliance_id=None,
        )

        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return dummy ID (1) for None

        :return:
        :rtype:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(first=result, second="1")


class TestForumTemplateVariables(TestCase):
    """
    Tests for aa_forum template_variables template tag
    """

    def test_aa_forum_template_variable(self):
        """
        Test aa_forum_template_variable

        :return:
        :rtype:
        """

        rendered = render_template(
            string=(
                "{% load aa_forum %}"
                "{% aa_forum_template_variable foo = content %}"
                "{{ foo }}"
            ),
            context={"content": "bar"},
        )

        self.assertEqual(first=rendered, second="bar")

    def test_should_raise_template_syntax_error(self):
        """
        Test should raise template syntax error

        :return:
        :rtype:
        """

        with self.assertRaisesMessage(
            expected_exception=TemplateSyntaxError,
            expected_message=(
                "'aa_forum_template_variable' tag must be of the form: "
                "{% aa_forum_template_variable <var_name> = <var_value> %}"
            ),
        ):
            render_template(
                string=(
                    "{% load aa_forum %}"
                    "{% aa_forum_template_variable foo %}"
                    "{{ foo }}"
                )
            )

    def test_should_return_personal_message_unread_count_as_empty_string(self):
        """
        Test personal_message_unread_count to return zero

        :return:
        :rtype:
        """

        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )

        self.client.force_login(user)

        rendered = render_template(
            string=("{% load aa_forum %}{% personal_message_unread_count 1001 %}")
        )

        self.assertEqual(first=rendered, second="")

    def test_should_return_personal_message_unread_count_as_bootstrap_badge_with_number(
        self,
    ):
        """
        Test personal_message_unread_count to return a bootstrap badge with a number

        :return:
        :rtype:
        """

        # given (creating our personal message)
        user_sender = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )

        user_receiver = create_fake_user(
            character_id=1002,
            character_name="Batman",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )

        PersonalMessage.objects.create(
            sender=user_sender,
            recipient=user_receiver,
            subject="Foo",
            message="Bar",
        )

        # when (template tag is triggered)
        response = personal_message_unread_count(user_receiver)

        # then
        self.assertEqual(
            first=response,
            second=(
                '<span class="badge text-bg-secondary aa-forum-badge-personal-messages-unread-count">1</span>'  # pylint: disable=line-too-long
            ),
        )


class TestHighlightSearchTerm(TestCase):
    """
    Tests for highlight_search_term template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.message_text = "Lorem Ipsum"
        cls.message_with_link = '<a href="https://lorem-ipsum.com">Lorem Ipsum</a>'
        cls.message_with_link_without_href = '<a title="Lorem Ipsum">Lorem Ipsum</a>'
        cls.message_with_link_and_title = (
            '<a href="https://lorem-ipsum.com" title="Lorem Ipsum">Lorem Ipsum</a>'
        )
        cls.message_with_link_and_name = (
            '<a href="https://lorem-ipsum.com" name="Lorem Ipsum">Lorem Ipsum</a>'
        )
        cls.message_with_image = (
            '<img src="https://lorem-ipsum.com/lorem-ipsum.jpg"> Lorem Ipsum'
        )
        cls.message_with_image_without_src = '<img alt="Lorem Ipsum"> Lorem Ipsum'
        cls.message_with_image_and_alt = (
            '<img src="https://lorem-ipsum.com/lorem-ipsum.jpg" alt="Lorem Ipsum"> '
            "Lorem Ipsum"
        )
        cls.message_with_image_and_title = (
            '<img src="https://lorem-ipsum.com/lorem-ipsum.jpg" title="Lorem Ipsum"> '
            "Lorem Ipsum"
        )
        cls.search_term = "Lorem"
        cls.template = (
            "{% load aa_forum %}"
            "{{ message|aa_forum_highlight_search_term:search_term  }}"
        )

    def test_should_highlight_with_just_text(self):
        """
        Test should highlight search term

        :return:
        :rtype:
        """

        context = {"message": self.message_text, "search_term": self.search_term}

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_add_dummy_href(self):
        """
        Test should add a dummy href

        :return:
        :rtype:
        """

        context = {
            "message": self.message_with_link_without_href,
            "search_term": self.search_term,
        }

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<a href="#" title="Lorem Ipsum">'
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum</a>'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_not_highlight_in_link_href(self):
        """
        Test should not highlight in an a-tag's href attribute

        :return:
        :rtype:
        """

        context = {"message": self.message_with_link, "search_term": self.search_term}

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<a href="https://lorem-ipsum.com">'
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum</a>'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_not_highlight_in_link_title(self):
        """
        Test should not highlight in an a-tag's title attribute

        :return:
        :rtype:
        """

        context = {
            "message": self.message_with_link_and_title,
            "search_term": self.search_term,
        }

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<a href="https://lorem-ipsum.com" title="Lorem Ipsum">'
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum</a>'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_not_highlight_in_link_name(self):
        """
        Test should not highlight in an a-tag's name attribute

        :return:
        :rtype:
        """

        context = {
            "message": self.message_with_link_and_name,
            "search_term": self.search_term,
        }

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<a href="https://lorem-ipsum.com" name="Lorem Ipsum">'
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum</a>'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_not_highlight_in_img_src(self):
        """
        Test should not highlight in an img-tag's src attribute

        :return:
        :rtype:
        """

        context = {
            "message": self.message_with_image,
            "search_term": self.search_term,
        }

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<img src="https://lorem-ipsum.com/lorem-ipsum.jpg"/> '
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_add_dummy_image_src(self):
        """
        Test should add a dummy image src

        :return:
        :rtype:
        """

        context = {
            "message": self.message_with_image_without_src,
            "search_term": self.search_term,
        }

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<img alt="Lorem Ipsum" src="#"/> '
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_not_highlight_in_img_alt(self):
        """
        Test should not highlight in an img-tag's alt attribute

        :return:
        :rtype:
        """

        context = {
            "message": self.message_with_image_and_alt,
            "search_term": self.search_term,
        }

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<img alt="Lorem Ipsum" src="https://lorem-ipsum.com/lorem-ipsum.jpg"/> '
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_not_highlight_in_img_title(self):
        """
        Test should not highlight in an img-tag's title attribute

        :return:
        :rtype:
        """

        context = {
            "message": self.message_with_image_and_title,
            "search_term": self.search_term,
        }

        rendered_template = render_template(string=self.template, context=context)

        expected_result = (
            '<img src="https://lorem-ipsum.com/lorem-ipsum.jpg" title="Lorem Ipsum"/> '
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(first=rendered_template, second=expected_result)


class TestForumDatetime(TestCase):
    """
    Tests for aa_forum_time template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.db_datetime = parser.parse(timestr="2021-08-17 05:38:13.887496")
        cls.template = "{% load aa_forum %}{{ message_date|aa_forum_time }}"

    @modify_settings(INSTALLED_APPS={"remove": "timezones"})
    def test_should_return_formatted_date_and_time(self):
        """
        Test should return the formatted date and time without aa-timezones support

        :return:
        :rtype:
        """

        context = {"message_date": self.db_datetime}
        rendered_template = render_template(string=self.template, context=context)
        expected_result = "Aug. 17, 2021, 05:38:13"

        self.assertEqual(first=rendered_template, second=expected_result)

    @modify_settings(INSTALLED_APPS={"append": "timezones"})
    def test_should_return_formatted_date_and_time_with_aa_timezones_support(self):
        """
        Test should return a formatted date and time with aa-timezones support

        :return:
        :rtype:
        """

        context = {"message_date": self.db_datetime}
        rendered_template = render_template(string=self.template, context=context)
        timestamp_from_db_datetime = int(datetime.timestamp(self.db_datetime))
        timezones_url = reverse_url(
            viewname="timezones:index", args=[timestamp_from_db_datetime]
        )
        link_title = "Timezone conversion"
        formatted_forum_date = "Aug. 17, 2021, 05:38:13"

        expected_result = (
            f"{formatted_forum_date} "
            f'<sup>(<a href="{timezones_url}" target="_blank" rel="noopener noreferer" '
            f'title="{link_title}" data-bs-tooltip="aa-forum">'
            '<i class="fa-solid fa-circle-question"></i></a>)</sup>'
        )

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_return_empty_date_and_time_string(self):
        """
        Test should return empty date and time string for message_date = ""

        :return:
        :rtype:
        """

        context = {"message_date": ""}
        rendered_template = render_template(string=self.template, context=context)
        expected_result = ""

        self.assertEqual(first=rendered_template, second=expected_result)

    def test_should_return_empty_date_and_time_string_for_none(self):
        """
        Test should return empty date and time string for message_date = None

        :return:
        :rtype:
        """

        context = {"message_date": None}
        rendered_template = render_template(string=self.template, context=context)
        expected_result = ""

        self.assertEqual(first=rendered_template, second=expected_result)
