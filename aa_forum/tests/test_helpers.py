"""
Test for the helpers
"""

# Standard Library
from unittest.mock import patch

# Django
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# Alliance Auth (External Libs)
from app_utils.testing import create_eve_character, create_fake_user

# AA Forum
from aa_forum.forms import NewCategoryForm
from aa_forum.helper.eve_images import get_character_portrait_from_evecharacter
from aa_forum.helper.forms import message_form_errors
from aa_forum.helper.text import get_first_image_url_from_text, string_cleanup
from aa_forum.helper.user import get_main_character_from_user
from aa_forum.models import get_sentinel_user


@patch("aa_forum.helper.forms.messages")
class TestHelperForms(TestCase):
    """
    Testing the form helpers
    """

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_should_send_form_errors_as_messages(self, messages):
        """
        Test should send form errors as messages

        :param messages:
        :type messages:
        :return:
        :rtype:
        """

        # given
        form = NewCategoryForm({"name": "Dummy"})
        form.add_error(field="name", error="error message 1")
        form.add_error(field=None, error="error message 2")
        request = self.factory.get(path=reverse(viewname="aa_forum:forum_index"))

        # when
        message_form_errors(request=request, form=form)

        # then
        _, result = messages.error.call_args_list[0]
        self.assertIn(member="Error: error message 1", container=result["message"])
        _, result = messages.error.call_args_list[1]
        self.assertIn(member="Error: error message 2", container=result["message"])

    def test_should_do_nothing_when_form_has_no_errors(self, messages):
        """
        Test should do nothing when form has no errors

        :param messages:
        :type messages:
        :return:
        :rtype:
        """

        # given
        form = NewCategoryForm({"name": "Dummy"})
        request = self.factory.get(path=reverse(viewname="aa_forum:forum_index"))

        # when
        message_form_errors(request=request, form=form)

        # then
        self.assertFalse(expr=messages.error.called)


class TestHelperText(TestCase):
    """
    Testing the text helpers
    """

    def test_should_return_cleaned_string(self):
        """
        Test should return cleaned string

        :return:
        :rtype:
        """

        # given
        string = (
            'this is a script test. <script type="text/javascript">alert('
            "'test')</script>and this is style test. <style>.MathJax, "
            ".MathJax_Message, .MathJax_Preview{display: none}</style>end tests."
        )

        # when
        cleaned_string = string_cleanup(string=string)

        # then
        self.assertIn(
            member="this is a script test. and this is style test. end tests.",
            container=cleaned_string,
        )

    def test_should_return_none_for_get_image_url(self):
        """
        Test should return none for get_image_url because there is none

        :return:
        :rtype:
        """

        text = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris "
            "vehicula viverra diam at ultrices. Donec accumsan metus vitae sapien "
            "malesuada, quis molestie quam euismod. Vestibulum malesuada non felis "
            "id pellentesque. Proin in sollicitudin massa. Vestibulum vitae ante "
            "quis dolor placerat feugiat. Praesent id gravida nulla, sed malesuada "
            "arcu. Fusce eu erat feugiat, tincidunt dolor varius, tincidunt velit. "
            "Mauris iaculis elit luctus nunc scelerisque mollis. Etiam imperdiet "
            "mi lacus, at sodales eros aliquet a. Maecenas pretium, odio et "
            "ultricies venenatis, nisl dui volutpat dui, vitae feugiat turpis "
            "dolor vel nisi. Mauris consequat, nulla id mattis ullamcorper, "
            "enim elit convallis erat, eget tempor velit mauris ac nisl. Praesent "
            "sit amet facilisis purus, mattis dictum dolor. Nam id ex sollicitudin "
            "nulla dictum rutrum."
        )

        image_url = get_first_image_url_from_text(text=text)

        self.assertIsNone(obj=image_url)

    def test_should_return_none_for_get_image_url_2(self):
        """
        Test should return none for get_image_url because it's invalid

        :return:
        :rtype:
        """

        text = (
            'Lorem ipsum dolor sit amet, <img src="consectetur adipiscing elit">. Mauris '
            "vehicula viverra diam at ultrices. Donec accumsan metus vitae sapien "
            "malesuada, quis molestie quam euismod. Vestibulum malesuada non felis "
            "id pellentesque. Proin in sollicitudin massa. Vestibulum vitae ante "
            "quis dolor placerat feugiat. Praesent id gravida nulla, sed malesuada "
            "arcu. Fusce eu erat feugiat, tincidunt dolor varius, tincidunt velit. "
            "Mauris iaculis elit luctus nunc scelerisque mollis. Etiam imperdiet "
            "mi lacus, at sodales eros aliquet a. Maecenas pretium, odio et "
            "ultricies venenatis, nisl dui volutpat dui, vitae feugiat turpis "
            "dolor vel nisi. Mauris consequat, nulla id mattis ullamcorper, "
            "enim elit convallis erat, eget tempor velit mauris ac nisl. Praesent "
            "sit amet facilisis purus, mattis dictum dolor. Nam id ex sollicitudin "
            "nulla dictum rutrum."
        )

        image_url = get_first_image_url_from_text(text=text)

        self.assertIsNone(obj=image_url)

    def test_should_return_first_image_url_for_get_image_url(self):
        """
        Test should return first image URL for get_image_url

        :return:
        :rtype:
        """

        text = (
            'Lorem ipsum dolor sit amet, <img src="https://test.de/foobar.jpg">. Mauris '
            "vehicula viverra diam at ultrices. Donec accumsan metus vitae sapien "
            "malesuada, quis molestie quam euismod. Vestibulum malesuada non felis "
            "id pellentesque. Proin in sollicitudin massa. Vestibulum vitae ante "
            "quis dolor placerat feugiat. Praesent id gravida nulla, sed malesuada "
            "arcu. Fusce eu erat feugiat, tincidunt dolor varius, tincidunt velit. "
            "Mauris iaculis elit luctus nunc scelerisque mollis. Etiam imperdiet "
            'mi lacus, at sodales eros <img src="https://test.de/barfoo.jpg"> aliquet '
            "a. Maecenas pretium, odio et ultricies venenatis, nisl dui volutpat dui, "
            "vitae feugiat turpis dolor vel nisi. Mauris consequat, nulla id mattis "
            "ullamcorper, enim elit convallis erat, eget tempor velit mauris ac nisl. "
            "Praesent sit amet facilisis purus, mattis dictum dolor. Nam id ex "
            "sollicitudin nulla dictum rutrum. "
        )

        image_url = get_first_image_url_from_text(text=text)

        self.assertEqual(first=image_url, second="https://test.de/foobar.jpg")


