import urllib.parse
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class ServiceCategory(models.Model):
    """
    Category or duration filter group (e.g., Postnatal Care, 28 Days Nurture, 21 Days Wellness, 14 Days Recovery).
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, blank=True)
    description = models.TextField(
        _('description / subtitle'),
        blank=True,
        help_text=_('Overview text or intro description for this section/category')
    )
    is_active = models.BooleanField(_('is active'), default=True)
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('service category')
        verbose_name_plural = _('service categories')
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    """
    Service package model representing packages such as:
    - Ayurvedic Wellness Therapies / Extended Shared Nurture Postnatal (28 Days)
    - Value Shared Wellness Postnatal (21 Days)
    - Affordable Shared Recovery Postnatal (14 Days)
    """
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
        verbose_name=_('category'),
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=220, unique=True, blank=True)
    subtitle = models.CharField(
        _('subtitle / tagline'),
        max_length=255,
        blank=True,
        help_text=_('e.g. Value 28 Days of Sustained Care & Privacy')
    )
    doctor_guidance = models.CharField(
        _('doctor guidance line'),
        max_length=200,
        blank=True,
        default='Guided by Experienced Ayurvedic Doctors',
        help_text=_('Displayed directly beneath title in the detailed modal')
    )

    # Badges displayed on package card & modal
    badge_tag = models.CharField(
        _('badge tag'),
        max_length=50,
        blank=True,
        help_text=_('e.g. AYURVEDIC POSTNATAL or SIGNATURE CARE')
    )
    duration_tag = models.CharField(
        _('duration tag'),
        max_length=50,
        blank=True,
        help_text=_('e.g. 28 Days Care, 21 Days Care, 14 Days Care')
    )
    image_overlay_badge = models.CharField(
        _('image overlay badge'),
        max_length=100,
        blank=True,
        default='Doctor-Led Wellness',
        help_text=_('Pill shown over the bottom-right of the cover image in modal')
    )

    # Media
    image = models.ImageField(
        _('card image'),
        upload_to='services/',
        null=True,
        blank=True,
        help_text=_('Cover image for the package card and modal')
    )

    # Rating and reviews
    rating = models.DecimalField(
        _('rating'),
        max_digits=3,
        decimal_places=1,
        default=5.0,
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('5.0'))],
        help_text=_('Rating out of 5 (e.g. 5.0, 4.9)')
    )
    review_count = models.PositiveIntegerField(
        _('review count'),
        default=0,
        help_text=_('Number of reviews / verified stays (e.g. 345, 450)')
    )

    # Descriptions
    short_description = models.TextField(
        _('short description'),
        help_text=_('Summary description displayed on the package card')
    )
    detailed_description = models.TextField(
        _('detailed description'),
        blank=True,
        help_text=_('Full overview text shown on the detailed modal')
    )
    recommended_for = models.TextField(
        _('recommended for'),
        blank=True,
        default='Mothers & wellness seekers seeking balanced recovery and inner calmness',
        help_text=_('Recommendation text shown near the WhatsApp CTA')
    )

    # Heritage Banner
    heritage_title = models.CharField(
        _('heritage banner title'),
        max_length=150,
        blank=True,
        default='30+ Years Generational Vaidya Heritage'
    )
    heritage_location = models.CharField(
        _('heritage banner location'),
        max_length=200,
        blank=True,
        default='Aaramam Centre • Near Govt Taluk Hospital, Feroke'
    )

    # Location & Facility
    location = models.CharField(
        _('location'),
        max_length=255,
        default='Aaramam Sanctuary • Near Govt Taluk Hospital, Feroke, Kozhikode',
        help_text=_('Center or facility location')
    )

    # Optional price
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Package price if available')
    )

    # Visibility & Display Order
    is_active = models.BooleanField(_('is active'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    order = models.PositiveIntegerField(_('display order'), default=0)

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('service package')
        verbose_name_plural = _('service packages')
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_whatsapp_url(self):
        """
        Builds a direct click-to-chat WhatsApp link for "ENQUIRE VIA WHATSAPP" in the modal.
        """
        target_number = '917034641282'
        message = (
            f"Namaskaram Aaramam Sanctuary Doctor Desk,\n\n"
            f"I would like to inquire about the package:\n"
            f"*{self.title}*\n"
            f"• Category: {self.category.name if self.category else 'Ayurvedic Treatment'}\n"
            f"• Location: {self.location}\n\n"
            f"Please share admission dates, doctor consultation availability, and package pricing."
        )
        encoded = urllib.parse.quote(message)
        return f"https://wa.me/{target_number}?text={encoded}"

    def get_primary_image(self):
        """Returns the primary image from the main field or from the gallery."""
        if self.image:
            return self.image
        primary = self.images.filter(is_primary=True).first() or self.images.first()
        return primary.image if primary else None


class ServiceImage(models.Model):
    """
    Multiple gallery / showcase images for a Service package.
    Allows displaying a carousel, photo gallery, or multiple views in the service card and modal.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('service package'),
    )
    image = models.ImageField(
        _('image'),
        upload_to='services/gallery/',
        help_text=_('Upload package or facility gallery photo')
    )
    caption = models.CharField(
        _('caption / title'),
        max_length=150,
        blank=True,
        help_text=_('Optional photo description or title (e.g. Suite View, Therapy Room)')
    )
    alt_text = models.CharField(
        _('alt text'),
        max_length=150,
        blank=True,
        help_text=_('Accessibility description for screen readers')
    )
    is_primary = models.BooleanField(
        _('is primary / cover'),
        default=False,
        help_text=_('Check if this should be featured as the main photo')
    )
    order = models.PositiveIntegerField(_('display order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('service image')
        verbose_name_plural = _('service images')
        ordering = ['order', 'id']

    def __str__(self):
        caption_str = f" - {self.caption}" if self.caption else ""
        return f"{self.service.title} (Image #{self.id or 'new'}{caption_str})"


class ServiceTherapy(models.Model):
    """
    Therapies and formulations shown under "THERAPEUTIC CARE & FORMULATIONS":
    e.g.
    - Shirodhara Oil Stream
    - Herbal Kizhi Poultices
    - Physician Assessment
    - Tridosha Balancing
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='therapies',
        verbose_name=_('service'),
    )
    name = models.CharField(_('therapy / formulation name'), max_length=120)
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('therapeutic formulation')
        verbose_name_plural = _('therapeutic formulations')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.service.title} - {self.name}"


SANCTUARY_ICON_CHOICES = (
    (_('Medical & Healthcare'), (
        ('health_and_safety', '🛡️ Doctor Supervised / Health & Safety (health_and_safety)'),
        ('stethoscope', '🩺 Doctor-Led Care / Stethoscope (stethoscope)'),
        ('medical_services', '🏥 Clinical & Medical Services (medical_services)'),
        ('healing', '🩹 Healing & Recovery (healing)'),
        ('medication', '🌿 Ayurvedic Medicines & Herbals (medication)'),
        ('monitor_heart', '💓 Vital Health Monitoring (monitor_heart)'),
        ('emergency', '🚨 24/7 Medical & Emergency Support (emergency)'),
        ('vaccines', '💉 Medical Treatments (vaccines)'),
    )),
    (_('Mother, Baby & Postnatal Nurture'), (
        ('child_care', '👶 Mother & Baby Postnatal Care (child_care)'),
        ('baby_changing_station', '🍼 Infant Care & Bath Station (baby_changing_station)'),
        ('pregnant_woman', '🤰 Maternity & Prenatal Wellness (pregnant_woman)'),
        ('family_restroom', '👨‍👩‍👧 Family & Bystander Stay (family_restroom)'),
        ('favorite', '❤️ Loving Mother Care & Compassion (favorite)'),
    )),
    (_('Ayurvedic Therapies, Spa & Body'), (
        ('spa', '🌸 Ayurvedic Spa & Rejuvenation (spa)'),
        ('water_drop', '💧 Herbal Oils & Shirodhara Stream (water_drop)'),
        ('hot_tub', '🛁 Herbal Bath & Steam / Vethukuzhi (hot_tub)'),
        ('clean_hands', '👐 Abhyanga Therapeutic Massage (clean_hands)'),
        ('self_improvement', '🧘 Meditation, Yoga & Mindful Rest (self_improvement)'),
        ('local_florist', '🌺 Natural Botanicals & Herbal Kizhi (local_florist)'),
        ('fitness_center', '💪 Physical Therapy & Rehabilitation (fitness_center)'),
    )),
    (_('Accommodation, Rooms & Comfort'), (
        ('bed', '🛏️ Private AC Suite / Bed (bed)'),
        ('hotel', '🏨 Inpatient Stay / Bystander Room (hotel)'),
        ('king_bed', '👑 Deluxe Suite / Premium Room (king_bed)'),
        ('bathtub', '🚿 Attached Hot Bath / Herbal Water (bathtub)'),
        ('shower', '🚿 Attached Shower / Hot Water (shower)'),
        ('ac_unit', '❄️ Air Conditioned Suite (ac_unit)'),
        ('room_service', '🛎️ 24/7 Nursing & Room Service (room_service)'),
        ('home', '🏡 Homely Sanctuary Atmosphere (home)'),
        ('wifi', '📶 Complimentary High-Speed Wi-Fi (wifi)'),
        ('local_parking', '🚗 Dedicated Guest Parking (local_parking)'),
        ('security', '🔒 Safe & Protected Sanctuary (security)'),
    )),
    (_('Diet, Food & Nourishment'), (
        ('restaurant', '🍲 Postpartum Diet / Pathya Ahara (restaurant)'),
        ('restaurant_menu', '📜 Prescribed Ayurvedic Diet Menu (restaurant_menu)'),
        ('local_dining', '🥗 Fresh Organic Balanced Meals (local_dining)'),
        ('soup_kitchen', '🥣 Herbal Soups & Oushadha Kanji (soup_kitchen)'),
        ('coffee', '☕ Herbal Decoctions & Warm Teas (coffee)'),
    )),
    (_('Trust, Heritage & Standards'), (
        ('verified', '✅ Verified & Certified Care (verified)'),
        ('shield', '🛡️ Safe & Protected Environment (shield)'),
        ('award_star', '⭐ Generational Vaidya Heritage (award_star)'),
        ('star', '🌟 Premium 5-Star Standards (star)'),
        ('schedule', '⏰ 24/7 Round-the-Clock Observation (schedule)'),
        ('eco', '🍃 100% Pure Natural Herbals (eco)'),
        ('nature_people', '🌳 Tranquil Natural Green Sanctuary (nature_people)'),
    )),
)


class ServiceAmenity(models.Model):
    """
    Left-hand 2x2 grid in detailed modal:
    - Doctor Supervised (24/7 BAMS Observation)
    - Postpartum Diet (Fresh Vata-Balancing Meals)
    - Private AC Suite (Bystander Stay Included)
    - Attached Hot Bath (Herbal Water Facilities)
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='amenities',
        verbose_name=_('service'),
    )
    title = models.CharField(_('title'), max_length=100)
    subtext = models.CharField(_('subtext'), max_length=150)
    icon = models.CharField(
        _('icon key'),
        max_length=60,
        choices=SANCTUARY_ICON_CHOICES,
        default='verified',
        help_text=_('Select an icon from the list')
    )
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('key highlight / amenity')
        verbose_name_plural = _('key highlights & amenities')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.service.title} - {self.title}"


