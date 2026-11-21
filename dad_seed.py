"""
Aaramam Ayurveda Sanctuary — Production Database Seeder (dad_seed.py)
Transcribes EXACT live text contents from the official website screenshots:
  1. Home Hero Banner (Title, Description, 200+ stat)
  2. Sanctuary Contact Info (Helpline, WhatsApp, Feroke address, hours, maps, socials)
  3. Service Categories (Filter tabs: Postnatal Care, Therapies, Wellness, Skin Care, Durations)
  4. Core Service Packages & Detailed Modals (Postnatal Care, Postnatal Therapies, Wellness Therapies, Beauty & Skin Care)
     - Full subtitles, ratings, verified stay counts, doctor guidance, descriptions, recommendations
     - Therapeutic Formulations pills
     - Key Highlights & Amenities with icons
     - Care Pillars with icons
     - Inclusions checklists
  5. Satisfaction Metrics (Overall Satisfaction 5.0, Doctor Attentiveness 99.4%, Efficacy 98.8%, Award 100%)
  6. Feedback Categories (Filter tags)
  7. Guest Testimonials (Dr. Ananya Nambiar, Rahul K. Panicker, Sreedevi Warrier)
  8. Sanctuary Reels & Living Stories (Instagram Reels & Stories with handles, likes, comments, time-ago)

Safe for PostgreSQL, SQLite, and MySQL on production VPS servers.
Uses update_or_create to allow idempotent re-running without duplicate records.
"""

import os
import sys
from decimal import Decimal

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.db import transaction
from App.UI.models import HeroBanner
from App.Contact.models import SanctuaryContactInfo
from App.Feedback.models import (
    FeedbackCategory,
    FeedbackStat,
    SanctuaryStory,
    Testimonial,
)
from App.Services.models import (
    Service,
    ServiceAmenity,
    ServiceCarePillar,
    ServiceCategory,
    ServiceImage,
    ServiceInclusion,
    ServiceTherapy,
)


def seed_hero_banner():
    print("🌱 [1/6] Seeding Home Hero Banner...")
    banner, created = HeroBanner.objects.update_or_create(
        id=1,
        defaults={
            'title': 'Motherhood Begins with Love and Care.',
            'description': (
                'Providing Gentle Ayurvedic Care, Comfort And Nurturing Support '
                'For Every New Mother And Baby.'
            ),
            'stat_number': '200+',
            'stat_label': 'Rejuvenated Guests Classical Ayurvedic Care',
            'is_active': True,
        }
    )
    action = "Created" if created else "Updated"
    print(f"   ✓ {action} Hero Banner: '{banner.title}' ({banner.stat_number} {banner.stat_label})")


def seed_contact_info():
    print("\n🌱 [2/6] Seeding Sanctuary Contact Info...")
    contact, created = SanctuaryContactInfo.objects.update_or_create(
        id=1,
        defaults={
            'center_name': 'Aaramam Prasavaraksha Centre',
            'tagline': 'Connect with Our Sanctuary Doctors',
            'hero_description': (
                'Whether planning your postnatal stay, booking a restorative therapy, or seeking holistic '
                'health guidance, our medical directors and compassionate team at Feroke, Kozhikode are here for you.'
            ),
            'address_line1': 'Near Govt Taluk Hospital (Chantha)',
            'address_line2': 'Feroke, Kozhikode, Keralam',
            'pincode': '673631',
            'helpline_phone': '+91 70346 41282',
            'whatsapp_number': '+91 70346 41282',
            'email': 'aaramcare@gmail.com',
            'opening_hours': 'Monday - Sunday: 8:00 AM - 8:00 PM',
            'nursing_hours': '24/7 In-House Postnatal Nursing',
            'visiting_center_title': 'Visiting Feroke Centre',
            'visiting_center_location': 'Feroke, Kozhikode',
            'visiting_center_description': (
                'Conveniently situated near Govt Taluk Hospital (Chantha), Feroke, Kozhikode, Keralam 673631.\n'
                'Our centre provides dedicated postnatal mother & baby recovery, traditional Ayurvedic therapies, and personalised assistance.'
            ),
            'google_maps_url': 'https://maps.google.com/?q=Govt+Taluk+Hospital+Feroke+Kozhikode+673631',
            'facebook_url': 'https://facebook.com/aaramamayurveda',
            'instagram_url': 'https://instagram.com/aaramamayurveda',
            'youtube_url': 'https://youtube.com/@aaramamayurveda',
        }
    )
    action = "Created" if created else "Updated"
    print(f"   ✓ {action} Contact Info: {contact.center_name} ({contact.helpline_phone})")


