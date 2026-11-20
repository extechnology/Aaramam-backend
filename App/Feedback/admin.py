from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.decorators import action, display

from App.common.export import GUEST_FEEDBACK_COLUMNS, export_to_csv, export_to_excel
from .models import (
    FeedbackCategory,
    FeedbackStat,
    GuestFeedbackSubmission,
    SanctuaryStory,
    Testimonial,
)


@admin.register(FeedbackStat)
class FeedbackStatAdmin(ModelAdmin):
    """
    Unfold admin configuration for Satisfaction Metrics.
    """
    list_display = ('title', 'value', 'subtext', 'display_stars', 'display_active', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'value', 'subtext')
    ordering = ('order', 'id')

    @display(description=_('Stars'))
    def display_stars(self, instance: FeedbackStat):
        return '★' * instance.stars

    @display(description=_('Active'), boolean=True)
    def display_active(self, instance: FeedbackStat):
        return instance.is_active


@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(ModelAdmin):
    """
    Unfold admin configuration for feedback filter tags.
    """
    list_display = ('name', 'slug', 'display_active', 'order')
    list_editable = ('order',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    @display(description=_('Active'), boolean=True)
    def display_active(self, instance: FeedbackCategory):
        return instance.is_active


@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    """
    Unfold admin configuration for guest testimonials.
    """
    list_display = (
        'display_author',
        'display_treatment',
        'category',
        'display_stars',
        'display_verified',
        'display_active',
        'display_featured',
        'order',
    )
    list_filter = (
        ('category', RelatedDropdownFilter),
        'is_verified_guest',
        'is_active',
        'is_featured',
    )
    list_editable = ('order',)
    search_fields = ('author_name', 'author_title', 'treatment_tag', 'quote')
    ordering = ('order', '-created_at')

    fieldsets = (
        (
            _('Author Information'),
            {
                'fields': ('author_name', 'author_title', 'avatar', 'category'),
            },
        ),
        (
            _('Testimonial Content'),
            {
                'fields': ('treatment_tag', 'quote', 'rating', 'is_verified_guest'),
            },
        ),
        (
            _('Visibility & Sorting'),
            {
                'fields': ('is_active', 'is_featured', 'order'),
            },
        ),
    )

    @display(description=_('Author'), header=True)
    def display_author(self, instance: Testimonial):
        return [instance.author_name, instance.author_title or _('Guest')]

    @display(description=_('Treatment / Therapy'), label=True)
    def display_treatment(self, instance: Testimonial):
        return instance.treatment_tag

    @display(description=_('Rating'))
    def display_stars(self, instance: Testimonial):
        return '★' * instance.rating

    @display(description=_('Verified'), boolean=True)
    def display_verified(self, instance: Testimonial):
        return instance.is_verified_guest

    @display(description=_('Active'), boolean=True)
    def display_active(self, instance: Testimonial):
        return instance.is_active

    @display(description=_('Featured'), boolean=True)
    def display_featured(self, instance: Testimonial):
        return instance.is_featured


@admin.register(SanctuaryStory)
class SanctuaryStoryAdmin(ModelAdmin):
    """
    Unfold admin configuration for Sanctuary Reels & Living Healing Stories.
    """
    list_display = (
        'display_story',
        'display_media_type',
        'account_handle',
        'badge_tag',
        'display_engagement',
        'time_ago_text',
        'display_active',
        'order',
    )
    list_filter = (
        ('media_type', ChoicesDropdownFilter),
        'is_active',
    )
    list_editable = ('order',)
    search_fields = ('title', 'caption', 'account_handle', 'location_or_audio')
    ordering = ('order', '-created_at')

    fieldsets = (
        (
            _('Story Details'),
            {
                'fields': ('title', 'caption', 'media_type', 'badge_tag'),
            },
        ),
        (
            _('Social & Account Info'),
            {
                'fields': ('account_handle', 'location_or_audio', 'time_ago_text'),
            },
        ),
        (
            _('Media & External Links'),
            {
                'fields': ('image', 'video_url', 'instagram_post_url'),
            },
        ),
        (
            _('Engagement Metrics'),
            {
                'fields': ('likes_count', 'comments_count'),
            },
        ),
        (
            _('Visibility & Order'),
            {
                'fields': ('is_active', 'order'),
            },
        ),
    )

    @display(description=_('Story / Post'), header=True)
    def display_story(self, instance: SanctuaryStory):
        return [instance.title, instance.caption[:60] + ('...' if len(instance.caption) > 60 else '')]

    @display(
        description=_('Media Type'),
        label={
            'story': 'primary',
            'reel': 'info',
            'photo': 'success',
        },
    )
    def display_media_type(self, instance: SanctuaryStory):
        return instance.media_type

    @display(description=_('Engagement'))
    def display_engagement(self, instance: SanctuaryStory):
        return f"♥ {instance.likes_count:,} | 💬 {instance.comments_count:,}"

    @display(description=_('Active'), boolean=True)
    def display_active(self, instance: SanctuaryStory):
        return instance.is_active


@admin.register(GuestFeedbackSubmission)
class GuestFeedbackSubmissionAdmin(ModelAdmin):
    """
    Unfold admin configuration for guest submissions with quick approval action.
    """
    list_display = (
        'display_guest',
        'phone_number',
        'treatment_taken',
        'display_stars',
        'display_status',
        'created_at',
    )
    list_filter = (
        'is_approved',
        'created_at',
    )
    search_fields = ('name', 'email', 'phone_number', 'feedback', 'treatment_taken')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions_list = ['export_all_excel', 'export_all_csv']
    actions = ['approve_submissions', 'export_selected_excel', 'export_selected_csv']

    @action(description=_('Export to Excel (.xlsx)'), icon='file_download')
    def export_all_excel(self, request):
        qs = self.get_queryset(request)
        return export_to_excel(qs, 'Aaramam_Guest_Submissions', 'Guest Submissions', GUEST_FEEDBACK_COLUMNS)

    @action(description=_('Export to CSV (.csv)'), icon='download')
    def export_all_csv(self, request):
        qs = self.get_queryset(request)
        return export_to_csv(qs, 'Aaramam_Guest_Submissions', GUEST_FEEDBACK_COLUMNS)

    @action(description=_('Export selected to Excel (.xlsx)'))
    def export_selected_excel(self, request, queryset):
        return export_to_excel(queryset, 'Aaramam_Selected_Guest_Submissions', 'Selected Submissions', GUEST_FEEDBACK_COLUMNS)

    @action(description=_('Export selected to CSV (.csv)'))
    def export_selected_csv(self, request, queryset):
        return export_to_csv(queryset, 'Aaramam_Selected_Guest_Submissions', GUEST_FEEDBACK_COLUMNS)

    @display(description=_('Guest'), header=True)
    def display_guest(self, instance: GuestFeedbackSubmission):
        return [instance.name, instance.email or instance.phone_number or _('No contact')]

    @display(description=_('Rating'))
    def display_stars(self, instance: GuestFeedbackSubmission):
        return '★' * instance.rating

    @display(
        description=_('Approval Status'),
        label={
            'Approved': 'success',
            'Pending': 'warning',
        },
    )
    def display_status(self, instance: GuestFeedbackSubmission):
        return 'Approved' if instance.is_approved else 'Pending'

    @action(description=_('Approve selected feedback and publish as Testimonials'))
    def approve_submissions(self, request, queryset):
        count = 0
        for submission in queryset:
            if not submission.is_approved:
                submission.is_approved = True
                submission.save()
                Testimonial.objects.create(
                    author_name=submission.name,
                    author_title=f"Guest • {submission.treatment_taken}" if submission.treatment_taken else "Sanctuary Guest",
                    rating=submission.rating,
                    treatment_tag=submission.treatment_taken or "Ayurvedic Treatment",
                    quote=submission.feedback,
                    is_verified_guest=True,
                    is_active=True,
                )
                count += 1
        self.message_user(request, f"{count} submission(s) approved and published as testimonials.")
