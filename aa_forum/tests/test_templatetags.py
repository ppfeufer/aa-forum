from django.template import Context, Template
from django.test import TestCase

from allianceauth.tests.auth_utils import AuthUtils

from .utils import create_fake_user


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

    def test_should_contain_character_name_for_users_with_main(self):
        # given
        user = create_fake_user(1001, "Bruce Wayne")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1001")

    def test_should_contain_user_character_name_for_users_without_main(self):
        # given
        user = AuthUtils.create_user("john")
        context = Context({"user": user})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "1")

    def test_should_be_empty_for_None(self):
        # given
        context = Context({"user": None})
        # when
        result = self.template.render(context)
        # then
        self.assertEqual(result, "")