def seed_categories():
    print("\n🌱 [3/6] Seeding Service Categories & Duration Filter Tabs...")
    categories_data = [
        {'name': 'Postnatal Care', 'slug': 'postnatal-care', 'order': 1, 'description': 'Dedicated maternal and newborn postpartum recovery.'},
        {'name': 'Therapies', 'slug': 'therapies', 'order': 2, 'description': 'Classical Kerala rejuvenating therapies and Shirodhara.'},
        {'name': 'Wellness', 'slug': 'wellness', 'order': 3, 'description': 'Holistic inner balance and vital health nourishment.'},
        {'name': 'Skin Care', 'slug': 'skin-care', 'order': 4, 'description': 'Natural herbal cosmetology and glow restoration.'},
        {'name': '28 Days Nurture', 'slug': '28-days-nurture', 'order': 5, 'description': 'Full classical 28-day postnatal care program.'},
        {'name': '21 Days Wellness', 'slug': '21-days-wellness', 'order': 6, 'description': '21-day restorative rejuvenation stay.'},
        {'name': '14 Days Recovery', 'slug': '14-days-recovery', 'order': 7, 'description': '14-day intensive postnatal strength revival.'},
    ]
    cat_map = {}
    for cat_dict in categories_data:
        cat, _ = ServiceCategory.objects.update_or_create(
            slug=cat_dict['slug'],
            defaults=cat_dict
        )
        cat_map[cat.slug] = cat
        print(f"   ✓ Category: '{cat.name}' (order={cat.order})")
    return cat_map


