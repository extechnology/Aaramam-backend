from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
    EmailOrPhoneAdminAuthenticationForm,
)

User = get_user_model()

# Customize the login form for the Unfold admin site
admin.site.login_form = EmailOrPhoneAdminAuthenticationForm

# Re-register Group with Unfold ModelAdmin for consistent cards and styling
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """
    Unfold-styled Group Admin with full-width cards and spacious permissions selector.
    """
    filter_horizontal = ('permissions',)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Unfold-styled Admin configuration for the custom User model.
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        'display_user',
        'phone_number',
        'display_staff',
        'display_active',
        'date_joined',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'phone_number',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_active',
                ),
            },
        ),
    )

    @display(description=_('User'), header=True)
    def display_user(self, instance):
        name = instance.full_name
        email = instance.email or _('No email')
        return [name, email]

    @display(description=_('Staff'), boolean=True)
    def display_staff(self, instance):
        return instance.is_staff

    @display(description=_('Active'), boolean=True)
    def display_active(self, instance):
        return instance.is_active
