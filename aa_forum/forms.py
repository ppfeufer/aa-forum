"""
Forms
"""

# Django
from django import forms
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, URLValidator
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# CKEditor
from django_ckeditor_5.widgets import CKEditor5Widget

# AA Forum
from aa_forum.app_settings import discord_messaging_proxy_available
from aa_forum.helper.forms import message_empty
from aa_forum.helper.text import string_cleanup
from aa_forum.models import (
    Board,
    Category,
    General,
    Message,
    PersonalMessage,
    Setting,
    Topic,
    UserProfile,
)


def get_mandatory_form_label_text(text):
    """
    Returns a label text with a mandatory marker

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
    given queryset from the database.
    """

    def __iter__(self):
        """
        Iterate over the choices

        :return:
        :rtype:
        """

        if self.field.empty_label is not None:
            yield "", self.field.empty_label

        queryset = self.queryset

        for obj in queryset:
            yield self.choice(obj=obj)


class SpecialModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Variant of Django's ModelMultipleChoiceField to prevent it from always
    re-fetching the given queryset from the database.
    """

    iterator = SpecialModelChoiceIterator

    def _get_queryset(self):
        """
        Get the queryset

        :return:
        :rtype:
        """

        return self._queryset

    def _set_queryset(self, queryset):
        """
        Set the queryset

        :param queryset:
        :type queryset:
        :return:
        :rtype:
        """

        self._queryset = queryset
        self.widget.choices = self.choices

    queryset = property(_get_queryset, _set_queryset)


class NewTopicForm(ModelForm):
    """
    New topic form
    """

    # Non-model field, so we have to define it here and not in the Meta class.
    message = forms.CharField(
        widget=CKEditor5Widget(
            config_name="extends",
            attrs={
                "class": "aa-forum-ckeditor django_ckeditor_5",
                "rows": 10,
                "cols": 20,
                "style": "width: 100%;",
            },
        ),
        required=False,  # We have to set this to False, otherwise CKEditor5 will not work
        label=get_mandatory_form_label_text(text=_("Message")),
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Topic

        fields = ["subject", "message"]
        labels = {"subject": get_mandatory_form_label_text(text=_("Subject"))}
        widgets = {
            "subject": forms.TextInput(attrs={"placeholder": _("Subject")}),
        }

    def clean(self):
        """
        Clean the form

        :return:
        :rtype:
        """

        cleaned_data = super().clean()

        if message_empty(message=cleaned_data.get("message")):
            raise ValidationError(_("You have forgotten the message!"))

        return cleaned_data

    def clean_message(self):
        """
        Cleanup the message

        :return:
        :rtype:
        """

        message = string_cleanup(string=self.cleaned_data["message"])

        if not message:
            raise ValidationError(_("You have forgotten the message!"))

        return message


class EditTopicForm(ModelForm):
    """
    Edit category form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Topic

        fields = ["subject"]
        labels = {"subject": get_mandatory_form_label_text(text=_("Subject"))}
        widgets = {
            "subject": forms.TextInput(attrs={"placeholder": _("Subject")}),
        }


class NewCategoryForm(ModelForm):
    """
    New category form
    """

    # Non-model field, so we have to define it here and not in the Meta class.
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
        labels = {"name": get_mandatory_form_label_text(text=_("Name"))}
        widgets = {"name": forms.TextInput(attrs={"placeholder": _("Category name")})}


class EditCategoryForm(ModelForm):
    """
    Edit category form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Category

        fields = ["name"]
        labels = {"name": get_mandatory_form_label_text(text=_("Name"))}
        widgets = {"name": forms.TextInput(attrs={"placeholder": _("Category name")})}


class EditBoardForm(ModelForm):
    """
    Edit board form
    """

    def __init__(self, *args, **kwargs):
        """
        When form is initialized

        :param args:
        :param kwargs:
        """

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
        labels = {
            "name": get_mandatory_form_label_text(text=_("Name")),
            "description": _("Description"),
            "groups": _("Group restrictions"),
            "discord_webhook": _("Discord webhook (optional)"),
            "use_webhook_for_replies": _(
                "Use this Discord webhook for replies as well?"
            ),
            "is_announcement_board": _('Mark board as "Announcement Board"'),
            "announcement_groups": _(
                'Start topic restrictions for "Announcement Boards"'
            ),
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": _("Board name")}),
            "description": forms.Textarea(
                attrs={
                    "rows": 10,
                    "cols": 20,
                    "input_type": "textarea",
                    "placeholder": _("Board description (optional)"),
                }
            ),
            "discord_webhook": forms.TextInput(
                attrs={
                    "placeholder": "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # pylint: disable=line-too-long
                }
            ),
        }
        querysets = {
            "groups": Group.objects.none(),
            "announcement_groups": Group.objects.none(),
        }


class EditMessageForm(ModelForm):
    """
    Edit message form
    """

    # Non-model fields, so we have to define them here and not in the Meta class.
    close_topic = forms.BooleanField(
        required=False,
        label=_("Close topic"),
        help_text=_(
            "If checked, this topic will be closed after posting this message."
        ),
    )

    reopen_topic = forms.BooleanField(
        required=False,
        label=_("Reopen topic"),
        help_text=_(
            "If checked, this topic will be reopened after posting this message."
        ),
    )

    def __init__(self, *args, **kwargs):
        """
        When form is initialized

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        super().__init__(*args, **kwargs)

        # We have to set this to False, otherwise CKEditor5 will not work
        self.fields["message"].required = False

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Message

        fields = ["message", "close_topic", "reopen_topic"]
        labels = {"message": get_mandatory_form_label_text(text=_("Message"))}

    def clean(self):
        """
        Clean the form

        :return:
        :rtype:
        """

        cleaned_data = super().clean()

        if message_empty(message=cleaned_data.get("message")):
            raise ValidationError(_("You have forgotten the message!"))

        return cleaned_data

    def clean_message(self):
        """
        Cleanup the message

        :return:
        :rtype:
        """

        message = string_cleanup(string=self.cleaned_data["message"])

        if not message:
            raise ValidationError(_("You have forgotten the message!"))

        return message