def seed_services_and_modals(cat_map):
    print("\n🌱 [4/6] Seeding Detailed Packages & Modals (Exact Screenshot Contents)...")

    # Shared default amenities across packages (as shown in modal screenshots)
    default_amenities = [
        {'title': 'Doctor Supervised', 'subtext': '24/7 BAMS Observation', 'icon': 'health_and_safety', 'order': 1},
        {'title': 'Postpartum Diet', 'subtext': 'Fresh Vata-Balancing Meals', 'icon': 'restaurant', 'order': 2},
        {'title': 'Private AC Suite', 'subtext': 'Bystander Stay Included', 'icon': 'bed', 'order': 3},
        {'title': 'Attached Hot Bath', 'subtext': 'Herbal Water Facilities', 'icon': 'bathtub', 'order': 4},
    ]

    # Shared default care pillars across packages (as shown in modal screenshots)
    default_care_pillars = [
        {'title': 'Doctor-Led Care', 'subtext': 'Daily BAMS physician observation', 'icon': 'stethoscope', 'order': 1},
        {'title': 'Pathya Ahara', 'subtext': 'Warm Vata postpartum diet', 'icon': 'restaurant_menu', 'order': 2},
        {'title': 'Mother & Baby', 'subtext': 'Gentle massage & Vethu bath', 'icon': 'child_care', 'order': 3},
        {'title': 'Bystander Stay', 'subtext': 'Family stay included', 'icon': 'hotel', 'order': 4},
    ]

    packages_data = [
        # ------------------------------------------------------------------
        # 1. Ayurvedic Postnatal Care (Modal Screenshot 1)
        # ------------------------------------------------------------------
        {
            'title': 'Ayurvedic Postnatal Care',
            'slug': 'ayurvedic-postnatal-care',
            'category': cat_map.get('postnatal-care'),
            'subtitle': 'Nurturing Mothers with Personalised Attention',
            'doctor_guidance': 'Guided by Experienced Ayurvedic Doctors',
            'badge_tag': 'AYURVEDIC POSTNATAL',
            'duration_tag': '28 Days Care',
            'image_overlay_badge': 'Personalised Care',
            'rating': Decimal('5.0'),
            'review_count': 480,
            'short_description': (
                'We provide traditional Ayurvedic postnatal care, nurturing mothers with '
                'personalised attention, comfort, strength restoration and holistic wellness after childbirth.'
            ),
            'detailed_description': (
                'We provide traditional Ayurvedic postnatal care, nurturing mothers with '
                'personalised attention, comfort, strength restoration and holistic wellness after childbirth.'
            ),
            'recommended_for': 'New mothers seeking strength restoration, comfort & holistic recovery',
            'heritage_title': '30+ Years Generational Vaidya Heritage',
            'heritage_location': 'Aaramam Centre • Near Govt Taluk Hospital, Feroke',
            'location': 'Aaramam Sanctuary • Near Govt Taluk Hospital, Feroke, Kozhikode',
            'order': 1,
            'is_featured': True,
            'is_active': True,
            'therapies': [
                'Daily Abhyanga Massage',
                'Herbal Baths & Vata Diet',
                'Lactation Guidance',
                'Private Mother-Baby Space',
            ],
            'amenities': default_amenities,
            'care_pillars': default_care_pillars,
            'inclusions': [
                'Personalised attention & continuous nursing care',
                'Comfort & strength restoration therapies',
                'Holistic maternal wellness after childbirth',
                'Near Govt Taluk Hospital (Chantha), Feroke, Kozhikode',
            ],
        },

        # ------------------------------------------------------------------
        # 2. Ayurvedic Postnatal Therapies (Modal Screenshot 2)
        # ------------------------------------------------------------------
        {
            'title': 'Ayurvedic Postnatal Therapies',
            'slug': 'ayurvedic-postnatal-therapies',
            'category': cat_map.get('therapies'),
            'subtitle': 'Restorative Massages & Personalised Care',
            'doctor_guidance': 'Guided by Experienced Ayurvedic Doctors',
            'badge_tag': 'AYURVEDIC POSTNATAL',
            'duration_tag': '21 Days Care',
            'image_overlay_badge': 'Restorative Therapies',
            'rating': Decimal('4.9'),
            'review_count': 395,
            'short_description': (
                'We provide traditional Ayurvedic postnatal therapies, massages and personalised care '
                'to restore mothers\' strength, comfort, relaxation and overall wellness.'
            ),
            'detailed_description': (
                'We provide traditional Ayurvedic postnatal therapies, massages and personalised care '
                'to restore mothers\' strength, comfort, relaxation and overall wellness.'
            ),
            'recommended_for': 'Postnatal mothers seeking strength revival, comfort and deep relaxation',
            'heritage_title': '30+ Years Generational Vaidya Heritage',
            'heritage_location': 'Aaramam Centre • Near Govt Taluk Hospital, Feroke',
            'location': 'Aaramam Sanctuary • Near Govt Taluk Hospital, Feroke, Kozhikode',
            'order': 2,
            'is_featured': True,
            'is_active': True,
            'therapies': [
                'Warm Medicated Oil Massage',
                'Pelvic Healing Herbs',
                'Deep Relaxation Rituals',
                'Doctor Supervision',
            ],
            'amenities': default_amenities,
            'care_pillars': default_care_pillars,
            'inclusions': [
                'Traditional Ayurvedic postnatal massages & therapies',
                'Restore mothers\' strength, comfort and relaxation',
                'Overall physical & emotional wellness support',
                'Customized herbal decoctions & warm oils',
            ],
        },

        # ------------------------------------------------------------------
        # 3. Ayurvedic Wellness Therapies (Modal Screenshot 3)
        # ------------------------------------------------------------------
        {
            'title': 'Ayurvedic Wellness Therapies',
            'slug': 'ayurvedic-wellness-therapies',
            'category': cat_map.get('wellness'),
            'subtitle': 'Guided by Experienced Ayurvedic Doctors',
            'doctor_guidance': 'Guided by Experienced Ayurvedic Doctors',
            'badge_tag': 'AYURVEDIC POSTNATAL',
            'duration_tag': '28 Days Care',
            'image_overlay_badge': 'Doctor-Led Wellness',
            'rating': Decimal('4.9'),
            'review_count': 345,
            'short_description': (
                'We offer traditional Kerala Ayurvedic therapies, promoting maternal wellness, '
                'relaxation and balanced recovery through personalised care guided by experienced Ayurvedic doctors.'
            ),
            'detailed_description': (
                'We offer traditional Kerala Ayurvedic therapies, promoting maternal wellness, '
                'relaxation and balanced recovery through personalised care guided by experienced Ayurvedic doctors.'
            ),
            'recommended_for': 'Mothers & wellness seekers seeking balanced recovery and inner calmness',
            'heritage_title': '30+ Years Generational Vaidya Heritage',
            'heritage_location': 'Aaramam Centre • Near Govt Taluk Hospital, Feroke',
            'location': 'Aaramam Sanctuary • Near Govt Taluk Hospital, Feroke, Kozhikode',
            'order': 3,
            'is_featured': True,
            'is_active': True,
            'therapies': [
                'Shirodhara Oil Stream',
                'Herbal Kizhi Poultices',
                'Physician Assessment',
                'Tridosha Balancing',
            ],
            'amenities': default_amenities,
            'care_pillars': default_care_pillars,
            'inclusions': [
                'Traditional Kerala Ayurvedic therapies & Shirodhara',
                'Maternal wellness, relaxation & balanced recovery',
                'Personalised care guided by senior Ayurvedic doctors',
                'Herbal Kizhi and classical rejuvenating protocols',
            ],
        },

        # ------------------------------------------------------------------
        # 4. Beauty & Skin Care (Modal Screenshot 4)
        # ------------------------------------------------------------------
        {
            'title': 'Beauty & Skin Care',
            'slug': 'beauty-skin-care',
            'category': cat_map.get('skin-care'),
            'subtitle': 'Restore Natural Radiance & Vitality',
            'doctor_guidance': 'Guided by Experienced Ayurvedic Doctors',
            'badge_tag': 'AYURVEDIC POSTNATAL',
            'duration_tag': '14 Days Care',
            'image_overlay_badge': 'Herbal Radiance',
            'rating': Decimal('5.0'),
            'review_count': 310,
            'short_description': (
                'We provide traditional Ayurvedic beauty and herbal skincare therapies, '
                'helping mothers restore natural radiance, relaxation and wellness after childbirth.'
            ),
            'detailed_description': (
                'We provide traditional Ayurvedic beauty and herbal skincare therapies, '
                'helping mothers restore natural radiance, relaxation and wellness after childbirth.'
            ),
            'recommended_for': 'New mothers seeking to restore skin radiance, tone and gentle glow',
            'heritage_title': '30+ Years Generational Vaidya Heritage',
            'heritage_location': 'Aaramam Centre • Near Govt Taluk Hospital, Feroke',
            'location': 'Aaramam Sanctuary • Near Govt Taluk Hospital, Feroke, Kozhikode',
            'order': 4,
            'is_featured': True,
            'is_active': True,
            'therapies': [
                'Wild Turmeric (Kasturi Manjal)',
                'Saffron (Kumkumadi)',
                'Herbal Face Lepam',
                'Nourishing Floral Extracts',
            ],
            'amenities': default_amenities,
            'care_pillars': default_care_pillars,
            'inclusions': [
                'Traditional Ayurvedic beauty and herbal skincare therapies',
                'Restores natural radiance, glow and hydration',
                'Gentle post-delivery skin rejuvenation protocols',
                'Pure wild-harvested botanicals & saffron elixirs',
            ],
        },

        # ------------------------------------------------------------------
        # 5. Extended Duration Program (28 Days Nurture)
        # ------------------------------------------------------------------
        {
            'title': 'Extended Shared Nurture Postnatal',
            'slug': 'extended-shared-nurture-postnatal',
            'category': cat_map.get('28-days-nurture'),
            'subtitle': 'Value 28 Days of Sustained Care & Privacy',
            'doctor_guidance': 'Guided by Experienced Ayurvedic Doctors',
            'badge_tag': '28 DAYS NURTURE',
            'duration_tag': '28 Days Care',
            'image_overlay_badge': 'Comprehensive Care',
            'rating': Decimal('4.9'),
            'review_count': 285,
            'short_description': (
                'Comprehensive 28-day inpatient postnatal stay covering complete herbal recovery, '
                'maternal nutrition, newborn care and full bystander accommodation.'
            ),
            'detailed_description': (
                'Comprehensive 28-day inpatient postnatal stay covering complete herbal recovery, '
                'maternal nutrition, newborn care and full bystander accommodation.'
            ),
            'recommended_for': 'Mothers seeking full postpartum recovery and peaceful sanctuary living',
            'heritage_title': '30+ Years Generational Vaidya Heritage',
            'heritage_location': 'Aaramam Centre • Near Govt Taluk Hospital, Feroke',
            'location': 'Aaramam Sanctuary • Near Govt Taluk Hospital, Feroke, Kozhikode',
            'order': 5,
            'is_featured': False,
            'is_active': True,
            'therapies': [
                'Daily Postpartum Abhyanga',
                'Medicated Vethu Herbal Baths',
                'Daily BAMS Doctor Rounds',
                'Postpartum Belly Binding',
            ],
            'amenities': default_amenities,
            'care_pillars': default_care_pillars,
            'inclusions': [
                'Complete 28-day mother and baby care protocol',
                'Private AC suite with attached herbal bath',
                'Bystander stay included with hot water facilities',
                'Custom Vata-balancing Pathya Ahara meals',
            ],
        },
    ]

    for pdata in packages_data:
        therapies = pdata.pop('therapies', [])
        amenities = pdata.pop('amenities', [])
        care_pillars = pdata.pop('care_pillars', [])
        inclusions = pdata.pop('inclusions', [])

        service, _ = Service.objects.update_or_create(
            slug=pdata['slug'],
            defaults=pdata
        )

        # Sync therapies
        service.therapies.all().delete()
        for idx, t_name in enumerate(therapies, 1):
            ServiceTherapy.objects.create(service=service, name=t_name, order=idx)

        # Sync amenities
        service.amenities.all().delete()
        for a_item in amenities:
            ServiceAmenity.objects.create(service=service, **a_item)

        # Sync care pillars
        service.care_pillars.all().delete()
        for cp_item in care_pillars:
            ServiceCarePillar.objects.create(service=service, **cp_item)

        # Sync inclusions
        service.inclusions.all().delete()
        for idx, inc_text in enumerate(inclusions, 1):
            ServiceInclusion.objects.create(service=service, text=inc_text, order=idx)

        print(f"   ✓ Seeded Package: '{service.title}' (Rating: {service.rating} ★, {service.review_count} stays)")


