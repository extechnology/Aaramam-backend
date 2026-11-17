from django.core.management.base import BaseCommand
from App.UI.models import HeroBanner


class Command(BaseCommand):
    help = 'Seeds simplified Home Hero Banner: image, title, description, and 100+/200+ stat'

    def handle(self, *args, **options):
        banner, created = HeroBanner.objects.update_or_create(
            title='Motherhood Begins with Love and Care.',
            defaults={
                'description': 'Providing Gentle Ayurvedic Care, Comfort And Nurturing Support For Every New Mother And Baby.',
                'stat_number': '100+',
                'stat_label': 'Rejuvenated Guests • Classical Ayurvedic Care',
                'is_active': True,
            }
        )
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded simplified Hero Banner!')
        )
