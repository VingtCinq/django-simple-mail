
from django import forms
from django.utils.translation import gettext_lazy as _


class AdminSendTestMailForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    required_css_class = 'required'
    email = forms.EmailField(
        label=_("Email"),
        required=True
    )