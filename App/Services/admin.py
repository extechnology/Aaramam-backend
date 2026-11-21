from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.decorators import action, display

from App.common.export import SERVICE_INQUIRY_COLUMNS, export_to_csv, export_to_excel
from App.common.widgets import PersistentInlinesMixin

from .models import (
    Service,
    ServiceAmenity,
    ServiceCarePillar,
    ServiceCategory,
    ServiceImage,
    ServiceInclusion,
    ServiceInquiry,
    ServiceTherapy,
)


class ServiceImageInline(TabularInline):
    """
    Inline gallery editor for multiple service package images.
    """
    model = ServiceImage
    extra = 3
    tab = True
    fields = ('image', 'caption', 'alt_text', 'is_primary', 'order')


class ServiceTherapyInline(TabularInline):
    """
    Inline editor for formulations & therapies pills under "THERAPEUTIC CARE & FORMULATIONS".
    """
    model = ServiceTherapy
    extra = 4
    tab = True
    fields = ('name', 'order')


class ServiceAmenityInline(TabularInline):
    """
    Inline editor for Key Highlights / Amenities (left-hand 2x2 grid in detailed modal).
    """
    model = ServiceAmenity
    extra = 4
    tab = True
    fields = ('title', 'subtext', 'icon', 'order')


class ServiceCarePillarInline(TabularInline):
    """
    Inline editor for Care Pillars (right-hand 2x2 grid in detailed modal).
    """
    model = ServiceCarePillar
    extra = 4
    tab = True
    fields = ('title', 'subtext', 'icon', 'order')


