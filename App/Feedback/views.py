from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    FeedbackCategory,
    FeedbackStat,
    GuestFeedbackSubmission,
    SanctuaryStory,
    Testimonial,
)
from .serializers import (
    FeedbackCategorySerializer,
    FeedbackStatSerializer,
    GuestFeedbackSubmissionSerializer,
    SanctuaryStorySerializer,
    TestimonialSerializer,
)


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Allow read-only requests to public, full write requests to staff only.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class FeedbackStatViewSet(viewsets.ModelViewSet):
    """
    API endpoint for satisfaction metrics (5.0/5.0, 99.4%, etc.).
    """
    queryset = FeedbackStat.objects.filter(is_active=True).order_by('order', 'id')
    serializer_class = FeedbackStatSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return FeedbackStat.objects.all().order_by('order', 'id')
        return super().get_queryset()


class FeedbackCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for feedback filter categories (e.g. Postnatal Recovery Stories, Doctor Attentiveness).
    """
    queryset = FeedbackCategory.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = FeedbackCategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            return FeedbackCategory.objects.all().order_by('order', 'name')
        return super().get_queryset()


class TestimonialViewSet(viewsets.ModelViewSet):
    """
    API endpoint for guest testimonials in "Loved by Wellness Seekers Worldwide".
    Supports filtering by category, treatment, featured, and search.
    """
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        queryset = Testimonial.objects.select_related('category')
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)

        # Filter by category slug or ID
        category = self.request.query_params.get('category')
        if category:
            if category.isdigit():
                queryset = queryset.filter(category_id=int(category))
            else:
                queryset = queryset.filter(category__slug=category)

        # Filter by treatment name or tag
        treatment = self.request.query_params.get('treatment')
        if treatment:
            queryset = queryset.filter(treatment_tag__icontains=treatment)

        # Filter by verified guests
        verified = self.request.query_params.get('verified')
        if verified is not None:
            queryset = queryset.filter(is_verified_guest=verified.lower() in ['true', '1'])

        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured is not None:
            queryset = queryset.filter(is_featured=featured.lower() in ['true', '1'])

        # Search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(author_name__icontains=search) |
                Q(author_title__icontains=search) |
                Q(treatment_tag__icontains=search) |
                Q(quote__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get('ordering', 'order')
        if ordering in ['order', '-order', 'rating', '-rating', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('order', '-created_at')

        return queryset

    def get_serializer_class(self):
        return TestimonialSerializer


class SanctuaryStoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Sanctuary Reels & Living Healing Stories from Instagram.
    Supports filtering by media_type (story, reel, photo), badge, and search.
    """
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        queryset = SanctuaryStory.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)

        # Filter by media type: all, story, reel, photo
        media_type = self.request.query_params.get('media_type')
        if media_type and media_type.lower() != 'all':
            queryset = queryset.filter(media_type=media_type.lower())

        # Filter by badge tag (e.g. SANCTUARY LIFE, DOCTOR INSIGHT)
        badge = self.request.query_params.get('badge')
        if badge:
            queryset = queryset.filter(badge_tag__icontains=badge)

        # Search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(caption__icontains=search) |
                Q(location_or_audio__icontains=search) |
                Q(account_handle__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get('ordering', 'order')
        if ordering in ['order', '-order', 'likes_count', '-likes_count', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('order', '-created_at')

        return queryset

    def get_serializer_class(self):
        return SanctuaryStorySerializer


class GuestFeedbackSubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for guest feedback submissions.
    Public users can submit (POST); staff can list, inspect, and approve them.
    """
    queryset = GuestFeedbackSubmission.objects.all().order_by('-created_at')
    serializer_class = GuestFeedbackSubmissionSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """
        Action to approve and automatically convert guest submission into a live Testimonial.
        """
        submission = self.get_object()
        submission.is_approved = True
        submission.save()

        # Create published Testimonial
        testimonial = Testimonial.objects.create(
            author_name=submission.name,
            author_title=f"Guest • {submission.treatment_taken}" if submission.treatment_taken else "Sanctuary Guest",
            rating=submission.rating,
            treatment_tag=submission.treatment_taken or "Ayurvedic Treatment",
            quote=submission.feedback,
            is_verified_guest=True,
            is_active=True,
        )

        return Response(
            {
                'message': f'Feedback from {submission.name} approved and published as testimonial!',
                'testimonial_id': testimonial.id,
            },
            status=status.HTTP_200_OK,
        )