class ServiceCarePillar(models.Model):
    """
    Right-hand 2x2 grid in detailed modal:
    - Doctor-Led Care (Daily BAMS physician observation)
    - Pathya Ahara (Warm Vata postpartum diet)
    - Mother & Baby (Gentle massage & Vethu bath)
    - Bystander Stay (Family stay included)
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='care_pillars',
        verbose_name=_('service'),
    )
    title = models.CharField(_('title'), max_length=100)
    subtext = models.CharField(_('subtext'), max_length=150)
    icon = models.CharField(
        _('icon key'),
        max_length=60,
        choices=SANCTUARY_ICON_CHOICES,
        default='spa',
        help_text=_('Select an icon from the list')
    )
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('care pillar')
        verbose_name_plural = _('care pillars')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.service.title} - {self.title}"


class ServiceInclusion(models.Model):
    """
    Checklist items listed under "WHAT'S INCLUDED IN THIS SANCTUARY PACKAGE:":
    - Traditional Kerala Ayurvedic therapies & Shirodhara
    - Maternal wellness, relaxation & balanced recovery
    - Personalised care guided by senior Ayurvedic doctors
    - Herbal Kizhi and classical rejuvenating protocols
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='inclusions',
        verbose_name=_('service'),
    )
    text = models.CharField(_('inclusion text'), max_length=255)
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        verbose_name = _('package inclusion')
        verbose_name_plural = _('package inclusions')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.service.title} - {self.text[:40]}"


class ServiceInquiry(models.Model):
    """
    Inquiry generated when a user clicks the "Enquire Now" button.
    """
    STATUS_CHOICES = (
        ('new', _('New')),
        ('contacted', _('Contacted')),
        ('converted', _('Converted')),
        ('closed', _('Closed')),
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
        verbose_name=_('service package'),
    )
    name = models.CharField(_('full name'), max_length=150)
    email = models.EmailField(_('email address'), blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=20)
    message = models.TextField(_('message / notes'), blank=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('service inquiry')
        verbose_name_plural = _('service inquiries')
        ordering = ['-created_at']

    def __str__(self):
        service_title = self.service.title if self.service else "General"
        return f"{self.name} - {service_title} ({self.phone_number})"
