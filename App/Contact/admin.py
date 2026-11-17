from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from unfold.decorators import display

from .models import AdmissionInquiry, SanctuaryContactInfo


@admin.register(SanctuaryContactInfo)
class SanctuaryContactInfoAdmin(ModelAdmin):
    """
    Unfold admin configuration for Sanctuary Location, Helplines & Center Details.
    """
    list_display = ('center_name', 'helpline_phone', 'whatsapp_number', 'email', 'opening_hours', 'updated_at')
    search_fields = ('center_name', 'helpline_phone', 'email', 'address_line1')

    fieldsets = (
        (
            _('Center Identity & Hero'),
            {
                'fields': ('center_name', 'tagline', 'hero_description'),
            },
        ),
        (
            _('Sanctuary Address & Maps'),
            {
                'fields': ('address_line1', 'address_line2', 'pincode', 'google_maps_url'),
            },
        ),
        (
            _('Helplines & Official Contact'),
            {
                'fields': ('helpline_phone', 'whatsapp_number', 'email'),
                'description': _('The WhatsApp number will receive incoming click-to-chat inquiry messages.'),
            },
        ),
        (
            _('Sanctuary Hours & Nursing Support'),
            {
                'fields': ('opening_hours', 'nursing_hours'),
            },
        ),
        (
            _('Visiting Feroke Centre Panel'),
            {
                'fields': ('visiting_center_title', 'visiting_center_location', 'visiting_center_description'),
            },
        ),
        (
            _('Social Media Channels'),
            {
                'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'twitter_url', 'linkedin_url', 'pinterest_url'),
            },
        ),
    )


@admin.register(AdmissionInquiry)
class AdmissionInquiryAdmin(ModelAdmin):
    """
    Unfold admin configuration for incoming Admission & Therapy inquiries.
    """
    list_display = (
        'display_applicant',
        'display_program',
        'bystander_accommodation',
        'status',
        'display_whatsapp_link',
        'created_at',
    )
    list_filter = (
        ('status', ChoicesDropdownFilter),
        ('program', ChoicesDropdownFilter),
        ('bystander_accommodation', ChoicesDropdownFilter),
        'created_at',
    )
    list_editable = ('status',)
    search_fields = ('name', 'phone_number', 'requirements_or_due_date', 'notes')
    readonly_fields = ('created_at', 'display_whatsapp_button')
    ordering = ('-created_at',)

    fieldsets = (
        (
            _('Applicant Details'),
            {
                'fields': ('name', 'phone_number', 'display_whatsapp_button'),
            },
        ),
        (
            _('Program & Accommodation'),
            {
                'fields': ('program', 'bystander_accommodation', 'requirements_or_due_date'),
            },
        ),
        (
            _('Inquiry Status & Doctor Notes'),
            {
                'fields': ('status', 'notes', 'created_at'),
            },
        ),
    )

    @display(description=_('Applicant'), header=True)
    def display_applicant(self, instance):
        return [instance.name, instance.phone_number]

    @display(description=_('Program / Therapy'), label=True)
    def display_program(self, instance):
        return instance.get_program_display()

    @display(
        description=_('Status'),
        label={
            'new': 'warning',
            'contacted': 'info',
            'scheduled': 'primary',
            'admitted': 'success',
            'closed': 'danger',
        },
    )
    def display_status(self, instance):
        return instance.status

    @display(description=_('WhatsApp Chat'))
    def display_whatsapp_link(self, instance):
        url = instance.get_whatsapp_url()
        return format_html(
            '<a href="{}" target="_blank" class="inline-flex items-center gap-1 font-semibold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400">'
            '<span class="material-symbols-outlined text-sm">chat</span> Chat</a>',
            url,
        )

    @display(description=_('Open Direct WhatsApp Chat'))
    def display_whatsapp_button(self, instance):
        if not instance.pk:
            return '-'
        url = instance.get_whatsapp_url()
        return format_html(
            '<a href="{}" target="_blank" class="inline-flex items-center gap-2 px-3 py-1.5 rounded-default bg-emerald-600 text-white font-medium hover:bg-emerald-700 shadow-xs">'
            '<span class="material-symbols-outlined text-base">chat</span> Connect with Guest on WhatsApp</a>',
            url,
        )
