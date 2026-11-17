from rest_framework import serializers

from .models import AdmissionInquiry, SanctuaryContactInfo


class SanctuaryContactInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for sanctuary contact cards, doctor helpline, hours, and center details.
    """
    class Meta:
        model = SanctuaryContactInfo
        fields = (
            'id',
            'center_name',
            'tagline',
            'hero_description',
            'address_line1',
            'address_line2',
            'pincode',
            'helpline_phone',
            'whatsapp_number',
            'email',
            'opening_hours',
            'nursing_hours',
            'visiting_center_title',
            'visiting_center_location',
            'visiting_center_description',
            'google_maps_url',
            'facebook_url',
            'instagram_url',
            'youtube_url',
            'twitter_url',
            'linkedin_url',
            'pinterest_url',
            'updated_at',
        )


class AdmissionInquirySerializer(serializers.ModelSerializer):
    """
    Serializer for handling "Send an Admission or Therapy Inquiry" submissions.
    Generates an immediate WhatsApp redirect link with pre-filled message text.
    """
    program_display = serializers.CharField(source='get_program_display', read_only=True)
    bystander_accommodation_display = serializers.CharField(source='get_bystander_accommodation_display', read_only=True)
    whatsapp_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AdmissionInquiry
        fields = (
            'id',
            'name',
            'phone_number',
            'program',
            'program_display',
            'bystander_accommodation',
            'bystander_accommodation_display',
            'requirements_or_due_date',
            'status',
            'whatsapp_url',
            'created_at',
        )
        read_only_fields = ('id', 'status', 'whatsapp_url', 'created_at')

    def get_whatsapp_url(self, obj):
        return obj.get_whatsapp_url()

    def validate_name(self, value):
        stripped = value.strip()
        if len(stripped) < 2:
            raise serializers.ValidationError('Please provide your full name.')
        return stripped

    def validate_phone_number(self, value):
        stripped = value.strip()
        if len(stripped) < 7:
            raise serializers.ValidationError('Please provide a valid phone or WhatsApp number.')
        return stripped
