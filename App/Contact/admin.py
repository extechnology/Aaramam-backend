from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter
from unfold.decorators import action, display

from App.common.export import ADMISSION_INQUIRY_COLUMNS, export_to_csv, export_to_excel
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
    search_fields = ('name', 'phone_number', 'email', 'requirements_or_due_date', 'notes')
    readonly_fields = ('created_at', 'display_whatsapp_button')
    ordering = ('-created_at',)
    actions_list = ['export_all_excel', 'export_all_csv']
    actions = ['export_selected_excel', 'export_selected_csv']

    @action(description=_('Export to Excel (.xlsx)'), icon='file_download')
    def export_all_excel(self, request):
        qs = self.get_queryset(request)
        return export_to_excel(qs, 'Aaramam_Admission_Inquiries', 'Admission Inquiries', ADMISSION_INQUIRY_COLUMNS)

    @action(description=_('Export to CSV (.csv)'), icon='download')
    def export_all_csv(self, request):
        qs = self.get_queryset(request)
        return export_to_csv(qs, 'Aaramam_Admission_Inquiries', ADMISSION_INQUIRY_COLUMNS)

    @action(description=_('Export selected to Excel (.xlsx)'))
    def export_selected_excel(self, request, queryset):
        return export_to_excel(queryset, 'Aaramam_Selected_Admission_Inquiries', 'Selected Inquiries', ADMISSION_INQUIRY_COLUMNS)

    @action(description=_('Export selected to CSV (.csv)'))
    def export_selected_csv(self, request, queryset):
        return export_to_csv(queryset, 'Aaramam_Selected_Admission_Inquiries', ADMISSION_INQUIRY_COLUMNS)

    fieldsets = (
        (
            _('Applicant Details'),
            {
                'fields': ('name', 'phone_number', 'email', 'display_whatsapp_button'),
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
        contact_line = f"{instance.phone_number} • {instance.email}" if instance.email else instance.phone_number
        return [instance.name, contact_line]

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
