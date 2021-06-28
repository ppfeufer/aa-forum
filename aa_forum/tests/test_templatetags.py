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
