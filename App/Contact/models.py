import re
import urllib.parse
from django.db import models
from django.utils.translation import gettext_lazy as _


class SanctuaryContactInfo(models.Model):
    """
    Sanctuary location, doctor helpline, hours, and center details.
    """
    center_name = models.CharField(_('center name'), max_length=150, default='Aaramam Prasavaraksha Centre')
    tagline = models.CharField(_('tagline / header'), max_length=200, default='Connect with Our Sanctuary Doctors')
    hero_description = models.TextField(
        _('hero description'),
        default=(
            'Whether planning your postnatal stay, booking a restorative therapy, or seeking holistic health '
            'guidance, our medical directors and compassionate team at Feroke, Kozhikode are here for you.'
        )
    )

    # Address
    address_line1 = models.CharField(_('address line 1'), max_length=200, default='Near Govt Taluk Hospital (Chantha)')
    address_line2 = models.CharField(_('address line 2'), max_length=200, default='Feroke, Kozhikode, Keralam')
    pincode = models.CharField(_('pincode'), max_length=20, default='673631')

    # Phone & WhatsApp
    helpline_phone = models.CharField(_('consultation helpline'), max_length=50, default='+91 70346 41282')
    whatsapp_number = models.CharField(
        _('official WhatsApp number'),
        max_length=50,
        default='+91 70346 41282',
        help_text=_('Number receiving WhatsApp consultation messages')
    )
    email = models.EmailField(_('official email'), default='aaramcare@gmail.com')

    # Working Hours
    opening_hours = models.CharField(_('sanctuary hours'), max_length=100, default='Monday - Sunday: 8:00 AM - 8:00 PM')
    nursing_hours = models.CharField(_('nursing support note'), max_length=100, default='24/7 In-House Postnatal Nursing')

    # Visiting Centre Panel
    visiting_center_title = models.CharField(_('visiting title'), max_length=150, default='Visiting Feroke Centre')
    visiting_center_location = models.CharField(_('visiting center location'), max_length=100, default='Feroke, Kozhikode')
    visiting_center_description = models.TextField(
        _('visiting center description'),
        default=(
            'Conveniently situated near Govt Taluk Hospital (Chantha), Feroke, Kozhikode, Keralam 673631.\n'
            'Our centre provides dedicated postnatal mother & baby recovery, traditional Ayurvedic therapies, and personalised assistance.'
        )
    )
    google_maps_url = models.URLField(
        _('Google Maps link'),
        default='https://maps.google.com/?q=Govt+Taluk+Hospital+Feroke+Kozhikode+673631',
        help_text=_('Link to open location in Google Maps')
    )

    # Social Media Links
    facebook_url = models.URLField(_('Facebook URL'), blank=True, default='https://facebook.com/aaramamayurveda')
    instagram_url = models.URLField(_('Instagram URL'), blank=True, default='https://instagram.com/aaramamayurveda')
    youtube_url = models.URLField(_('YouTube URL'), blank=True, default='https://youtube.com/@aaramamayurveda')
    twitter_url = models.URLField(_('X (Twitter) URL'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    pinterest_url = models.URLField(_('Pinterest URL'), blank=True)

    updated_at = models.DateTimeField(_('last updated'), auto_now=True)

    class Meta:
        verbose_name = _('sanctuary contact info')
        verbose_name_plural = _('sanctuary contact info')

    def __str__(self):
        return f"{self.center_name} ({self.helpline_phone})"

    @property
    def whatsapp_digits(self):
        """Clean numerical string suitable for wa.me links."""
        digits = re.sub(r'\D', '', self.whatsapp_number)
        return digits or '917034641282'


class AdmissionInquiry(models.Model):
    """
    Submissions from "Send an Admission or Therapy Inquiry" form.
    Connects directly with the senior doctor desk via official WhatsApp while recording the lead in DB.
    """
    PROGRAM_CHOICES = (
        ('postnatal', _('Ayurvedic Postnatal Care')),
        ('shirodhara', _('Shirodhara & Stress Relief')),
        ('panchakarma', _('Panchakarma & Detox Therapy')),
        ('kizhi', _('Herbal Kizhi Pain Management')),
        ('doctor_consultation', _('Doctor Consultation')),
        ('general', _('General Sanctuary Inquiry')),
    )

    BYSTANDER_CHOICES = (
        ('1_bystander', _('1 Bystander Included (Mother + Baby + 1)')),
        ('2_bystanders', _('2 Bystanders (Family Suite)')),
        ('no_bystander', _('No Bystander (Mother & Baby Only)')),
        ('day_care', _('Day Care Only (No Stay)')),
    )

    STATUS_CHOICES = (
        ('new', _('New')),
        ('contacted', _('Contacted')),
        ('scheduled', _('Consultation Scheduled')),
        ('admitted', _('Admitted')),
        ('closed', _('Closed')),
    )

    name = models.CharField(_('your name'), max_length=150)
    phone_number = models.CharField(_('phone / WhatsApp number'), max_length=30)
    email = models.EmailField(
        _('email address'),
        blank=True,
        null=True,
        help_text=_('Email address for receiving confirmation and doctor consultation notes')
    )
    program = models.CharField(_('program / treatment'), max_length=100, choices=PROGRAM_CHOICES, default='postnatal')
    bystander_accommodation = models.CharField(
        _('bystander accommodation'),
        max_length=100,
        choices=BYSTANDER_CHOICES,
        default='1_bystander'
    )
    requirements_or_due_date = models.TextField(
        _('specific requirements or due date'),
        blank=True,
        help_text=_('Expected delivery date, chronic pains, dietary preferences, or questions...')
    )
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(_('internal doctor notes'), blank=True)
    created_at = models.DateTimeField(_('submitted at'), auto_now_add=True)

    class Meta:
        verbose_name = _('admission / therapy inquiry')
        verbose_name_plural = _('admission / therapy inquiries')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_program_display()} ({self.phone_number})"

    def get_whatsapp_url(self):
        """
        Builds a pre-populated WhatsApp click-to-chat URL.
        """
        contact_info = SanctuaryContactInfo.objects.first()
        target_number = contact_info.whatsapp_digits if contact_info else '917034641282'

        message_lines = [
            "Namaskaram Aaramam Sanctuary Doctor Desk,",
            "",
            f"*New Admission / Therapy Inquiry:*",
            f"• *Name:* {self.name}",
            f"• *Phone / WhatsApp:* {self.phone_number}",
            f"• *Program / Treatment:* {self.get_program_display()}",
            f"• *Bystander Option:* {self.get_bystander_accommodation_display()}",
        ]
        if self.requirements_or_due_date:
            message_lines.append(f"• *Requirements / Due Date:* {self.requirements_or_due_date}")

        message_lines.extend([
            "",
            "Please guide me with the admission procedure and doctor consultation.",
        ])

        encoded_text = urllib.parse.quote("\n".join(message_lines))
        return f"https://wa.me/{target_number}?text={encoded_text}"
