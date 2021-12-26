# Django
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA Forum
from aa_forum import __version__
from aa_forum.tests.utils import create_fake_user


class TestMainCharacterName(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_name }}"
        )

    def test_should_contain_character_name_for_users_with_main(self):
        # given
        user = create_fake_user(1001, "Bruce Wayne")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "Bruce Wayne")

    def test_should_contain_user_character_name_for_users_without_main(self):
        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "john")

    def test_should_be_empty_for_None(self):
        # given
        context = Context({"user": None})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "")


class TestMainCharacterId(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template("{% load aa_forum_user %}{{ user|main_character_id }}")

    def test_should_contain_character_id_for_users_with_main(self):
        # given
        user = create_fake_user(1001, "Bruce Wayne")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1001")

    def test_should_contain_dummy_id_for_users_without_main(self):
        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_None(self):
        # given
        context = Context({"user": None})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1")


class TestMainCharacterCorporationName(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_corporation_name }}"
        )

    def test_should_contain_corp_name_for_users_with_main(self):
        # given
        user = create_fake_user(1001, "Bruce Wayne", 2001, "Wayne Tech Inc.", "WYT")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "Wayne Tech Inc.")

    def test_should_be_empty_for_users_without_main(self):
        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_None(self):
        # given
        context = Context({"user": None})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "")


class TestMainCorporationId(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_corporation_id }}"
        )

    def test_should_contain_corporation_id_for_users_with_main(self):
        # given
        user = create_fake_user(1001, "Bruce Wayne", 2001, "Wayne Tech Inc.", "WYT")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "2001")

    def test_should_be_dummy_id_for_users_without_main(self):
        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_None(self):
        # given
        context = Context({"user": None})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1")


class TestMainCharacterAllianceName(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_alliance_name }}"
        )

    def test_should_contain_alliance_name_for_users_with_main(self):
        # given
        user = create_fake_user(
            1001,
            "Bruce Wayne",
            2001,
            "Wayne Tech Inc.",
            "WYT",
            3001,
            "Wayne Enterprices",
        )
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "Wayne Enterprices")

    def test_should_be_empty_for_users_without_main(self):
        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "")

    def test_should_be_empty_for_None(self):
        # given
        context = Context({"user": None})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "")


class TestMainAllianceId(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            "{% load aa_forum_user %}{{ user|main_character_alliance_id }}"
        )

    def test_should_contain_alliance_id_for_users_with_main(self):
        # given
        user = create_fake_user(
            1001,
            "Bruce Wayne",
            2001,
            "Wayne Tech Inc.",
            "WYT",
            3001,
            "Wayne Enterprices",
        )
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "3001")

    def test_should_be_dummy_id_for_users_without_main(self):
        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1")

    def test_should_be_dummy_id_for_None(self):
        # given
        context = Context({"user": None})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1")


class TestForumTemplateVariables(TestCase):
    def test_set_template_variable(self):
        context = Context({"content": "bar"})
        template_to_render = Template(
            "{% load aa_forum_template_variables %}"
            "{% set_template_variable foo = content %}"
            "{{ foo }}"
        )

        rendered_template = template_to_render.render(context)

        self.assertInHTML("bar", rendered_template)

    def test_should_raise_template_syntax_error(self):
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
    def test_versioned_static(self):
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