def seed_satisfaction_metrics():
    print("\n🌱 [5/6] Seeding Satisfaction Metric Cards (Exact Screenshot 4)...")
    stats_data = [
        {
            'title': 'OVERALL GUEST SATISFACTION',
            'value': '5.0/5.0',
            'subtext': 'Based on 1,200+ Verified Stays',
            'stars': 5,
            'order': 1,
            'is_active': True,
        },
        {
            'title': 'DOCTOR ATTENTIVENESS',
            'value': '99.4%',
            'subtext': 'Dedicated daily BAMS oversight',
            'stars': 5,
            'order': 2,
            'is_active': True,
        },
        {
            'title': 'THERAPEUTIC EFFICACY',
            'value': '98.8%',
            'subtext': 'Visible postpartum recovery',
            'stars': 5,
            'order': 3,
            'is_active': True,
        },
        {
            'title': 'POSTPARTUM CARE NOBLE AWARDED',
            'value': '100%',
            'subtext': 'Recommended by OBGYN Specialists',
            'stars': 5,
            'order': 4,
            'is_active': True,
        },
    ]
    for s_dict in stats_data:
        stat, _ = FeedbackStat.objects.update_or_create(
            title=s_dict['title'],
            defaults=s_dict
        )
        print(f"   ✓ Metric: '{stat.title}' -> {stat.value} ({stat.subtext})")


