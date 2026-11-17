from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HeroBannerViewSet

router = DefaultRouter()
router.register(r'banner', HeroBannerViewSet, basename='ui-banner')
router.register(r'hero', HeroBannerViewSet, basename='ui-hero')

urlpatterns = [
    path('', include(router.urls)),
]