class ServiceInclusionInline(TabularInline):
    """
    Inline editor for checklist items under "WHAT'S INCLUDED IN THIS SANCTUARY PACKAGE:".
    """
    model = ServiceInclusion
    extra = 4
    tab = True
    fields = ('text', 'order')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(ModelAdmin):
    """
    Unfold Admin configuration for Service Categories / Filter Tabs.
    """
    list_display = ('name', 'slug', 'display_active', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    @display(description=_('Active'), boolean=True)
    def display_active(self, instance):
        return instance.is_active


@admin.register(Service)
class ServiceAdmin(PersistentInlinesMixin, ModelAdmin):
    """
    Unfold Admin configuration for Service Packages & Detailed Modal.
    """
    list_display = (
        'display_package',
        'category',
        'display_badge',
        'duration_tag',
        'display_images_count',
        'display_rating',
        'display_active',
        'display_featured',
        'order',
    )
    list_filter = (
        ('category', RelatedDropdownFilter),
        'is_active',
        'is_featured',
        'badge_tag',
    )
    list_editable = ('order',)
    search_fields = ('title', 'subtitle', 'short_description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [
        ServiceImageInline,
        ServiceTherapyInline,
        ServiceAmenityInline,
        ServiceCarePillarInline,
        ServiceInclusionInline,
    ]

    fieldsets = (
        (
            _('Overview'),
            {
                'fields': ('title', 'slug', 'category', 'subtitle', 'doctor_guidance'),
            },
        ),
        (
            _('Badges & Tags'),
            {
                'fields': ('badge_tag', 'duration_tag', 'image_overlay_badge'),
                'description': _('e.g. badge_tag="AYURVEDIC POSTNATAL" and image_overlay_badge="Doctor-Led Wellness"'),
            },
        ),
        (
            _('Media'),
            {
                'fields': ('image',),
            },
        ),
        (
            _('Rating & Social Proof'),
            {
                'fields': ('rating', 'review_count'),
            },
        ),
        (
            _('Descriptions & Modal Content'),
            {
                'fields': ('short_description', 'detailed_description', 'recommended_for'),
            },
        ),
        (
            _('Heritage Banner'),
            {
                'fields': ('heritage_title', 'heritage_location'),
            },
        ),
        (
            _('Location & Price'),
            {
                'fields': ('location', 'price'),
            },
        ),
        (
            _('Visibility & Sorting'),
            {
                'fields': ('is_active', 'is_featured', 'order'),
            },
        ),
    )

    @display(description=_('Package'), header=True)
    def display_package(self, instance):
        return [instance.title, instance.subtitle or instance.location]

    @display(description=_('Badge'), label=True)
    def display_badge(self, instance):
        return f"#{instance.badge_tag}" if instance.badge_tag else None

    @display(description=_('Rating'))
    def display_rating(self, instance):
        return f"★ {instance.rating} ({instance.review_count})"

    @display(description=_('Active'), boolean=True)
    def display_active(self, instance):
        return instance.is_active

    @display(description=_('Featured'), boolean=True)
    def display_featured(self, instance):
        return instance.is_featured

    @display(description=_('Gallery'))
    def display_images_count(self, instance):
        count = instance.images.count()
        has_cover = bool(instance.image)
        total = count + (1 if has_cover else 0)
        return f"📷 {total} image{'s' if total != 1 else ''}"


@admin.register(ServiceImage)
class ServiceImageAdmin(ModelAdmin):
    """
    Unfold Admin for managing individual service package gallery images.
    """
    list_display = (
        'service',
        'display_thumbnail',
        'caption',
        'display_primary',
        'order',
        'created_at',
    )
    list_filter = (
        ('service', RelatedDropdownFilter),
        'is_primary',
    )
    list_editable = ('order',)
    search_fields = ('caption', 'alt_text', 'service__title')
    ordering = ('service', 'order', 'id')

    @display(description=_('Thumbnail'))
    def display_thumbnail(self, instance):
        if instance.image:
            return format_html(
                '<img src="{}" style="width: 52px; height: 38px; object-fit: cover; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);" />',
                instance.image.url
            )
        return "-"

    @display(description=_('Primary'), boolean=True)
    def display_primary(self, instance):
        return instance.is_primary


@admin.register(ServiceInquiry)
class ServiceInquiryAdmin(ModelAdmin):
    """
    Unfold Admin configuration for "Enquire Now" submissions.
    """
    list_display = (
        'display_applicant',
        'phone_number',
        'email',
        'service',
        'display_status',
        'created_at',
    )
    list_filter = (
        ('status', ChoicesDropdownFilter),
        'service',
        'created_at',
    )
    search_fields = ('name', 'phone_number', 'email', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions_list = ['export_all_excel', 'export_all_csv']
    actions = ['export_selected_excel', 'export_selected_csv']

    @action(description=_('Export to Excel (.xlsx)'), icon='file_download')
    def export_all_excel(self, request):
        qs = self.get_queryset(request)
        return export_to_excel(qs, 'Aaramam_Package_Inquiries', 'Package Inquiries', SERVICE_INQUIRY_COLUMNS)

    @action(description=_('Export to CSV (.csv)'), icon='download')
    def export_all_csv(self, request):
        qs = self.get_queryset(request)
        return export_to_csv(qs, 'Aaramam_Package_Inquiries', SERVICE_INQUIRY_COLUMNS)

    @action(description=_('Export selected to Excel (.xlsx)'))
    def export_selected_excel(self, request, queryset):
        return export_to_excel(queryset, 'Aaramam_Selected_Package_Inquiries', 'Selected Inquiries', SERVICE_INQUIRY_COLUMNS)

    @action(description=_('Export selected to CSV (.csv)'))
    def export_selected_csv(self, request, queryset):
        return export_to_csv(queryset, 'Aaramam_Selected_Package_Inquiries', SERVICE_INQUIRY_COLUMNS)

    @display(description=_('Lead / Applicant'), header=True)
    def display_applicant(self, instance):
        return [instance.name, instance.phone_number]

    @display(
        description=_('Status'),
        label={
            'new': 'warning',
            'contacted': 'info',
            'converted': 'success',
            'closed': 'danger',
        },
    )
    def display_status(self, instance):
        return instance.status
