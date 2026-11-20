"""
Aaramam Ayurveda Sanctuary — Email Dispatcher Engine.
Handles automatic dual-email notifications upon incoming inquiries:
1. Client Acknowledgment Email: Warm confirmation sent to the client (if email provided).
2. Company Notification Email: Real-time lead alert sent to the sanctuary team (aaramcare@gmail.com).

Asynchronously dispatched via background threads to ensure zero API latency.
"""
import logging
import threading
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _build_inquiry_context(inquiry):
    """
    Normalizes context fields across ServiceInquiry and AdmissionInquiry models.
    """
    if inquiry is None:
        return {}

    now = timezone.localtime(getattr(inquiry, 'created_at', None) or timezone.now())
    submitted_at_str = now.strftime('%B %d, %Y at %I:%M %p')

    inquiry_id = getattr(inquiry, 'id', 'new')

    # Detect model type
    is_admission = hasattr(inquiry, 'program')

    if is_admission:
        inquiry_type_display = "Inpatient Admission & Doctor Consultation"
        package_or_program_name = (
            inquiry.get_program_display()
            if hasattr(inquiry, 'get_program_display')
            else getattr(inquiry, 'program', 'Ayurvedic Treatment')
        )
        accommodation = (
            inquiry.get_bystander_accommodation_display()
            if hasattr(inquiry, 'get_bystander_accommodation_display')
            else getattr(inquiry, 'bystander_accommodation', '')
        )
        message_or_requirements = getattr(inquiry, 'requirements_or_due_date', '')
        admin_path = f"/admin/Contact/admissioninquiry/{inquiry_id}/change/"
    else:
        inquiry_type_display = "Package & Treatment Inquiry"
        service = getattr(inquiry, 'service', None)
        package_or_program_name = service.title if service else "General Sanctuary Package"
        accommodation = ""
        message_or_requirements = getattr(inquiry, 'message', '')
        admin_path = f"/admin/Services/serviceinquiry/{inquiry_id}/change/"

    whatsapp_url = (
        inquiry.get_whatsapp_url()
        if hasattr(inquiry, 'get_whatsapp_url')
        else f"https://wa.me/{getattr(inquiry, 'phone_number', '')}"
    )

    admin_base_url = getattr(settings, 'ADMIN_BASE_URL', 'http://127.0.0.1:8000')
    admin_url = f"{admin_base_url.rstrip('/')}{admin_path}"

    return {
        'inquiry_id': getattr(inquiry, 'id', 'new'),
        'inquiry_type_display': inquiry_type_display,
        'name': getattr(inquiry, 'name', 'Guest'),
        'email': getattr(inquiry, 'email', None),
        'phone_number': getattr(inquiry, 'phone_number', ''),
        'package_or_program_name': package_or_program_name,
        'accommodation': accommodation,
        'message_or_requirements': message_or_requirements,
        'submitted_at': submitted_at_str,
        'whatsapp_url': whatsapp_url,
        'admin_url': admin_url,
        'current_year': datetime.now().year,
    }


def _send_emails_worker(inquiry):
    """
    Worker function executed in a background thread to send both client and company emails.
    """
    try:
        ctx = _build_inquiry_context(inquiry)
        if not ctx:
            return
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'aaramcare@gmail.com')
        company_email = getattr(settings, 'COMPANY_NOTIFICATION_EMAIL', 'aaramcare@gmail.com')
        client_email = ctx.get('email')

        # ----------------------------------------------------------------------
        # 1. SEND CLIENT ACKNOWLEDGMENT EMAIL (If client provided an email)
        # ----------------------------------------------------------------------
        if client_email and '@' in client_email:
            try:
                client_subject = f"Inquiry Received: {ctx['package_or_program_name']} – Aaramam Ayurveda Sanctuary"
                html_client = render_to_string('emails/client_inquiry_acknowledgment.html', ctx)
                text_client = strip_tags(html_client)

                msg_client = EmailMultiAlternatives(
                    subject=client_subject,
                    body=text_client,
                    from_email=from_email,
                    to=[client_email.strip()],
                )
                msg_client.attach_alternative(html_client, "text/html")
                msg_client.send(fail_silently=False)
                logger.info(f"Client acknowledgment email sent to {client_email} for inquiry #{ctx['inquiry_id']}")
                print(f"[EMAIL SUCCESS] Client acknowledgment sent to {client_email}")
            except Exception as e:
                logger.warning(f"Failed to send client acknowledgment email to {client_email}: {e}")
                print(f"[EMAIL WARNING] Could not send client acknowledgment to {client_email}: {e}")

        # ----------------------------------------------------------------------
        # 2. SEND COMPANY NOTIFICATION EMAIL (Always sent to sanctuary desk)
        # ----------------------------------------------------------------------
        try:
            company_subject = f"🔔 New Website Lead: {ctx['package_or_program_name']} – {ctx['name']}"
            html_company = render_to_string('emails/company_inquiry_notification.html', ctx)
            text_company = strip_tags(html_company)

            headers = {}
            if client_email and '@' in client_email:
                headers['Reply-To'] = client_email.strip()

            msg_company = EmailMultiAlternatives(
                subject=company_subject,
                body=text_company,
                from_email=from_email,
                to=[company_email.strip()],
                headers=headers,
            )
            msg_company.attach_alternative(html_company, "text/html")
            msg_company.send(fail_silently=False)
            logger.info(f"Company notification email sent to {company_email} for inquiry #{ctx['inquiry_id']}")
            print(f"[EMAIL SUCCESS] Company notification sent to {company_email}")
        except Exception as e:
            logger.warning(f"Failed to send company notification email to {company_email}: {e}")
            print(f"[EMAIL WARNING] Could not send company notification to {company_email}: {e}")

    except Exception as e:
        logger.exception(f"Unhandled error in _send_emails_worker: {e}")
        print(f"[EMAIL ERROR] Unhandled exception in email worker: {e}")


def dispatch_inquiry_emails(inquiry):
    """
    Public entry point: Spawns an asynchronous background thread to send inquiry emails.
    Returns immediately without blocking the API response.
    """
    thread = threading.Thread(
        target=_send_emails_worker,
        args=(inquiry,),
        daemon=True,
        name=f"email-sender-inquiry-{getattr(inquiry, 'id', 'new')}"
    )
    thread.start()
    return thread
