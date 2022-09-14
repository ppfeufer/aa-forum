"""
Tests for the template tags
"""

# Django
from django.template import TemplateSyntaxError
from django.test import TestCase

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA Forum
from aa_forum import __version__
from aa_forum.models import PersonalMessage, get_sentinel_user
from aa_forum.templatetags.aa_forum_template_variables import (
    personal_message_unread_count,
)
from aa_forum.tests.utils import create_fake_user, render_template


class TestMainCharacterName(TestCase):
    """
    Tests for main_character_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = "{% load aa_forum_user %}{{ user|main_character_name }}"

    def test_should_contain_character_name_for_users_with_main(self):
        """
        test should contain character name for user with main set
        :return:
        """

        # given
        user = create_fake_user(1001, "Bruce Wayne")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "Bruce Wayne")

    def test_should_contain_user_character_name_for_users_without_main(self):
        """
        Should return username for users without a main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "john")

    def test_should_return_deleted_user_for_sentinel_user(self):
        """
        Should return "deleted" for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "deleted")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty
        :return:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "")


class TestMainCharacterId(TestCase):
    """
    Tests for main_character_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = "{% load aa_forum_user %}{{ user|main_character_id }}"

    def test_should_contain_character_id_for_users_with_main(self):
        """
        Test should contain main character ID for users with main
        :return:
        """

        # given
        user = create_fake_user(1001, "Bruce Wayne")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1001")

    def test_should_contain_dummy_id_for_users_without_main(self):
        """
        Test should contain dummy ID (1) for users without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return dummy ID (1) for None
        :return:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")


class TestMainCharacterCorporationName(TestCase):
    """
    Tests for main_character_corporation_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = (
            "{% load aa_forum_user %}{{ user|main_character_corporation_name }}"
        )

    def test_should_contain_corp_name_for_users_with_main(self):
        """
        Test should return corporation name for users with main character
        :return:
        """

        # given
        user = create_fake_user(1001, "Bruce Wayne", 2001, "Wayne Tech Inc.", "WYT")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "Wayne Tech Inc.")

    def test_should_be_empty_for_users_without_main(self):
        """
        Test should be empty for users without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_sentinel_user(self):
        """
        Test should be empty for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty for None
        :return:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "")


class TestMainCorporationId(TestCase):
    """
    Tests for main_character_corporation_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = (
            "{% load aa_forum_user %}{{ user|main_character_corporation_id }}"
        )

    def test_should_contain_corporation_id_for_users_with_main(self):
        """
        Test should return main character corp ID for users with main character
        :return:
        """

        # given
        user = create_fake_user(1001, "Bruce Wayne", 2001, "Wayne Tech Inc.", "WYT")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "2001")

    def test_should_be_dummy_id_for_users_without_main(self):
        """
        Test should return dummy ID (1) for users without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)
        # then

        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return dummy ID (1) for None
        :return:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")