class TestHelperEveImages(TestCase):
    """
    Testing the EVE image helpers
    """

    def setUp(self) -> None:
        self.user_1001 = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            permissions=["aa_forum.basic_access"],
        )

    def test_should_return_character_portrait_url(self):
        """
        Test should return character portrait URL

        :return:
        :rtype:
        """

        character = self.user_1001.profile.main_character

        portrait_url = get_character_portrait_from_evecharacter(character=character)
        expected_url = f"https://images.evetech.net/characters/{character.character_id}/portrait?size=32"  # pylint: disable=line-too-long

        self.assertEqual(first=portrait_url, second=expected_url)

    def test_should_return_character_portrait_html(self):
        """
        Test should return character portrait HTML

        :return:
        :rtype:
        """

        character = self.user_1001.profile.main_character

        portrait_html = get_character_portrait_from_evecharacter(
            character=character, as_html=True
        )
        expected_url = f"https://images.evetech.net/characters/{character.character_id}/portrait?size=32"  # pylint: disable=line-too-long
        expected_html = (
            '<img class="aa-forum-character-portrait img rounded" '
            f'src="{expected_url}" alt="{character.character_name}" '
            'width="32" height="32" loading="lazy">'
        )

        self.assertEqual(first=portrait_html, second=expected_html)


class TestGetMainCharacterFromUser(TestCase):
    """
    Test get_main_character_from_user
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users

        :return:
        :rtype:
        """

        super().setUpClass()
        cls.group = Group.objects.create(name="Enterprise Crew")

        cls.user_main_character = create_fake_user(
            character_id=1001, character_name="William T. Riker"
        )

        cls.character_without_profile = create_eve_character(
            character_id=1003, character_name="Christopher Pike"
        )

    def test_get_main_character_from_user_should_return_character_name(self):
        """
        Test should return the main character name for a user with a character

        :return:
        :rtype:
        """

        character_name = get_main_character_from_user(self.user_main_character)

        self.assertEqual(first=character_name, second="William T. Riker")

    def test_get_main_character_from_user_should_return_user_name(self):
        """
        Test should return the username for a user without a character

        :return:
        :rtype:
        """

        user = AuthUtils.create_user(username="John Doe")

        character_name = get_main_character_from_user(user=user)

        self.assertEqual(first=character_name, second="John Doe")

    def test_get_main_character_from_user_should_return_sentinel_user(self):
        """
        Test should return "deleted" (Sentinel User) if user has no profile

        :return:
        :rtype:
        """

        user = get_sentinel_user()

        character_name = get_main_character_from_user(user=user)

        self.assertEqual(first=character_name, second="deleted")

    def test_get_main_character_from_user_should_return_sentinel_user_for_none(self):
        """
        Test should return "deleted" (Sentinel User) if user is None

        :return:
        :rtype:
        """

        user = None

        character_name = get_main_character_from_user(user=user)

        self.assertEqual(first=character_name, second="deleted")
