# Standard Library
from unittest.mock import patch

# Django
from django.test import RequestFactory, TestCase
from django.urls import reverse

# AA Forum
from aa_forum import helpers
from aa_forum.forms import NewCategoryForm


@patch("aa_forum.helpers.messages")
class TestHelpers(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_should_send_form_errors_as_messages(self, messages):
        # given
        form = NewCategoryForm({"name": "Dummy"})
        form.add_error("name", "error message 1")
        form.add_error(None, "error message 2")
        request = self.factory.get(reverse("aa_forum:forum_index"))
        # when
        helpers.message_form_errors(request, form)
        # then
        args, _ = messages.error.call_args_list[0]
        self.assertIn("error message 1", args[1])
        args, _ = messages.error.call_args_list[1]
        self.assertIn("error message 2", args[1])

    def test_should_do_nothing_when_form_has_no_errors(self, messages):
        # given
        form = NewCategoryForm({"name": "Dummy"})
        request = self.factory.get(reverse("aa_forum:forum_index"))
        # when
        helpers.message_form_errors(request, form)
        # then
        self.assertFalse(messages.error.called)

    def test_should_return_cleaned_string(self, messages):
        string = (
            'this is a script test. <script type="text/javascript">alert('
            "'test')</script>and this is style test. <style>.MathJax, "
            ".MathJax_Message, .MathJax_Preview{display: none}</style>end tests."
        )

        cleaned_string = helpers.string_cleanup(string)

        self.assertIn(
            "this is a script test. and this is style test. end tests.", cleaned_string
        )