class TestMainCharacterAllianceName(TestCase):
    """
    Tests for main_character_alliance_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = "{% load aa_forum_user %}{{ user|main_character_alliance_name }}"

    def test_should_contain_alliance_name_for_users_with_main(self):
        """
        Test should return main character alliance name for users with min character
        :return:
        """

        # given
        user = create_fake_user(
            1001,
            "Bruce Wayne",
            2001,
            "Wayne Tech Inc.",
            "WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprices",
        )

        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "Wayne Enterprices")

    def test_should_be_empty_for_users_without_main(self):
        """
        Test should be empty for users without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_when_main_is_not_in_an_alliance(self):
        """
        Test should be empty when main character is not in an alliance
        :return:
        """

        # given
        user = create_fake_user(
            2012, "William Riker", 2012, "Starfleet", "SF", alliance_id=None
        )

        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_sentinel_user(self):
        """
        Test should be empty for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty for None
        :return:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "")


class TestMainAllianceId(TestCase):
    """
    Tests for main_character_alliance_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = "{% load aa_forum_user %}{{ user|main_character_alliance_id }}"

    def test_should_contain_alliance_id_for_users_with_main(self):
        """
        Test should return main character alliance ID for user with main character
        :return:
        """

        # given
        user = create_fake_user(
            1001,
            "Bruce Wayne",
            2001,
            "Wayne Tech Inc.",
            "WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "3001")

    def test_should_be_dummy_id_for_users_without_main(self):
        """
        Test should return dummy ID (1) for user without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")

    def test_should_dummy_id_when_main_is_not_in_an_alliance(self):
        """
        Test should dummy ID (1) when main character is not in an alliance
        :return:
        """

        # given
        user = create_fake_user(
            2012, "William Riker", 2012, "Starfleet", "SF", alliance_id=None
        )

        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = {"user": user}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_none(self):
        """
        test should return dummy ID (1) for None
        :return:
        """

        # given
        context = {"user": None}

        # when
        result = render_template(string=self.template, context=context)

        # then
        self.assertEqual(result, "1")


class TestForumTemplateVariables(TestCase):
    """
    Tests for aa_forum_template_variables template tag
    """

    def test_set_template_variable(self):
        """
        Test set template variable
        :return:
        """

        rendered = render_template(
            string=(
                "{% load aa_forum_template_variables %}"
                "{% set_template_variable foo = content %}"
                "{{ foo }}"
            ),
            context={"content": "bar"},
        )

        # self.assertInHTML("bar", rendered_template)
        self.assertEqual(rendered, "bar")

    def test_should_raise_template_syntax_error(self):
        """
        Test should raise template syntax error
        :return:
        """

        with self.assertRaisesMessage(
            TemplateSyntaxError,
            "'set_template_variable' tag must be of the form: "
            "{% set_template_variable <var_name> = <var_value> %}",
        ):
            render_template(
                "{% load aa_forum_template_variables %}"
                "{% set_template_variable foo %}"
                "{{ foo }}"
            )

    def test_should_return_personal_message_unread_count_as_empty_string(self):
        """
        Test personal_message_unread_count to return zero
        :return:
        """

        user = create_fake_user(
            1001,
            "Bruce Wayne",
            2001,
            "Wayne Tech Inc.",
            "WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )

        self.client.force_login(user)

        rendered = render_template(
            "{% load aa_forum_template_variables %}"
            "{% personal_message_unread_count 1001 %}"
        )

        self.assertEqual(rendered, "")

    def test_should_return_personal_message_unread_count_as_bootstrap_badge_with_number(
        self,
    ):
        """
        Test personal_message_unread_count to return a bootstrap badge with a number
        :return:
        """

        # given (creating our personal message)
        user_sender = create_fake_user(
            1001,
            "Bruce Wayne",
            2001,
            "Wayne Tech Inc.",
            "WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )

        user_receiver = create_fake_user(
            1002,
            "Batman",
            2001,
            "Wayne Tech Inc.",
            "WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )

        PersonalMessage.objects.create(
            sender=user_sender,
            recipient=user_receiver,
            subject="Foo",
            message="Bar",
        )

        # when (template tage is triggered)
        response = personal_message_unread_count(user_receiver)

        # then
        self.assertEqual(
            response,
            '<span class="badge aa-forum-badge-personal-messages-unread-count">1</span>',
        )


class TestForumVersionedStatic(TestCase):
    """
    Tests for aa_forum_versioned_static template tag
    """

    def test_versioned_static(self):
        """
        Test should return static URL string with version
        :return:
        """

        context = {"version": __version__}

        rendered_template = render_template(
            string=(
                "{% load aa_forum_versioned_static %}"
                "{% aa_forum_static 'aa_forum/css/aa-forum.min.css' %}"
            ),
            context=context,
        )

        self.assertEqual(
            rendered_template,
            f'/static/aa_forum/css/aa-forum.min.css?v={context["version"]}',
        )


class TestHighlightSearchTerm(TestCase):
    """
    Tests for aa_forum_versioned_static template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
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
            "{% load aa_forum_search %}"
            "{{ message|highlight_search_term:search_term  }}"
        )

    def test_should_highlight_with_just_text(self):
        """
        Test should highlight search term
        :return:
        """

        context = {"message": self.message_text, "search_term": self.search_term}

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(rendered_template, expected_result)

    def test_should_add_dummy_href(self):
        """
        Test should add a dummy href
        :return:
        """

        context = {
            "message": self.message_with_link_without_href,
            "search_term": self.search_term,
        }

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<a href="#" title="Lorem Ipsum">'
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum</a>'
        )

        self.assertEqual(rendered_template, expected_result)

    def test_should_not_highlight_in_link_href(self):
        """
        Test should not highlight in an a-tag's href attribute
        :return:
        """

        context = {"message": self.message_with_link, "search_term": self.search_term}

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<a href="https://lorem-ipsum.com">'
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum</a>'
        )

        self.assertEqual(rendered_template, expected_result)

    def test_should_not_highlight_in_link_title(self):
        """
        Test should not highlight in an a-tag's title attribute
        :return:
        """

        context = {
            "message": self.message_with_link_and_title,
            "search_term": self.search_term,
        }

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<a href="https://lorem-ipsum.com" title="Lorem Ipsum">'
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum</a>'
        )

        self.assertEqual(rendered_template, expected_result)

    def test_should_not_highlight_in_link_name(self):
        """
        Test should not highlight in an a-tag's name attribute
        :return:
        """

        context = {
            "message": self.message_with_link_and_name,
            "search_term": self.search_term,
        }

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<a href="https://lorem-ipsum.com" name="Lorem Ipsum">'
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum</a>'
        )

        self.assertEqual(rendered_template, expected_result)

    def test_should_not_highlight_in_img_src(self):
        """
        Test should not highlight in an img-tag's src attribute
        :return:
        """

        context = {
            "message": self.message_with_image,
            "search_term": self.search_term,
        }

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<img src="https://lorem-ipsum.com/lorem-ipsum.jpg"/> '
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(rendered_template, expected_result)

    def test_should_add_dummy_image_src(self):
        """
        Test should add a dummy image src
        :return:
        """

        context = {
            "message": self.message_with_image_without_src,
            "search_term": self.search_term,
        }

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<img alt="Lorem Ipsum" src="#"/> '
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(rendered_template, expected_result)

    def test_should_not_highlight_in_img_alt(self):
        """
        Test should not highlight in an img-tag's alt attribute
        :return:
        """

        context = {
            "message": self.message_with_image_and_alt,
            "search_term": self.search_term,
        }

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<img alt="Lorem Ipsum" src="https://lorem-ipsum.com/lorem-ipsum.jpg"/> '
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(rendered_template, expected_result)

    def test_should_not_highlight_in_img_title(self):
        """
        Test should not highlight in an img-tag's title attribute
        :return:
        """

        context = {
            "message": self.message_with_image_and_title,
            "search_term": self.search_term,
        }

        rendered_template = render_template(
            string=self.template,
            context=context,
        )

        expected_result = (
            '<img src="https://lorem-ipsum.com/lorem-ipsum.jpg" title="Lorem Ipsum"/> '
            '<span class="aa-forum-search-term-highlight">Lorem</span> Ipsum'
        )

        self.assertEqual(rendered_template, expected_result)
