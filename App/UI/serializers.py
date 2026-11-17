from rest_framework import serializers
from .models import HeroBanner


class HeroBannerSerializer(serializers.ModelSerializer):
    """
    Serializer for the simplified Hero Banner:
    - title, description, image, image_url, stat_number, stat_label, is_active
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = HeroBanner
        fields = (
            'id',
            'title',
            'description',
            'image',
            'image_url',
            'stat_number',
            'stat_label',
            'is_active',
            'created_at',
            'updated_at',
        )

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
