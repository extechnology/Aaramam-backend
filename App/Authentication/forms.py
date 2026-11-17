from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from unfold.forms import (
    AdminAuthenticationForm,
    UserChangeForm as UnfoldUserChangeForm,
    UserCreationForm as UnfoldUserCreationForm,
)

User = get_user_model()


class CustomUserCreationForm(UnfoldUserCreationForm):
    """
    Form for creating new users in Django Admin (styled with Unfold Tailwind).
    """

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'first_name', 'last_name', 'is_staff', 'is_active')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        if not email and not phone_number:
            raise forms.ValidationError(_('Either an email address or a phone number is required.'))
        return cleaned_data


class CustomUserChangeForm(UnfoldUserChangeForm):
    """
    Form for updating users in Django Admin (styled with Unfold Tailwind).
    """

    class Meta:
        model = User
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        if not email and not phone_number:
            raise forms.ValidationError(_('Either an email address or a phone number is required.'))
        return cleaned_data


class EmailOrPhoneAdminAuthenticationForm(AdminAuthenticationForm):
    """
    Custom Unfold admin authentication form clearly labeled for email or phone number.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Email or Phone Number')
        self.fields['username'].widget.attrs.update({
            'placeholder': _('Enter email or phone number'),
            'autocapitalize': 'none',
            'autocomplete': 'username',
        })
