from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AdmissionInquiry, SanctuaryContactInfo
from .serializers import AdmissionInquirySerializer, SanctuaryContactInfoSerializer


class SanctuaryContactInfoView(APIView):
    """
    Public endpoint providing sanctuary contact details, doctor helpline, hours, and map links.
    GET /api/contact/info/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        info = SanctuaryContactInfo.objects.first()
        if not info:
            info = SanctuaryContactInfo.objects.create()
        serializer = SanctuaryContactInfoSerializer(info)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdmissionInquiryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for handling Admission / Therapy inquiries.
    - POST: Publicly accessible by visitors clicking "CONNECT WITH DOCTOR ON WHATSAPP"
    - GET / PATCH / DELETE: Restricted to clinic staff / doctors
    """
    queryset = AdmissionInquiry.objects.all().order_by('-created_at')
    serializer_class = AdmissionInquirySerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by program
        program = self.request.query_params.get('program')
        if program:
            queryset = queryset.filter(program=program)

        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by bystander accommodation
        bystander = self.request.query_params.get('bystander')
        if bystander:
            queryset = queryset.filter(bystander_accommodation=bystander)

        # Search by name, phone, or requirements
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(requirements_or_due_date__icontains=search) |
                Q(notes__icontains=search)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inquiry = serializer.save()

        whatsapp_url = inquiry.get_whatsapp_url()

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Your admission inquiry has been recorded. Redirecting to official WhatsApp...',
                'whatsapp_url': whatsapp_url,
                'data': serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def whatsapp(self, request, pk=None):
        """
        Direct action for clinic staff to open chat with the guest on WhatsApp.
        """
        inquiry = self.get_object()
        return Response({'whatsapp_url': inquiry.get_whatsapp_url()})
