from rest_framework import serializers

from .models import (
    FeedbackCategory,
    FeedbackStat,
    GuestFeedbackSubmission,
    SanctuaryStory,
    Testimonial,
)


class FeedbackStatSerializer(serializers.ModelSerializer):
    """
    Serializer for key satisfaction metrics cards.
    """
    class Meta:
        model = FeedbackStat
        fields = ('id', 'title', 'value', 'subtext', 'stars', 'order')


class FeedbackCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for feedback category / story filter tabs.
    """
    testimonials_count = serializers.IntegerField(source='testimonials.count', read_only=True)

    class Meta:
        model = FeedbackCategory
        fields = ('id', 'name', 'slug', 'order', 'testimonials_count')


class TestimonialSerializer(serializers.ModelSerializer):
    """
    Serializer for guest testimonials / reviews.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = Testimonial
        fields = (
            'id',
            'author_name',
            'author_title',
            'avatar',
            'rating',
            'is_verified_guest',
            'treatment_tag',
            'quote',
            'category',
            'category_name',
            'category_slug',
            'is_featured',
            'order',
            'created_at',
        )


class SanctuaryStorySerializer(serializers.ModelSerializer):
    """
    Serializer for Sanctuary Reels & Living Healing Stories from Instagram.
    """
    class Meta:
        model = SanctuaryStory
        fields = (
            'id',
            'media_type',
            'account_handle',
            'badge_tag',
            'title',
            'caption',
            'location_or_audio',
            'image',
            'video_url',
            'instagram_post_url',
            'likes_count',
            'comments_count',
            'time_ago_text',
            'order',
            'created_at',
        )


class GuestFeedbackSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for incoming guest feedback submissions.
    """
    class Meta:
        model = GuestFeedbackSubmission
        fields = (
            'id',
            'name',
            'email',
            'phone_number',
            'treatment_taken',
            'rating',
            'feedback',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Please enter a valid name.')
        return value.strip()

    def validate_feedback(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Please provide at least a brief feedback note.')
        return value.strip()
