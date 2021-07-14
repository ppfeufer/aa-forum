"""
Forms
"""

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from django import forms
from django.contrib.auth.models import Group
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from aa_forum.models import Board, Category, Message, Topic


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


class SpecialModelChoiceIterator(forms.models.ModelChoiceIterator):
    """
    Variant of Django's ModelChoiceIterator to prevent it from always re-fetching the
    given queryset from database.
    """

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)

        queryset = self.queryset

        for obj in queryset:
            yield self.choice(obj)


class SpecialModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Variant of Django's ModelMultipleChoiceField to prevent it from always
    re-fetching the given queryset from database.
    """

    iterator = SpecialModelChoiceIterator

    def _get_queryset(self):
        return self._queryset

    def _set_queryset(self, queryset):
        self._queryset = queryset
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)


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
            config_name="aa_forum",
            attrs={"rows": 10, "cols": 20, "style": "width: 100%;"},
        ),
        required=True,
        label=get_mandatory_form_label_text(_("Message")),
    )


class EditTopicForm(ModelForm):
    """
    Edit category form
    """

    subject = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(_("Subject")),
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": _("Subject")}),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Topic
        fields = ["subject"]


class NewCategoryForm(ModelForm):
    """
    New category form
    """

    name = forms.CharField(
        required=True,
        label=get_mandatory_form_label_text(_("Name")),
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": _("Category Name")}),
    )
    boards = forms.CharField(
        required=False,
        label=_("Boards"),
        help_text=_(
            "Boards to be created with this category (One board per line). These "
            "boards will have no group restrictions, so you have to add them later "
            "where needed."
        ),
        widget=forms.Textarea(
            attrs={
                "rows": 10,
                "cols": 20,
                "input_type": "textarea",
                "placeholder": _("Boards"),
            }
        ),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Category
        fields = ["name", "boards"]


class EditCategoryForm(ModelForm):
    """
    Edit category form
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


class EditBoardForm(ModelForm):
    """
    Edit board form
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
    groups = SpecialModelMultipleChoiceField(
        required=False, queryset=Group.objects.all()
    )

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
    Edit message form
    """

    message = forms.CharField(
        widget=CKEditorUploadingWidget(
            config_name="aa_forum",
            attrs={"rows": 10, "cols": 20, "style": "width: 100%;"},
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
