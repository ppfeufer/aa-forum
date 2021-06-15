"""
Forms
"""

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from django import forms
from django.contrib.auth.models import Group
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from aa_forum.models import Board, Category, Message


def get_mandatory_form_label_text(text):
    """
    Label text for mandatory form fields
    :param text:
    :type text:
    :return:
    :rtype:
    """

    required_text = _("This field is mandatory")
    required_marker = (
        f'<span aria-label="{required_text}" class="form-required-marker">*</span>'
    )

    return mark_safe(
        f'<span class="form-field-required">{text} {required_marker}</span>'
    )


class NewTopicForm(forms.Form):
    """
    New topic form
    """

    subject = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(_("Subject")),
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": _("Subject")}),
    )

    message = forms.CharField(
        widget=CKEditorUploadingWidget(
            attrs={"rows": 10, "cols": 20, "style": "width: 100%;"}
        ),
        required=True,
        label=get_mandatory_form_label_text(_("Message")),
    )


class EditCategoryForm(ModelForm):
    """
    New category form
    """

    name = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(_("Name")),
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": _("Category Name")}),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Category
        fields = ["name"]


class MyModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """Variant of ModelMultipleChoiceField to prevent it from loading the
    groups queryset more than once.
    """

    def _get_queryset(self):
        return self._queryset

    def _set_queryset(self, queryset):
        self._queryset = None if queryset is None else queryset
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)


class EditBoardForm(ModelForm):
    """
    New board form
    """

    name = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(_("Name")),
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": _("Board Name")}),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
        widget=forms.Textarea(
            attrs={
                "rows": 10,
                "cols": 20,
                "input_type": "textarea",
                "placeholder": _("Board Description (Optional)"),
            }
        ),
    )
    groups = MyModelMultipleChoiceField(required=False, queryset=Group.objects.none())

    def __init__(self, *args, **kwargs):
        groups_queryset = kwargs.pop("groups_queryset", None)
        super().__init__(*args, **kwargs)
        if groups_queryset:
            self.fields["groups"].queryset = groups_queryset

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Board
        fields = ["name", "description", "groups"]


class EditMessageForm(ModelForm):
    """
    Reply form
    """

    message = forms.CharField(
        widget=CKEditorUploadingWidget(
            attrs={"rows": 10, "cols": 20, "style": "width: 100%;"}
        ),
        required=True,
        label=get_mandatory_form_label_text(_("Message")),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Message
        fields = ["message"]
