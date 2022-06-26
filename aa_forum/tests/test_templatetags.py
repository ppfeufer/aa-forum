"""
Tests for the template tags
"""

# Django
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA Forum
from aa_forum import __version__
from aa_forum.models import get_sentinel_user
from aa_forum.tests.utils import create_fake_user


class TestMainCharacterName(TestCase):
    """
    Tests for main_character_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_name }}"
        )

    def test_should_contain_character_name_for_users_with_main(self):
        """
        test should contain character name for user with main set
        :return:
        """

        # given
        user = create_fake_user(1001, "Bruce Wayne")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "Bruce Wayne")

    def test_should_contain_user_character_name_for_users_without_main(self):
        """
        Should return user name for users without a main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "john")

    def test_should_return_deleted_user_for_sentinel_user(self):
        """
        Should return "deleted" for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "deleted")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty
        :return:
        """

        # given
        context = Context({"user": None})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "")


class TestMainCharacterId(TestCase):
    """
    Tests for main_character_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template("{% load aa_forum_user %}{{ user|main_character_id }}")

    def test_should_contain_character_id_for_users_with_main(self):
        """
        Test should contain main character ID for users with main
        :return:
        """

        # given
        user = create_fake_user(1001, "Bruce Wayne")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "1001")

    def test_should_contain_dummy_id_for_users_without_main(self):
        """
        Test should contain dummy ID (1) for users without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return dummy ID (1) for None
        :return:
        """

        # given
        context = Context({"user": None})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "1")


class TestMainCharacterCorporationName(TestCase):
    """
    Tests for main_character_corporation_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_corporation_name }}"
        )

    def test_should_contain_corp_name_for_users_with_main(self):
        """
        Test shoud return corporation name for users with main character
        :return:
        """

        # given
        user = create_fake_user(1001, "Bruce Wayne", 2001, "Wayne Tech Inc.", "WYT")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "Wayne Tech Inc.")

    def test_should_be_empty_for_users_without_main(self):
        """
        Test should be empty for users without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_sentinel_user(self):
        """
        Test should be empty for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty for None
        :return:
        """

        # given
        context = Context({"user": None})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "")


class TestMainCorporationId(TestCase):
    """
    Tests for main_character_corporation_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_corporation_id }}"
        )

    def test_should_contain_corporation_id_for_users_with_main(self):
        """
        Test should return main character corp ID for users with main character
        :return:
        """

        # given
        user = create_fake_user(1001, "Bruce Wayne", 2001, "Wayne Tech Inc.", "WYT")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "2001")

    def test_should_be_dummy_id_for_users_without_main(self):
        """
        Test should return dummy ID (1) for users without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})

        # when
        result = self.template.render(context)
        # then

        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return dummy ID (1) for None
        :return:
        """

        # given
        context = Context({"user": None})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "1")


class TestMainCharacterAllianceName(TestCase):
    """
    Tests for main_character_alliance_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_alliance_name }}"
        )

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

        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "Wayne Enterprices")

    def test_should_be_empty_for_users_without_main(self):
        """
        Test should be empty for users without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

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

        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_sentinel_user(self):
        """
        Test should be empty for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty for None
        :return:
        """

        # given
        context = Context({"user": None})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "")


class TestMainAllianceId(TestCase):
    """
    Tests for main_character_alliance_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_alliance_id }}"
        )

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
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "3001")

    def test_should_be_dummy_id_for_users_without_main(self):
        """
        Test should return dummy ID (1) for user without main character
        :return:
        """

        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})

        # when
        result = self.template.render(context)

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

        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return dummy ID (1) for sentinel user
        :return:
        """

        # given
        user = get_sentinel_user()
        context = Context({"user": user})

        # when
        result = self.template.render(context)

        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_none(self):
        """
        test should return dummy ID (1) for None
        :return:
        """

        # given
        context = Context({"user": None})

        # when
        result = self.template.render(context)

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

        context = Context({"content": "bar"})
        template_to_render = Template(
            "{% load aa_forum_template_variables %}"
            "{% set_template_variable foo = content %}"
            "{{ foo }}"
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML("bar", rendered_template)

    def test_should_raise_template_syntax_error(self):
        """
        Test should raise template syntax error
        :return:
        """

        self.assertRaises(
            TemplateSyntaxError,
            Template,
            "{% load aa_forum_template_variables %}"
            "{% set_template_variable foo %}"
            "{{ foo }}",
        )

        with self.assertRaisesMessage(
            TemplateSyntaxError,
            "'set_template_variable' tag must be of the form: "
            "{% set_template_variable <var_name> = <var_value> %}",
        ):
            Template(
                "{% load aa_forum_template_variables %}"
                "{% set_template_variable foo %}"
                "{{ foo }}"
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

        context = Context({"version": __version__})
        template_to_render = Template(
            "{% load aa_forum_versioned_static %}"
            "{% aa_forum_static 'aa_forum/css/aa-forum.min.css' %}"
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML(
            f'/static/aa_forum/css/aa-forum.min.css?v={context["version"]}',
            rendered_template,
        )
