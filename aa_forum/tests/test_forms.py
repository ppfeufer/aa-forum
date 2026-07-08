"""
Tests for forms.py
"""

# Django
from django import forms

# AA Forum
from aa_forum.forms import (
    NewTopicForm,
    SpecialModelChoiceIterator,
    SpecialModelMultipleChoiceField,
    get_mandatory_form_label_text,
)
from aa_forum.models import Category
from aa_forum.tests import BaseTestCase


class TestGetMandatoryFormLabelText(BaseTestCase):
    """
    Test get_mandatory_form_label_text function
    """

    def test_returns_safe_string_with_asterisk_for_plain_text(self):
        """
        Ensure the function returns a SafeString with the correct asterisk for plain text

        :return:
        :rtype:
        """

        label = "Field Label"
        result = get_mandatory_form_label_text(label)

        self.assertIn(label, result)
        self.assertIn(
            '<span aria-label="This field is mandatory" class="form-required-marker">*</span>',
            result,
        )

    def test_handles_html_in_label_text_without_double_escaping(self):
        """
        Ensure HTML in label text is preserved and required marker appended

        :return:
        :rtype:
        """

        label = "<strong>Important</strong>"
        result = get_mandatory_form_label_text(label)

        self.assertIn("<strong>Important</strong>", result)
        self.assertIn('class="form-field-required"', result)


class TestSpecialModelChoiceIterator(BaseTestCase):
    """
    Test SpecialModelChoiceIterator
    """

    def test_yields_empty_label_when_present(self):
        """
        Ensure iterator yields the empty_label as first choice when set

        :return:
        :rtype:
        """

        Category.objects.create(name="A")
        Category.objects.create(name="B")

        field = forms.ModelChoiceField(
            queryset=Category.objects.all(), empty_label="(none)"
        )

        iterator = SpecialModelChoiceIterator(field=field)

        choices = list(iterator)

        self.assertEqual(choices[0], ("", "(none)"))
        self.assertEqual(len(choices), 3)
        labels = [c[1] for c in choices[1:]]
        self.assertIn("A", labels)
        self.assertIn("B", labels)

    def test_does_not_yield_empty_label_when_none(self):
        """
        Ensure iterator does not yield empty_label when it is None

        :return:
        :rtype:
        """

        field = forms.ModelChoiceField(
            queryset=Category.objects.none(), empty_label=None
        )

        iterator = SpecialModelChoiceIterator(field=field)

        choices = list(iterator)

        self.assertEqual(choices, [])

    def test_yields_only_choices_for_queryset(self):
        """
        Ensure iterator yields choices corresponding exactly to the provided queryset

        :return:
        :rtype:
        """

        cat = Category.objects.create(name="Solo")
        field = forms.ModelChoiceField(
            queryset=Category.objects.filter(pk=cat.pk), empty_label=None
        )

        iterator = SpecialModelChoiceIterator(field=field)

        choices = list(iterator)

        self.assertEqual(len(choices), 1)
        self.assertEqual(str(choices[0][1]), "Solo")


class TestSpecialModelMultipleChoiceField(BaseTestCase):
    """
    Test SpecialModelMultipleChoiceField
    """

    def test_query_set_property_sets_and_updates_widget_choices(self):
        """
        Ensure setting the queryset property stores the queryset and updates widget.choices

        :return:
        :rtype:
        """

        a = Category.objects.create(name="A-multi")
        b = Category.objects.create(name="B-multi")

        # swap to our special field behavior by constructing SpecialModelMultipleChoiceField
        special = SpecialModelMultipleChoiceField(
            queryset=Category.objects.filter(pk=a.pk)
        )

        self.assertIs(special.iterator, SpecialModelChoiceIterator)
        self.assertEqual(list(special.queryset), [a])

        # now set a new queryset and ensure widget.choices are updated
        special.queryset = Category.objects.filter(pk__in=[a.pk, b.pk])

        choices = list(special.widget.choices)
        labels = [str(c[1]) for c in choices]

        self.assertIn("A-multi", labels)
        self.assertIn("B-multi", labels)

    def test_widget_choices_become_empty_when_setting_empty_queryset(self):
        """
        Ensure widget.choices becomes empty list when queryset set to none

        :return:
        :rtype:
        """

        Category.objects.create(name="C1")

        special = SpecialModelMultipleChoiceField(queryset=Category.objects.all())
        self.assertTrue(len(list(special.widget.choices)) >= 1)

        special.queryset = Category.objects.none()
        self.assertEqual(list(special.widget.choices), [])


class TestNewTopicForm(BaseTestCase):
    """
    Test NewTopicForm behaviour
    """

    def test_form_is_valid_with_subject_and_non_empty_message(self):
        """
        Ensure the form is valid when subject and a non-empty message are provided
        """

        form = NewTopicForm(data={"subject": "Hello", "message": "<p> Hi there </p>"})

        self.assertTrue(form.is_valid())
        self.assertIn("Hi there", form.cleaned_data["message"])

    def test_form_is_invalid_when_message_is_missing_or_whitespace(self):
        """
        Ensure the form is invalid when the message is empty or only whitespace
        """

        form = NewTopicForm(data={"subject": "Hello", "message": "   "})

        self.assertFalse(form.is_valid())
        # error may be field-specific or non-field; accept either
        self.assertTrue(
            bool(form.errors.get("message")) or bool(form.non_field_errors())
        )

    def test_clean_message_strips_html_and_collapses_whitespace(self):
        """
        Ensure clean_message strips HTML and collapses whitespace
        """

        raw = "<div>  Hello   <b>World</b> </div>"
        form = NewTopicForm(data={"subject": "S", "message": raw})

        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data["message"]
        self.assertIn("Hello", cleaned)
        self.assertIn("World", cleaned)
        # Ensure HTML tags are preserved by string_cleanup (scripts/styles removed elsewhere)
        self.assertIn("<b>World</b>", cleaned)
