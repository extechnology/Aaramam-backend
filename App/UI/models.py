from django.db import models
from django.utils.translation import gettext_lazy as _


class HeroBanner(models.Model):
    """
    Clean, simplified Hero Banner model:
    - Image: Main hero banner image
    - Title: Main headline (e.g. "Motherhood Begins with Love and Care.")
    - Description: Subtitle / overview text
    - Stat: Number (e.g. "100+", "200+") and Label (e.g. "Rejuvenated Guests")
    """
    title = models.CharField(
        _('title / headline'),
        max_length=255,
        default='Motherhood Begins with Love and Care.',
        help_text=_('Main banner headline')
    )
    description = models.TextField(
        _('description / subtitle'),
        default='Providing Gentle Ayurvedic Care, Comfort And Nurturing Support For Every New Mother And Baby.',
        help_text=_('Description text displayed below the title')
    )
    image = models.ImageField(
        _('banner image'),
        upload_to='ui/banner/',
        blank=True,
        null=True,
        help_text=_('Main hero banner background photo')
    )
    stat_number = models.CharField(
        _('stat number'),
        max_length=50,
        default='200+',
        help_text=_('Metric number (e.g. 100+, 200+)')
    )
    stat_label = models.CharField(
        _('stat label'),
        max_length=150,
        default='Rejuvenated Guests • Classical Ayurvedic Care',
        help_text=_('Label text below the stat number')
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('hero banner')
        verbose_name_plural = _('hero banners')
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"
