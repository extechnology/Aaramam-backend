from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import HeroBanner
from .serializers import HeroBannerSerializer


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Allow read-only requests to anyone, write requests to staff only.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class HeroBannerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the Home Hero Banner.
    GET /api/ui/banner/
    GET /api/ui/banner/active/
    """
    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = HeroBannerSerializer

    def get_queryset(self):
        queryset = HeroBanner.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Returns the active hero banner object directly.
        If ?all=true is passed by an admin, returns the full array.
        """
        if request.query_params.get('all') == 'true' and request.user.is_staff:
            return super().list(request, *args, **kwargs)

        banner = self.get_queryset().filter(is_active=True).first() or self.get_queryset().first()
        if not banner:
            return Response(
                {'detail': 'No active hero banner configured.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(banner)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='active')
    def active(self, request):
        banner = self.get_queryset().filter(is_active=True).first() or self.get_queryset().first()
        if not banner:
            return Response(
                {'detail': 'No active hero banner configured.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(banner)
        return Response(serializer.data)
