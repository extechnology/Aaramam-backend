from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FeedbackCategoryViewSet,
    FeedbackStatViewSet,
    GuestFeedbackSubmissionViewSet,
    SanctuaryStoryViewSet,
    TestimonialViewSet,
)

router = DefaultRouter()
router.register(r'stats', FeedbackStatViewSet, basename='feedback-stat')
router.register(r'categories', FeedbackCategoryViewSet, basename='feedback-category')
router.register(r'testimonials', TestimonialViewSet, basename='feedback-testimonial')
router.register(r'stories', SanctuaryStoryViewSet, basename='sanctuary-story')
router.register(r'submissions', GuestFeedbackSubmissionViewSet, basename='guest-feedback-submission')

urlpatterns = [
    path('', include(router.urls)),
]
