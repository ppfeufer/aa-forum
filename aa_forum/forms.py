"""
Forms
"""

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


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
