from django.core.management.base import BaseCommand
from App.Feedback.models import (
    FeedbackCategory,
    FeedbackStat,
    SanctuaryStory,
    Testimonial,
)


class Command(BaseCommand):
    help = 'Seeds initial feedback data (satisfaction metrics, categories, testimonials, and sanctuary stories) based on Aaramam UI'

    def handle(self, *args, **options):
        # 1. Satisfaction Metrics
        stats_data = [
            {
                'title': 'OVERALL GUEST SATISFACTION',
                'value': '5.0 / 5.0',
                'subtext': 'Based on 750+ sanctuary stays',
                'stars': 5,
                'order': 1,
            },
            {
                'title': 'DOCTOR ATTENTIVENESS',
                'value': '99.4%',
                'subtext': 'Round-the-clock medical care',
                'stars': 5,
                'order': 2,
            },
            {
                'title': 'THERAPEUTIC RESULTS',
                'value': '98.8%',
                'subtext': 'Postpartum recovery & pain relief',
                'stars': 5,
                'order': 3,
            },
            {
                'title': 'SANCTUARY CLEANLINESS & AMBIENCE',
                'value': '100%',
                'subtext': 'Hygienic & warm living quarters',
                'stars': 5,
                'order': 4,
            },
        ]
        for item in stats_data:
            stat, _ = FeedbackStat.objects.update_or_create(
                title=item['title'],
                defaults=item
            )
            self.stdout.write(self.style.SUCCESS(f"Metric: {stat.title} ({stat.value})"))

        # 2. Filter Categories
        categories_data = [
            {'name': '750+ Verified Mothers & Guests', 'order': 1},
            {'name': 'Postnatal Recovery Stories', 'order': 2},
            {'name': 'Doctor Attentiveness', 'order': 3},
            {'name': 'Private & Warm In-Stay', 'order': 4},
        ]
        cats = {}
        for item in categories_data:
            cat, _ = FeedbackCategory.objects.update_or_create(
                name=item['name'],
                defaults={'order': item['order'], 'is_active': True}
            )
            cats[cat.name] = cat
            self.stdout.write(self.style.SUCCESS(f"Category: {cat.name}"))

        # 3. Testimonials
        testimonials_data = [
            {
                'author_name': 'Dr. Claire Vance',
                'author_title': 'Integrative Medicine & Holistic Physician',
                'rating': 5,
                'is_verified_guest': True,
                'treatment_tag': 'Abhyanga Herbal Body Therapy',
                'quote': 'Experiencing the synchronized Abhyanga with warm Dhanwantharam thailam completely relieved my chronic lower back stiffness and nervous fatigue. The classical rhythmic strokes and authentic herbal decoctions are truly world-class.',
                'category': cats.get('Doctor Attentiveness'),
                'order': 1,
            },
            {
                'author_name': 'Marcus K.',
                'author_title': 'Verified Sanctuary Guest • London, UK',
                'rating': 5,
                'is_verified_guest': True,
                'treatment_tag': 'Shirodhara Medicated Oil Stream',
                'quote': 'Shirodhara here is transcendent. After months of chronic insomnia and mental burnout, a single 45-minute continuous warm oil stream session brought immediate mental stillness and the deepest sleep I have had in years.',
                'category': cats.get('Private & Warm In-Stay'),
                'order': 2,
            },
            {
                'author_name': 'Elena Rostova',
                'author_title': 'Holistic Spa & Wellness Director',
                'rating': 5,
                'is_verified_guest': True,
                'treatment_tag': 'Herbal Kizhi & Panchakarma Detox',
                'quote': 'The Herbal Kizhi poultice fermentation and Panchakarma protocols follow authentic Kerala Ayurvedic traditions with meticulous precision. My joint inflammation resolved, and my bodily vitality feels completely renewed.',
                'category': cats.get('Postnatal Recovery Stories'),
                'order': 3,
            },
        ]
        for t_data in testimonials_data:
            testi, _ = Testimonial.objects.update_or_create(
                author_name=t_data['author_name'],
                defaults=t_data
            )
            self.stdout.write(self.style.SUCCESS(f"Testimonial: {testi.author_name}"))

        # 4. Sanctuary Reels & Living Stories
        stories_data = [
            {
                'media_type': 'story',
                'account_handle': '@aaramamayurveda',
                'badge_tag': 'SANCTUARY LIFE',
                'title': 'Morning Uruli Decoctions & Nilavilakku',
                'caption': 'Every dawn begins with the sacred lighting of the bronze Nilavilakku and fresh Neem Thailam vessels gently simmering in...',
                'location_or_audio': 'Temple Bells of Kerala',
                'likes_count': 1540,
                'comments_count': 62,
                'time_ago_text': '7d ago',
                'order': 1,
            },
            {
                'media_type': 'story',
                'account_handle': '@dr.reshma_ayurveda',
                'badge_tag': 'DOCTOR INSIGHT',
                'title': 'Ayurvedic Cosmetology & Postpartum Radiance',
                'caption': 'Restoring natural skin radiance and holistic maternal vitality through customized Njavara lepam and Vata...',
                'location_or_audio': 'Vital Prana Rhythm',
                'likes_count': 2310,
                'comments_count': 78,
                'time_ago_text': '1w ago',
                'order': 2,
            },
        ]
        for s_data in stories_data:
            story, _ = SanctuaryStory.objects.update_or_create(
                title=s_data['title'],
                defaults=s_data
            )
            self.stdout.write(self.style.SUCCESS(f"Story: {story.title}"))

        self.stdout.write(self.style.SUCCESS('Successfully seeded Aaramam Feedback and Sanctuary Stories!'))