def seed_testimonials_and_stories():
    print("\n🌱 [6/6] Seeding Categories, Testimonials & Sanctuary Stories (Screenshot 4)...")

    # Filter categories
    feedback_cats_data = [
        {'name': 'All Sanctuary Reflections', 'slug': 'all-sanctuary-reflections', 'order': 1},
        {'name': 'Postnatal Recovery Stories', 'slug': 'postnatal-recovery-stories', 'order': 2},
        {'name': 'Doctor Consultations', 'slug': 'doctor-consultations', 'order': 3},
        {'name': 'Ayurvedic Therapies', 'slug': 'ayurvedic-therapies', 'order': 4},
    ]
    fb_map = {}
    for fc in feedback_cats_data:
        cat, _ = FeedbackCategory.objects.update_or_create(
            slug=fc['slug'],
            defaults={'name': fc['name'], 'order': fc['order'], 'is_active': True}
        )
        fb_map[cat.slug] = cat
        print(f"   ✓ Feedback Filter Tag: '{cat.name}'")

    # Exact Testimonials from Screenshot 4
    testimonials_data = [
        {
            'author_name': 'Dr. Ananya Nambiar',
            'author_title': 'Verified Resident Guest • 28 Days Postnatal Retreat',
            'category': fb_map.get('postnatal-recovery-stories'),
            'rating': 5,
            'is_verified_guest': True,
            'treatment_tag': '28 Days Postnatal Care',
            'quote': (
                'Experiencing the specialized Abhyanga and warm herbal baths with my newborn in such a '
                'serene sanctuary gave me profound relief from fatigue. The doctor\'s daily visits and '
                'warm postpartum meals made this journey unforgettable.'
            ),
            'is_featured': True,
            'is_active': True,
            'order': 1,
        },
        {
            'author_name': 'Rahul K. Panicker',
            'author_title': 'Wellness Traveler • 14 Days Rejuvenation',
            'category': fb_map.get('ayurvedic-therapies'),
            'rating': 5,
            'is_verified_guest': True,
            'treatment_tag': '14 Days Rejuvenation Therapy',
            'quote': (
                'After months of stress and desk fatigue, the classical Shirodhara and Kizhi treatments '
                'revived my energy completely. The tranquil Feroke riverfront setting and authentic Vaidya '
                'heritage make Aaramam truly world-class.'
            ),
            'is_featured': True,
            'is_active': True,
            'order': 2,
        },
        {
            'author_name': 'Sreedevi Warrier',
            'author_title': 'Postpartum Mother • Feroke Sanctuary, Kozhikode',
            'category': fb_map.get('postnatal-recovery-stories'),
            'rating': 5,
            'is_verified_guest': True,
            'treatment_tag': 'Postnatal Care & Recovery',
            'quote': (
                'The care and tradition at Aaramam gave me strength during my first month of motherhood. '
                'Having my mother as bystander in the spacious suite and eating fresh Pathya Ahara made '
                'recovery seamless and joyful.'
            ),
            'is_featured': True,
            'is_active': True,
            'order': 3,
        },
    ]

    for t_data in testimonials_data:
        testi, _ = Testimonial.objects.update_or_create(
            author_name=t_data['author_name'],
            defaults=t_data
        )
        print(f"   ✓ Testimonial: '{testi.author_name}' ({testi.treatment_tag})")

    # Exact 6 Sanctuary Reels & Stories from Screenshot 4
    stories_data = [
        {
            'title': 'Postnatal Recovery at Feroke, Kozhikode',
            'account_handle': '@aaramam_ayurveda',
            'media_type': 'reel',
            'badge_tag': 'POSTNATAL',
            'likes_count': 2400,
            'comments_count': 128,
            'time_ago_text': '2d ago',
            'location_or_audio': 'Feroke Sanctuary • Original Audio',
            'caption': 'Gentle mother & baby care in our serene inpatient suites near Govt Taluk Hospital, Feroke.',
            'order': 1,
            'is_active': True,
        },
        {
            'title': 'Dr. Jabeena on Postpartum Nutrition',
            'account_handle': '@dr.jabeena_ayurveda',
            'media_type': 'reel',
            'badge_tag': 'DOCTOR INSIGHT',
            'likes_count': 1900,
            'comments_count': 94,
            'time_ago_text': '4d ago',
            'location_or_audio': 'Doctor\'s Desk • Inpatient Insights',
            'caption': 'Why traditional Pathya Ahara and warm Vata-balancing soups are crucial in the first 28 days.',
            'order': 2,
            'is_active': True,
        },
        {
            'title': 'Morning Oushadha Decoctions & Kizhi Making',
            'account_handle': '@aaramam_ayurveda',
            'media_type': 'story',
            'badge_tag': 'PHOTO',
            'likes_count': 840,
            'comments_count': 42,
            'time_ago_text': '1w ago',
            'location_or_audio': 'Aaramam Pharmacy • Fresh Herbs',
            'caption': 'Handcrafting freshly tied herbal poultices and medicated oils for the morning therapies.',
            'order': 3,
            'is_active': True,
        },
        {
            'title': 'The Calming Art of Shirodhara',
            'account_handle': '@aaramam_ayurveda',
            'media_type': 'reel',
            'badge_tag': 'THERAPY',
            'likes_count': 3100,
            'comments_count': 215,
            'time_ago_text': '5d ago',
            'location_or_audio': 'Therapy Suite • Medicated Oils',
            'caption': 'A continuous warm stream of herbal oil to calm the central nervous system and soothe tension.',
            'order': 4,
            'is_active': True,
        },
        {
            'title': 'Ayurvedic Cosmetology & Postpartum Radiance',
            'account_handle': '@dr.jabeena_ayurveda',
            'media_type': 'reel',
            'badge_tag': 'DOCTOR INSIGHT',
            'likes_count': 1500,
            'comments_count': 87,
            'time_ago_text': '1w ago',
            'location_or_audio': 'Ayurvedic Beauty • Kasturi Manjal',
            'caption': 'Restore natural skin glow and elasticity after delivery using pure Kumkumadi and floral extracts.',
            'order': 5,
            'is_active': True,
        },
        {
            'title': 'Guest Stay: 28 Days of Transformation',
            'account_handle': '@aaramam_ayurveda',
            'media_type': 'reel',
            'badge_tag': 'POSTNATAL',
            'likes_count': 4200,
            'comments_count': 381,
            'time_ago_text': '3d ago',
            'location_or_audio': 'Resident Sanctuary • Mother & Baby',
            'caption': 'The step-by-step reflection of a mother recovering her energy, posture, and wellness.',
            'order': 6,
            'is_active': True,
        },
    ]

    for s_dict in stories_data:
        story, _ = SanctuaryStory.objects.update_or_create(
            title=s_dict['title'],
            defaults=s_dict
        )
        print(f"   ✓ Story [{story.media_type.upper()}]: '{story.title}' ({story.likes_count:,} likes)")


def main():
    print("=" * 70)
    print("  AARAMAM AYURVEDA SANCTUARY — PRODUCTION DATABASE SEEDER")
    print("  Populating exact contents from official live UI screenshots...")
    print("=" * 70)

    with transaction.atomic():
        seed_hero_banner()
        seed_contact_info()
        cat_map = seed_categories()
        seed_services_and_modals(cat_map)
        seed_satisfaction_metrics()
        seed_testimonials_and_stories()

    print("\n" + "=" * 70)
    print("🎉 ALL PRODUCTION DATA SEEDED SUCCESSFULLY WITH 100% FAITHFUL CONTENT!")
    print("=" * 70)


if __name__ == '__main__':
    main()
