from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdmissionInquiryViewSet, SanctuaryContactInfoView

router = DefaultRouter()
router.register(r'inquiries', AdmissionInquiryViewSet, basename='admission-inquiry')

urlpatterns = [
    path('info/', SanctuaryContactInfoView.as_view(), name='contact-info'),
    path('', include(router.urls)),
]