class UserProfileForm(ModelForm):
    """
    Userprofile form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = UserProfile

        fields = [
            "signature",
            "website_title",
            "website_url",
            "discord_dm_on_new_personal_message",
            "show_unread_topics_dashboard_widget",
        ]
        help_texts = {
            "signature": _("Your signature will appear below your posts."),
            "website_title": _("Your website's title."),
            "website_url": _(
                "Your website's URL. (Don't forget to also set a title for your "
                "website, otherwise this field will be ignored.)"
            ),
            "discord_dm_on_new_personal_message": (
                _(
                    "Information: There is currently no module installed that can "
                    "handle Discord direct messages. Have a chat with your IT guys "
                    "to remedy this."
                )
                if discord_messaging_proxy_available() is False
                else ""
            ),
            "show_unread_topics_dashboard_widget": (
                _(
                    "Activating this setting will ad a widget to your dashboard that "
                    "shows unread topics in the forum."
                )
            ),
        }
        labels = {
            "signature": _("Signature"),
            "website_title": _("Website title"),
            "website_url": _("Website URL"),
            "discord_dm_on_new_personal_message": _(
                "PM me on Discord when I get a new personal message"
            ),
            "show_unread_topics_dashboard_widget": _(
                "Show unread topics as widget on the dashboard"
            ),
        }
        widgets = {
            "website_title": forms.TextInput(
                attrs={
                    "placeholder": _("e.g.: My Homepage"),
                }
            ),
            "website_url": forms.TextInput(
                attrs={
                    "placeholder": "https://example.com",
                }
            ),
        }

    def clean_signature(self):
        """
        Check that the signature is not longer than allowed

        :return:
        :rtype:
        """

        signature = string_cleanup(string=self.cleaned_data["signature"])

        if not signature:
            return ""

        max_signature_length = Setting.objects.get_setting(
            setting_key=Setting.Field.USERSIGNATURELENGTH
        )

        try:
            MaxLengthValidator(max_signature_length)(signature)
        except ValidationError as exc:
            raise ValidationError(
                _(
                    f"Ensure your signature has at most {max_signature_length} characters. (Currently: {len(signature)})"  # pylint: disable=line-too-long
                )
            ) from exc

        return signature

    def clean_website_url(self):
        """
        Check if it's a valid URL

        :return:
        :rtype:
        """

        website_url = self.cleaned_data["website_url"]

        if not website_url:
            return ""

        try:
            URLValidator()(website_url)
        except ValidationError as exc:
            raise ValidationError(_("This is not a valid URL")) from exc

        return website_url


class SettingForm(ModelForm):
    """
    Edit message form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = Setting

        fields = ["messages_per_page", "topics_per_page", "user_signature_length"]
        labels = {
            "messages_per_page": get_mandatory_form_label_text(
                Setting.Field.MESSAGESPERPAGE.label  # pylint: disable=no-member
            ),
            "topics_per_page": get_mandatory_form_label_text(
                Setting.Field.TOPICSPERPAGE.label  # pylint: disable=no-member
            ),
            "user_signature_length": get_mandatory_form_label_text(
                Setting.Field.USERSIGNATURELENGTH.label  # pylint: disable=no-member
            ),
        }


class NewPersonalMessageForm(ModelForm):
    """
    New personal message form
    """

    def __init__(self, *args, **kwargs):
        """
        When form is initialized

        :param args:
        :param kwargs:
        """

        super().__init__(*args, **kwargs)

        self.fields["recipient"].queryset = General.users_with_basic_access()
        self.fields["message"].required = False

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = PersonalMessage

        fields = ["recipient", "subject", "message"]
        labels = {
            "message": get_mandatory_form_label_text(text=_("Message")),
            "recipient": get_mandatory_form_label_text(text=_("Recipient")),
            "subject": get_mandatory_form_label_text(text=_("Subject")),
        }
        querysets = {"recipient": User.objects.none()}

    def clean(self):
        """
        Clean the form

        :return:
        :rtype:
        """

        cleaned_data = super().clean()

        if message_empty(message=cleaned_data.get("message")):
            raise ValidationError(_("You have forgotten the message!"))

        return cleaned_data

    def clean_message(self):
        """
        Cleanup the message

        :return:
        :rtype:
        """

        message = string_cleanup(string=self.cleaned_data["message"])

        if not message:
            raise ValidationError(_("You have forgotten the message!"))

        return message


class ReplyPersonalMessageForm(ModelForm):
    """
    Reply to personal message form
    """

    def __init__(self, *args, **kwargs):
        """
        When form is initialized

        :param args:
        :param kwargs:
        """

        super().__init__(*args, **kwargs)

        self.fields["message"].required = False

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = PersonalMessage

        fields = ["message"]
        labels = {"message": get_mandatory_form_label_text(text=_("Message"))}

    def clean(self):
        """
        Clean the form

        :return:
        :rtype:
        """

        cleaned_data = super().clean()

        if message_empty(message=cleaned_data.get("message")):
            raise ValidationError(_("You have forgotten the message!"))

        return cleaned_data

    def clean_message(self):
        """
        Cleanup the message

        :return:
        :rtype:
        """

        message = string_cleanup(string=self.cleaned_data["message"])

        if not message:
            raise ValidationError(_("You have forgotten the message!"))

        return message
