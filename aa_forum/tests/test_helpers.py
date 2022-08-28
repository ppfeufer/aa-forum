"""
Test for our helper functions
"""

# Standard Library
from unittest.mock import patch

# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse

# Alliance Auth (External Libs)
from app_utils.testing import create_fake_user

# AA Forum
from aa_forum.forms import NewCategoryForm
from aa_forum.helper.eve_images import get_character_portrait_from_evecharacter
from aa_forum.helper.forms import message_form_errors
from aa_forum.helper.text import get_image_url, string_cleanup


@patch("aa_forum.helper.forms.messages")
class TestHelperForms(TestCase):
    """
    Testing the forms helper
    """

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_should_send_form_errors_as_messages(self, messages):
        """
        Test should send form errors as message
        :param messages:
        :return:
        """

        # given
        form = NewCategoryForm({"name": "Dummy"})
        form.add_error("name", "error message 1")
        form.add_error(None, "error message 2")
        request = self.factory.get(reverse("aa_forum:forum_index"))

        # when
        message_form_errors(request, form)

        # then
        args, _ = messages.error.call_args_list[0]
        self.assertIn("error message 1", args[1])
        args, _ = messages.error.call_args_list[1]
        self.assertIn("error message 2", args[1])

    def test_should_do_nothing_when_form_has_no_errors(self, messages):
        """
        Test should do nothing when form has no errors
        :param messages:
        :return:
        """

        # given
        form = NewCategoryForm({"name": "Dummy"})
        request = self.factory.get(reverse("aa_forum:forum_index"))

        # when
        message_form_errors(request, form)

        # then
        self.assertFalse(messages.error.called)


class TestHelperText(TestCase):
    """
    Testing the text helper
    """

    def test_should_return_cleaned_string(self):
        """
        Test should return a clean/sanitized string
        :return:
        """

        # given
        string = (
            'this is a script test. <script type="text/javascript">alert('
            "'test')</script>and this is style test. <style>.MathJax, "
            ".MathJax_Message, .MathJax_Preview{display: none}</style>end tests."
        )

        # when
        cleaned_string = string_cleanup(string)

        # then
        self.assertIn(
            "this is a script test. and this is style test. end tests.", cleaned_string
        )

    def test_should_return_none_for_get_image_url(self):
        """
        Test should return none for get_image_url
        :return:
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

        image_url = get_image_url(text)

        self.assertIsNone(image_url)

    def test_should_return_none_for_get_image_url_2(self):
        """
        Test should return none for get_image_url because it's invalid
        :return:
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

        image_url = get_image_url(text)

        self.assertIsNone(image_url)

    def test_should_return_first_image_url_for_get_image_url(self):
        """
        Test should return none for get_image_url because it's invalid
        :return:
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

        image_url = get_image_url(text)

        self.assertEqual(image_url, "https://test.de/foobar.jpg")


class TestHelperEveImages(TestCase):
    """
    Testing the eve_images helpers
    """

    def setUp(self) -> None:
        self.user_1001 = create_fake_user(
            1001, "Bruce Wayne", permissions=["aa_forum.basic_access"]
        )

    def test_should_return_character_portrait_url(self):
        """
        Test should return character portrait URL
        :return:
        """

        character = self.user_1001.profile.main_character

        portrait_url = get_character_portrait_from_evecharacter(character=character)
        expected_url = f"https://images.evetech.net/characters/{character.character_id}/portrait?size=32"  # , pylint: disable=line-too-long

        self.assertEqual(portrait_url, expected_url)

    def test_should_return_character_portrait_html(self):
        """
        Test should return character portrait HTML image tag
        :return:
        """

        character = self.user_1001.profile.main_character

        portrait_html = get_character_portrait_from_evecharacter(
            character=character, as_html=True
        )
        expected_url = f"https://images.evetech.net/characters/{character.character_id}/portrait?size=32"  # , pylint: disable=line-too-long
        expected_html = (
            '<img class="aa-forum-character-portrait img-rounded" '
            f'src="{expected_url}" alt="{character.character_name}" '
            'width="32" height="32">'
        )

        self.assertEqual(portrait_html, expected_html)
