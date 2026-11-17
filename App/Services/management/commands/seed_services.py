from django.core.management.base import BaseCommand
from App.Services.models import (
    Service,
    ServiceAmenity,
    ServiceCarePillar,
    ServiceCategory,
    ServiceImage,
    ServiceInclusion,
    ServiceTherapy,
)


class Command(BaseCommand):
    help = 'Seeds services packages, categories, and detailed modal data based on Aaramam UI'

    def handle(self, *args, **options):
        # 1. Categories
        cat_postnatal, _ = ServiceCategory.objects.get_or_create(
            name='Prasava Raksha',
            defaults={
                'description': '24/7 holistic nursing, daily warm medicated oil Abhyanga, herbal baths, lactation support & customized Vata nutrition for mother, baby & bystander at Feroke Center, Kozhikode.',
                'order': 1,
            }
        )
        cat_wellness, _ = ServiceCategory.objects.get_or_create(
            name='Postnatal Care',
            defaults={
                'description': 'Traditional Kerala Ayurvedic postnatal care and maternal rejuvenation.',
                'order': 2,
            }
        )
        ServiceCategory.objects.get_or_create(name='28 Days Nurture', defaults={'order': 3})
        ServiceCategory.objects.get_or_create(name='21 Days Wellness', defaults={'order': 4})
        ServiceCategory.objects.get_or_create(name='14 Days Recovery', defaults={'order': 5})

        # 2. Main Package from the Detailed Modal Screenshot:
        modal_package = {
            'title': 'Ayurvedic Wellness Therapies',
            'subtitle': 'Guided by Experienced Ayurvedic Doctors',
            'doctor_guidance': 'Guided by Experienced Ayurvedic Doctors',
            'badge_tag': 'AYURVEDIC POSTNATAL',
            'duration_tag': '28 Days Care',
            'image_overlay_badge': 'Doctor-Led Wellness',
            'rating': 4.9,
            'review_count': 345,
            'short_description': 'Traditional Kerala Ayurvedic therapies, promoting maternal wellness, relaxation and balanced recovery through personalised care.',
            'detailed_description': (
                'We offer traditional Kerala Ayurvedic therapies, promoting maternal wellness, relaxation '
                'and balanced recovery through personalised care guided by experienced Ayurvedic doctors.'
            ),
            'recommended_for': 'Mothers & wellness seekers seeking balanced recovery and inner calmness',
            'heritage_title': '30+ Years Generational Vaidya Heritage',
            'heritage_location': 'Aaramam Centre • Near Govt Taluk Hospital, Feroke',
            'location': 'Aaramam Sanctuary • Near Govt Taluk Hospital, Feroke, Kozhikode',
            'order': 0,
            'is_featured': True,
            'category': cat_postnatal,
            'therapies': [
                'Shirodhara Oil Stream',
                'Herbal Kizhi Poultices',
                'Physician Assessment',
                'Tridosha Balancing',
            ],
            'amenities': [
                {'title': 'Doctor Supervised', 'subtext': '24/7 BAMS Observation', 'icon': 'health_and_safety', 'order': 1},
                {'title': 'Postpartum Diet', 'subtext': 'Fresh Vata-Balancing Meals', 'icon': 'restaurant', 'order': 2},
                {'title': 'Private AC Suite', 'subtext': 'Bystander Stay Included', 'icon': 'bed', 'order': 3},
                {'title': 'Attached Hot Bath', 'subtext': 'Herbal Water Facilities', 'icon': 'bathtub', 'order': 4},
            ],
            'care_pillars': [
                {'title': 'Doctor-Led Care', 'subtext': 'Daily BAMS physician observation', 'icon': 'stethoscope', 'order': 1},
                {'title': 'Pathya Ahara', 'subtext': 'Warm Vata postpartum diet', 'icon': 'restaurant_menu', 'order': 2},
                {'title': 'Mother & Baby', 'subtext': 'Gentle massage & Vethu bath', 'icon': 'child_care', 'order': 3},
                {'title': 'Bystander Stay', 'subtext': 'Family stay included', 'icon': 'hotel', 'order': 4},
            ],
            'inclusions': [
                'Traditional Kerala Ayurvedic therapies & Shirodhara',
                'Maternal wellness, relaxation & balanced recovery',
                'Personalised care guided by senior Ayurvedic doctors',
                'Herbal Kizhi and classical rejuvenating protocols',
            ],
        }

        # Seed the modal package
        service, created = Service.objects.update_or_create(
            title=modal_package['title'],
            defaults={
                k: v for k, v in modal_package.items()
                if k not in ['therapies', 'amenities', 'care_pillars', 'inclusions']
            }
        )
        service.inclusions.all().delete()
        for i, text in enumerate(modal_package['inclusions'], 1):
            ServiceInclusion.objects.create(service=service, text=text, order=i)

        service.therapies.all().delete()
        for i, name in enumerate(modal_package['therapies'], 1):
            ServiceTherapy.objects.create(service=service, name=name, order=i)

        service.amenities.all().delete()
        for item in modal_package['amenities']:
            ServiceAmenity.objects.create(service=service, **item)

        service.care_pillars.all().delete()
        for item in modal_package['care_pillars']:
            ServiceCarePillar.objects.create(service=service, **item)

        self.stdout.write(self.style.SUCCESS(f"Seeded Detailed Modal Package: {service.title}"))

        # Also populate therapies, amenities, and care pillars on the other packages
        other_packages = [
            'Extended Shared Nurture Postnatal',
            'Value Shared Wellness Postnatal',
            'Affordable Shared Recovery Postnatal',
        ]
        for title in other_packages:
            pkg = Service.objects.filter(title=title).first()
            if pkg:
                if not pkg.therapies.exists():
                    for i, name in enumerate(['Shirodhara Oil Stream', 'Herbal Kizhi Poultices', 'Physician Assessment', 'Tridosha Balancing'], 1):
                        ServiceTherapy.objects.create(service=pkg, name=name, order=i)
                if not pkg.amenities.exists():
                    for item in modal_package['amenities']:
                        ServiceAmenity.objects.create(service=pkg, **item)
                if not pkg.care_pillars.exists():
                    for item in modal_package['care_pillars']:
                        ServiceCarePillar.objects.create(service=pkg, **item)

        # Seed sample gallery placeholders for each service package
        sample_gallery = [
            {'caption': 'Mother & Newborn Care Suite', 'alt_text': 'Private maternal suite with newborn cradle', 'order': 1, 'is_primary': True},
            {'caption': 'Warm Oil Abhyanga Therapy Room', 'alt_text': 'Traditional wooden droni treatment table', 'order': 2, 'is_primary': False},
            {'caption': 'Herbal Kizhi & Decoction Station', 'alt_text': 'Freshly prepared medicated herbal poultices and oils', 'order': 3, 'is_primary': False},
            {'caption': 'Vethu Herbal Water Bath Facility', 'alt_text': 'Therapeutic warm bath area for postpartum healing', 'order': 4, 'is_primary': False},
        ]
        for s in Service.objects.all():
            if not s.images.exists():
                for g in sample_gallery:
                    ServiceImage.objects.create(service=s, **g)

        self.stdout.write(self.style.SUCCESS('Successfully updated and seeded all services and detailed modal data!'))
