from datetime import timedelta
from django.db.models import Avg, Count, Q
from django.utils import timezone

from App.Contact.models import AdmissionInquiry
from App.Feedback.models import GuestFeedbackSubmission, Testimonial
from App.Services.models import Service, ServiceCategory, ServiceInquiry


def dashboard_callback(request, context):
    """
    Enriches the Django Unfold index context with real-time analytics,
    KPI metrics, conversion funnels, and recent inquiry feeds.
    """
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    # 1. Package Inquiries Metrics
    total_service_inq = ServiceInquiry.objects.count()
    new_service_inq = ServiceInquiry.objects.filter(status='new').count()
    contacted_service_inq = ServiceInquiry.objects.filter(status='contacted').count()
    converted_service_inq = ServiceInquiry.objects.filter(status='converted').count()
    closed_service_inq = ServiceInquiry.objects.filter(status='closed').count()
    recent_7d_service_inq = ServiceInquiry.objects.filter(created_at__gte=seven_days_ago).count()

    conv_rate_service = round((converted_service_inq / total_service_inq * 100), 1) if total_service_inq > 0 else 0.0

    # 2. Admission & Doctor Consultation Inquiries
    total_adm_inq = AdmissionInquiry.objects.count()
    new_adm_inq = AdmissionInquiry.objects.filter(status='new').count()
    contacted_adm_inq = AdmissionInquiry.objects.filter(status='contacted').count()
    scheduled_adm_inq = AdmissionInquiry.objects.filter(status='scheduled').count()
    admitted_adm_inq = AdmissionInquiry.objects.filter(status='admitted').count()
    closed_adm_inq = AdmissionInquiry.objects.filter(status='closed').count()
    recent_7d_adm_inq = AdmissionInquiry.objects.filter(created_at__gte=seven_days_ago).count()

    conv_rate_adm = round(((admitted_adm_inq + scheduled_adm_inq) / total_adm_inq * 100), 1) if total_adm_inq > 0 else 0.0

    # 3. Guest Feedback Submissions
    total_feedback = GuestFeedbackSubmission.objects.count()
    approved_feedback = GuestFeedbackSubmission.objects.filter(is_approved=True).count()
    pending_feedback = GuestFeedbackSubmission.objects.filter(is_approved=False).count()
    avg_rating_val = GuestFeedbackSubmission.objects.aggregate(avg=Avg('rating'))['avg'] or 5.0
    avg_rating = round(float(avg_rating_val), 1)

    # Rating distribution (1 to 5 stars)
    rating_counts = {}
    for star in [5, 4, 3, 2, 1]:
        cnt = GuestFeedbackSubmission.objects.filter(rating=star).count()
        pct = round((cnt / total_feedback * 100), 1) if total_feedback > 0 else (100 if star == 5 else 0)
        rating_counts[star] = {'count': cnt, 'percent': pct}

    # 4. Services & Sanctuary Offerings
    total_services = Service.objects.filter(is_active=True).count()
    total_categories = ServiceCategory.objects.filter(is_active=True).count()
    total_testimonials = Testimonial.objects.filter(is_active=True).count()

    # 5. Last 7 Days Inquiry Velocity (Chart points)
    trend_labels = []
    trend_service_data = []
    trend_adm_data = []
    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        day_label = day_date.strftime('%a %d')
        trend_labels.append(day_label)
        s_count = ServiceInquiry.objects.filter(created_at__date=day_date).count()
        a_count = AdmissionInquiry.objects.filter(created_at__date=day_date).count()
        trend_service_data.append(s_count)
        trend_adm_data.append(a_count)

    # 6. Recent Feeds (Last 5 records)
    recent_service_inquiries = ServiceInquiry.objects.select_related('service', 'service__category').order_by('-created_at')[:5]
    recent_admission_inquiries = AdmissionInquiry.objects.order_by('-created_at')[:5]
    recent_feedback = GuestFeedbackSubmission.objects.order_by('-created_at')[:5]

    # Package Status Percentages for Funnel Bars
    def get_pct(val, total):
        return round((val / total * 100), 1) if total > 0 else 0

    analytics = {
        'total_leads_all': total_service_inq + total_adm_inq,
        'new_leads_pending': new_service_inq + new_adm_inq,
        'service_inquiries': {
            'total': total_service_inq,
            'new': new_service_inq,
            'contacted': contacted_service_inq,
            'converted': converted_service_inq,
            'closed': closed_service_inq,
            'conversion_rate': conv_rate_service,
            'recent_7d': recent_7d_service_inq,
            'new_pct': get_pct(new_service_inq, total_service_inq),
            'contacted_pct': get_pct(contacted_service_inq, total_service_inq),
            'converted_pct': get_pct(converted_service_inq, total_service_inq),
            'closed_pct': get_pct(closed_service_inq, total_service_inq),
        },
        'admission_inquiries': {
            'total': total_adm_inq,
            'new': new_adm_inq,
            'contacted': contacted_adm_inq,
            'scheduled': scheduled_adm_inq,
            'admitted': admitted_adm_inq,
            'closed': closed_adm_inq,
            'conversion_rate': conv_rate_adm,
            'recent_7d': recent_7d_adm_inq,
            'new_pct': get_pct(new_adm_inq, total_adm_inq),
            'contacted_pct': get_pct(contacted_adm_inq, total_adm_inq),
            'scheduled_pct': get_pct(scheduled_adm_inq, total_adm_inq),
            'admitted_pct': get_pct(admitted_adm_inq, total_adm_inq),
            'closed_pct': get_pct(closed_adm_inq, total_adm_inq),
        },
        'feedback': {
            'total': total_feedback,
            'approved': approved_feedback,
            'pending': pending_feedback,
            'avg_rating': avg_rating,
            'ratings': rating_counts,
        },
        'catalog': {
            'total_services': total_services,
            'total_categories': total_categories,
            'total_testimonials': total_testimonials,
        },
        'trend': {
            'labels': trend_labels,
            'service_data': trend_service_data,
            'adm_data': trend_adm_data,
            'max_val': max(max(trend_service_data, default=1), max(trend_adm_data, default=1), 4),
        },
        'recent_service_inquiries': recent_service_inquiries,
        'recent_admission_inquiries': recent_admission_inquiries,
        'recent_feedback': recent_feedback,
    }

    context['analytics'] = analytics
    return context
