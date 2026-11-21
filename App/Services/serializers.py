from rest_framework import serializers

from .models import (
    Service,
    ServiceAmenity,
    ServiceCarePillar,
    ServiceCategory,
    ServiceImage,
    ServiceInclusion,
    ServiceInquiry,
    ServiceTherapy,
)


class ServiceCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for service categories/filter tabs.
    """
    services_count = serializers.IntegerField(source='services.count', read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ('id', 'name', 'slug', 'description', 'order', 'services_count')


class ServiceTherapySerializer(serializers.ModelSerializer):
    """
    Serializer for formulations & therapies (e.g. Shirodhara Oil Stream, Herbal Kizhi Poultices).
    """
    class Meta:
        model = ServiceTherapy
        fields = ('id', 'name', 'order')


class ServiceAmenitySerializer(serializers.ModelSerializer):
    """
    Serializer for key highlights / amenities (left grid in detailed modal).
    """
    icon_display = serializers.CharField(source='get_icon_display', read_only=True)

    class Meta:
        model = ServiceAmenity
        fields = ('id', 'title', 'subtext', 'icon', 'icon_display', 'order')


class ServiceCarePillarSerializer(serializers.ModelSerializer):
    """
    Serializer for care pillars (right grid in detailed modal).
    """
    icon_display = serializers.CharField(source='get_icon_display', read_only=True)

    class Meta:
        model = ServiceCarePillar
        fields = ('id', 'title', 'subtext', 'icon', 'icon_display', 'order')


class ServiceInclusionSerializer(serializers.ModelSerializer):
    """
    Serializer for package inclusions (checklist items in modal).
    """
    class Meta:
        model = ServiceInclusion
        fields = ('id', 'text', 'order')


class ServiceImageSerializer(serializers.ModelSerializer):
    """
    Serializer for multiple gallery photos for a service package.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceImage
        fields = ('id', 'image', 'image_url', 'caption', 'alt_text', 'is_primary', 'order')

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ServiceListSerializer(serializers.ModelSerializer):
    """
    Serializer optimized for displaying package cards in the services section.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    images = ServiceImageSerializer(many=True, read_only=True)
    gallery = serializers.SerializerMethodField()
    inclusions = serializers.SerializerMethodField()
    whatsapp_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            'id',
            'title',
            'slug',
            'subtitle',
            'doctor_guidance',
            'category',
            'category_name',
            'category_slug',
            'badge_tag',
            'duration_tag',
            'image_overlay_badge',
            'image',
            'images',
            'gallery',
            'rating',
            'review_count',
            'short_description',
            'inclusions',
            'location',
            'price',
            'is_featured',
            'order',
            'whatsapp_url',
        )

    def get_gallery(self, obj):
        request = self.context.get('request')
        urls = []
        if obj.image:
            urls.append(request.build_absolute_uri(obj.image.url) if request else obj.image.url)
        for img_obj in obj.images.all():
            if img_obj.image:
                url = request.build_absolute_uri(img_obj.image.url) if request else img_obj.image.url
                if url not in urls:
                    urls.append(url)
        return urls

    def get_inclusions(self, obj):
        return [inclusion.text for inclusion in obj.inclusions.all()]

    def get_whatsapp_url(self, obj):
        return obj.get_whatsapp_url()


class ServiceDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for the Services Detailed Modal ("View Package Details").
    Includes:
    - Left Column: Image, image overlay badge, formulations pills, 2x2 amenities grid, heritage banner.
    - Right Column: Title, doctor guidance, category badge, 2x2 care pillars, inclusions checklist, recommendation, WhatsApp CTA.
    """
    category = ServiceCategorySerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    inclusions = ServiceInclusionSerializer(many=True, read_only=True)
    inclusions_list = serializers.SerializerMethodField()
    therapies = ServiceTherapySerializer(many=True, read_only=True)
    therapies_list = serializers.SerializerMethodField()
    amenities = ServiceAmenitySerializer(many=True, read_only=True)
    care_pillars = ServiceCarePillarSerializer(many=True, read_only=True)
    images = ServiceImageSerializer(many=True, read_only=True)
    gallery = serializers.SerializerMethodField()
    whatsapp_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            'id',
            'title',
            'slug',
            'subtitle',
            'doctor_guidance',
            'category',
            'category_name',
            'badge_tag',
            'duration_tag',
            'image_overlay_badge',
            'image',
            'images',
            'gallery',
            'rating',
            'review_count',
            'short_description',
            'detailed_description',
            'recommended_for',
            'heritage_title',
            'heritage_location',
            'therapies',
            'therapies_list',
            'amenities',
            'care_pillars',
            'inclusions',
            'inclusions_list',
            'location',
            'price',
            'whatsapp_url',
            'is_active',
            'is_featured',
            'order',
            'created_at',
            'updated_at',
        )

    def get_gallery(self, obj):
        request = self.context.get('request')
        urls = []
        if obj.image:
            urls.append(request.build_absolute_uri(obj.image.url) if request else obj.image.url)
        for img_obj in obj.images.all():
            if img_obj.image:
                url = request.build_absolute_uri(img_obj.image.url) if request else img_obj.image.url
                if url not in urls:
                    urls.append(url)
        return urls

    def get_inclusions_list(self, obj):
        return [inc.text for inc in obj.inclusions.all()]

    def get_therapies_list(self, obj):
        return [th.name for th in obj.therapies.all()]

    def get_whatsapp_url(self, obj):
        return obj.get_whatsapp_url()


class ServiceInquirySerializer(serializers.ModelSerializer):
    """
    Serializer for handling "Enquire Now" requests.
    """
    service_title = serializers.CharField(source='service.title', read_only=True)

    class Meta:
        model = ServiceInquiry
        fields = (
            'id',
            'service',
            'service_title',
            'name',
            'email',
            'phone_number',
            'message',
            'status',
            'created_at',
        )
        read_only_fields = ('id', 'status', 'created_at')

    def validate_phone_number(self, value):
        stripped = str(value).strip()
        if len(stripped) < 7:
            raise serializers.ValidationError('Please provide a valid phone number.')
        return stripped
