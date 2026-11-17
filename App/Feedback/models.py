from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class FeedbackStat(models.Model):
    """
    Key satisfaction metrics shown below the hero banner, e.g.:
    - 5.0 / 5.0 (OVERALL GUEST SATISFACTION - Based on 750+ sanctuary stays)
    - 99.4% (DOCTOR ATTENTIVENESS - Round-the-clock medical care)
    - 98.8% (THERAPEUTIC RESULTS - Postpartum recovery & pain relief)
    - 100% (SANCTUARY CLEANLINESS & AMBIENCE - Hygienic & warm living quarters)
    """
    title = models.CharField(_('metric title'), max_length=150)
    value = models.CharField(_('display score / percentage'), max_length=50, help_text=_('e.g. 5.0 / 5.0, 99.4%, 100%'))
    subtext = models.CharField(_('subtext description'), max_length=255, help_text=_('e.g. Based on 750+ sanctuary stays'))
    stars = models.PositiveSmallIntegerField(
        _('star count'),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Number of stars to display (1-5)')
    )
    order = models.PositiveIntegerField(_('order'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('satisfaction metric')
        verbose_name_plural = _('satisfaction metrics')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.value})"


class FeedbackCategory(models.Model):
    """
    Story filter pills under hero:
    e.g. "750+ Verified Mothers & Guests", "Postnatal Recovery Stories", "Doctor Attentiveness", "Private & Warm In-Stay"
    """
    name = models.CharField(_('category / tag name'), max_length=120, unique=True)
    slug = models.SlugField(_('slug'), max_length=140, unique=True, blank=True)
    order = models.PositiveIntegerField(_('order'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)

    class Meta:
        verbose_name = _('feedback category')
        verbose_name_plural = _('feedback categories')
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    """
    Guest reflections / reviews in "Loved by Wellness Seekers Worldwide".
    e.g.:
    - Dr. Claire Vance (Abhyanga Herbal Body Therapy)
    - Marcus K. (Shirodhara Medicated Oil Stream)
    - Elena Rostova (Herbal Kizhi & Panchakarma Detox)
    """
    category = models.ForeignKey(
        FeedbackCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonials',
        verbose_name=_('category'),
    )
    author_name = models.CharField(_('author name'), max_length=150)
    author_title = models.CharField(
        _('author title / designation / location'),
        max_length=200,
        blank=True,
        help_text=_('e.g. Integrative Medicine & Holistic Physician or Verified Sanctuary Guest • London, UK')
    )
    avatar = models.ImageField(
        _('author avatar / photo'),
        upload_to='feedbacks/avatars/',
        null=True,
        blank=True,
    )
    rating = models.PositiveSmallIntegerField(
        _('rating (stars)'),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    is_verified_guest = models.BooleanField(
        _('is verified guest'),
        default=True,
        help_text=_('Displays the green "VERIFIED GUEST" badge')
    )
    treatment_tag = models.CharField(
        _('treatment / therapy tag'),
        max_length=150,
        help_text=_('e.g. Abhyanga Herbal Body Therapy, Shirodhara Medicated Oil Stream, Herbal Kizhi & Panchakarma Detox')
    )
    quote = models.TextField(_('review / testimonial text'))

    is_featured = models.BooleanField(_('is featured'), default=True)
    is_active = models.BooleanField(_('is active'), default=True)
    order = models.PositiveIntegerField(_('order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('guest testimonial')
        verbose_name_plural = _('guest testimonials')
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.author_name} - {self.treatment_tag}"


class SanctuaryStory(models.Model):
    """
    Sanctuary Reels & Living Healing Stories from Instagram feed.
    Supports filtering by: All Stories, Reels, Photos.
    """
    MEDIA_TYPE_CHOICES = (
        ('story', _('Story')),
        ('reel', _('Reel')),
        ('photo', _('Photo')),
    )

    media_type = models.CharField(
        _('media type'),
        max_length=20,
        choices=MEDIA_TYPE_CHOICES,
        default='story',
    )
    account_handle = models.CharField(
        _('account handle'),
        max_length=100,
        default='@aaramamayurveda',
        help_text=_('e.g. @aaramamayurveda or @dr.reshma_ayurveda')
    )
    badge_tag = models.CharField(
        _('badge tag'),
        max_length=50,
        blank=True,
        help_text=_('e.g. SANCTUARY LIFE, DOCTOR INSIGHT')
    )
    title = models.CharField(
        _('story title'),
        max_length=200,
        help_text=_('e.g. Morning Uruli Decoctions & Nilavilakku, Ayurvedic Cosmetology & Postpartum Radiance')
    )
    caption = models.TextField(_('caption description'))
    location_or_audio = models.CharField(
        _('location or audio tag'),
        max_length=150,
        blank=True,
        help_text=_('e.g. Temple Bells of Kerala, Vital Prana Rhythm')
    )
    image = models.ImageField(
        _('cover image / thumbnail'),
        upload_to='feedbacks/stories/',
        null=True,
        blank=True,
    )
    video_url = models.URLField(
        _('video URL'),
        blank=True,
        help_text=_('Link to video or reel stream')
    )
    instagram_post_url = models.URLField(
        _('Instagram post link'),
        blank=True,
        help_text=_('Direct link to open in Instagram')
    )
    likes_count = models.PositiveIntegerField(_('likes count'), default=0)
    comments_count = models.PositiveIntegerField(_('comments count'), default=0)
    time_ago_text = models.CharField(
        _('time ago text'),
        max_length=50,
        default='1w ago',
        help_text=_('e.g. 7d ago, 1w ago')
    )

    is_active = models.BooleanField(_('is active'), default=True)
    order = models.PositiveIntegerField(_('order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('sanctuary story / reel')
        verbose_name_plural = _('sanctuary stories & reels')
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.account_handle})"


class GuestFeedbackSubmission(models.Model):
    """
    Submissions from guests submitting their own feedback online.
    Requires admin approval (`is_approved`) before displaying publicly.
    """
    name = models.CharField(_('guest name'), max_length=150)
    email = models.EmailField(_('email address'), blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    treatment_taken = models.CharField(_('treatment / package experienced'), max_length=150, blank=True)
    rating = models.PositiveSmallIntegerField(
        _('rating'),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    feedback = models.TextField(_('detailed feedback / review'))
    is_approved = models.BooleanField(_('approved for display'), default=False)
    created_at = models.DateTimeField(_('submitted at'), auto_now_add=True)

    class Meta:
        verbose_name = _('guest feedback submission')
        verbose_name_plural = _('guest feedback submissions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating}★ ({'Approved' if self.is_approved else 'Pending'})"
