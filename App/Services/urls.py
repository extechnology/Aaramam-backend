from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ServiceCategoryViewSet, ServiceInquiryViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r'categories', ServiceCategoryViewSet, basename='service-category')
router.register(r'packages', ServiceViewSet, basename='service-package')
router.register(r'inquiries', ServiceInquiryViewSet, basename='service-inquiry')

urlpatterns = [
    path('', include(router.urls)),
]
