from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import HeroBanner


@admin.register(HeroBanner)
class HeroBannerAdmin(ModelAdmin):
    """
    Unfold Admin for managing the Home Hero Banner.
    Clean interface to update the hero image, title, description, and 100+/200+ stat.
    """
    list_display = (
        'display_title',
        'display_thumbnail',
        'display_stat',
        'display_active',
        'updated_at',
    )
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

    fieldsets = (
        (
            _('Banner Headline & Description'),
            {
                'fields': (
                    'title',
                    'description',
                ),
            },
        ),
        (
            _('Banner Image'),
            {
                'fields': (
                    'image',
                ),
                'description': _('Upload the main sanctuary hero banner photo.'),
            },
        ),
        (
            _('Stat Highlight (e.g. 100+ / 200+)'),
            {
                'fields': (
                    ('stat_number', 'stat_label'),
                ),
                'description': _('Metric highlighted on the banner (e.g. 100+ or 200+ and Rejuvenated Guests).'),
            },
        ),
        (
            _('Status'),
            {
                'fields': (
                    'is_active',
                ),
            },
        ),
    )

    @display(description=_('Headline'), header=True)
    def display_title(self, instance):
        return [
            instance.title,
            instance.description[:70] + "..." if len(instance.description) > 70 else instance.description
        ]

    @display(description=_('Banner Image'))
    def display_thumbnail(self, instance):
        if instance.image:
            return format_html(
                '<img src="{}" style="width: 72px; height: 44px; object-fit: cover; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);" />',
                instance.image.url
            )
        return _("No image")

    @display(description=_('Stat Highlight'), label=True)
    def display_stat(self, instance):
        return f"{instance.stat_number} {instance.stat_label}"

    @display(description=_('Active'), boolean=True)
    def display_active(self, instance):
        return instance.is_active
