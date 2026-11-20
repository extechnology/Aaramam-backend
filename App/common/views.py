from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from App.Contact.models import AdmissionInquiry
from App.Feedback.models import GuestFeedbackSubmission
from App.Services.models import ServiceInquiry

from .export import (
    ADMISSION_INQUIRY_COLUMNS,
    GUEST_FEEDBACK_COLUMNS,
    SERVICE_INQUIRY_COLUMNS,
    export_to_csv,
    export_to_excel,
)


@staff_member_required
def export_service_inquiries_view(request: HttpRequest, format: str) -> HttpResponse:
    """
    Downloads all Service Inquiries as Excel or CSV.
    """
    if not request.user.has_perm('Services.view_serviceinquiry'):
        raise PermissionDenied

    qs = ServiceInquiry.objects.select_related('service', 'service__category').order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    filename = 'Aaramam_Package_Inquiries'
    sheet_title = 'Package Inquiries'

    if format.lower() == 'excel':
        return export_to_excel(qs, filename, sheet_title, SERVICE_INQUIRY_COLUMNS)
    return export_to_csv(qs, filename, SERVICE_INQUIRY_COLUMNS)


@staff_member_required
def export_admission_inquiries_view(request: HttpRequest, format: str) -> HttpResponse:
    """
    Downloads all Admission & Doctor Consultation Inquiries as Excel or CSV.
    """
    if not request.user.has_perm('Contact.view_admissioninquiry'):
        raise PermissionDenied

    qs = AdmissionInquiry.objects.order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    filename = 'Aaramam_Admission_Inquiries'
    sheet_title = 'Admission Inquiries'

    if format.lower() == 'excel':
        return export_to_excel(qs, filename, sheet_title, ADMISSION_INQUIRY_COLUMNS)
    return export_to_csv(qs, filename, ADMISSION_INQUIRY_COLUMNS)


@staff_member_required
def export_guest_feedback_view(request: HttpRequest, format: str) -> HttpResponse:
    """
    Downloads all Guest Feedback Submissions as Excel or CSV.
    """
    if not request.user.has_perm('Feedback.view_guestfeedbacksubmission'):
        raise PermissionDenied

    qs = GuestFeedbackSubmission.objects.order_by('-created_at')
    approved_filter = request.GET.get('approved')
    if approved_filter is not None:
        qs = qs.filter(is_approved=approved_filter.lower() in ['true', '1'])

    filename = 'Aaramam_Guest_Feedback'
    sheet_title = 'Guest Submissions'

    if format.lower() == 'excel':
        return export_to_excel(qs, filename, sheet_title, GUEST_FEEDBACK_COLUMNS)
    return export_to_csv(qs, filename, GUEST_FEEDBACK_COLUMNS)
