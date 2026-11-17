from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Service, ServiceCategory, ServiceInquiry
from .serializers import (
    ServiceCategorySerializer,
    ServiceDetailSerializer,
    ServiceInquirySerializer,
    ServiceListSerializer,
)


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Allow read-only requests to anyone, write requests to staff only.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for service categories and filter tabs (e.g. 28 Days Nurture, 21 Days Wellness).
    """
    queryset = ServiceCategory.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user and self.request.user.is_staff:
            return ServiceCategory.objects.all().order_by('order', 'name')
        return queryset


class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for service packages.
    Supports filtering by category, duration tag, badge tag, and search query.
    """
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Service.objects.prefetch_related(
            'images', 'inclusions', 'therapies', 'amenities', 'care_pillars'
        ).select_related('category')
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)

        # Filter by category slug or id
        category = self.request.query_params.get('category')
        if category:
            if category.isdigit():
                queryset = queryset.filter(category_id=int(category))
            else:
                queryset = queryset.filter(category__slug=category)

        # Filter by duration tag (e.g. '28 Days Care')
        duration = self.request.query_params.get('duration')
        if duration:
            queryset = queryset.filter(duration_tag__icontains=duration)

        # Filter by badge tag (e.g. 'SIGNATURE CARE')
        badge = self.request.query_params.get('badge')
        if badge:
            queryset = queryset.filter(badge_tag__icontains=badge)

        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured is not None:
            queryset = queryset.filter(is_featured=featured.lower() in ['true', '1'])

        # Search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(subtitle__icontains=search) |
                Q(short_description__icontains=search) |
                Q(location__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get('ordering', 'order')
        if ordering in ['order', '-order', 'rating', '-rating', 'review_count', '-review_count', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('order', '-created_at')

        return queryset

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return ServiceDetailSerializer
        return ServiceListSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def enquire(self, request, slug=None):
        """
        Directly submit an inquiry for this specific service package.
        """
        service = self.get_object()
        data = request.data.copy()
        data['service'] = service.id

        serializer = ServiceInquirySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': f'Inquiry for "{service.title}" submitted successfully!',
                    'data': serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceInquiryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for handling "Enquire Now" submissions.
    Public users can submit (POST); staff can list and manage them.
    """
    queryset = ServiceInquiry.objects.select_related('service').order_by('-created_at')
    serializer_class = ServiceInquirySerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
