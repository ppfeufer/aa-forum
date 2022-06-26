"""
Forms
"""

# Django
from django import forms
from django.contrib.auth.models import Group
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# ckEditor
from ckeditor_uploader.widgets import CKEditorUploadingWidget

# AA Forum
from aa_forum.models import Board, Category, Message, Topic


def get_mandatory_form_label_text(text):
    """
    Label text for mandatory form fields
    :param text:
    :return:
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
        max_length=254,
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
        max_length=254,
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
        max_length=254,
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
        max_length=254,
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
        max_length=254,
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
        required=False,
        label=_("Group Restrictions"),
        help_text=_(
            "This will restrict access to this board to the selected groups. If no "
            "groups are selected, everyone who can access the forum can also access "
            "this board. (This setting is optional)"
        ),
        queryset=Group.objects.all(),
    )
    discord_webhook = forms.CharField(
        required=False,
        label=_("Discord Webhook (Optional)"),
        help_text=_(
            "Discord Webhook URL for the channel to post about new topics in this "
            "board. (This setting is optional) "
        ),
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "placeholder": "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # , pylint: disable=line-too-long
            }
        ),
    )
    use_webhook_for_replies = forms.BooleanField(
        initial=False,
        required=False,
        label=_("Use this Discord Webhook for replies as well?"),
        help_text=_(
            "When activated every reply to any topic in this board will be "
            "posted to the defined Discord channel. (Child boards are excluded) "
            "Chose wisely! (Default: NO)"
        ),
    )
    is_announcement_board = forms.BooleanField(
        initial=False,
        required=False,
        label=_("Mark Board as 'Announcement Board'"),
        help_text=_(
            "Mark this board as an 'Announcement Board', meaning that only certain "
            "selected groups can start new topics. All others who have access to this "
            "board will still be able to discuss in the topics though. This setting "
            "will not be inherited to child boards. (Default: NO)"
        ),
    )
    announcement_groups = SpecialModelMultipleChoiceField(
        required=False,
        label=_("Start Topic Restrictions for 'Announcement Boards'"),
        help_text=_(
            "User in at least one of the selected groups will be able to start topics "
            "in 'Announcement Boards'. If no group is selected, only forum admins can "
            "do so. This setting will not be inherited to child boards. (Hint: These "
            "restrictions only take effect when a board is marked as 'Announcement "
            "Board', see checkbox above.)"
        ),
        queryset=Group.objects.all(),
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
        fields = [
            "name",
            "description",
            "groups",
            "discord_webhook",
            "use_webhook_for_replies",
            "is_announcement_board",
            "announcement_groups",
        ]


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
