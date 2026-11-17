from django.core.management.base import BaseCommand
from App.Contact.models import AdmissionInquiry, SanctuaryContactInfo


class Command(BaseCommand):
    help = 'Seeds initial sanctuary contact details and a sample admission inquiry based on Aaramam Contact Page UI'

    def handle(self, *args, **options):
        contact_info, created = SanctuaryContactInfo.objects.update_or_create(
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
                    'Conveniently situated near Govt Taluk Hospital (Chantha), Feroke, Kozhikode, Keralam 673631. '
                    'Our centre provides dedicated postnatal mother & baby recovery, traditional Ayurvedic therapies, and personalised assistance.'
                ),
                'google_maps_url': 'https://maps.google.com/?q=Govt+Taluk+Hospital+Feroke+Kozhikode+673631',
                'facebook_url': 'https://facebook.com/aaramamayurveda',
                'instagram_url': 'https://instagram.com/aaramamayurveda',
                'youtube_url': 'https://youtube.com/@aaramamayurveda',
            }
        )
        self.stdout.write(self.style.SUCCESS(f"Sanctuary Contact Info: {contact_info.center_name}"))

        # Sample inquiry matching placeholder from the form
        inquiry, inq_created = AdmissionInquiry.objects.get_or_create(
            phone_number='+91 98745 43210',
            defaults={
                'name': 'Maya Menon',
                'program': 'postnatal',
                'bystander_accommodation': '1_bystander',
                'requirements_or_due_date': 'Expected delivery in March 2027. Need traditional Vata postpartum diet and gentle recovery massage.',
                'status': 'new',
            }
        )
        self.stdout.write(self.style.SUCCESS(f"Sample Inquiry: {inquiry.name} ({inquiry.phone_number})"))

        self.stdout.write(self.style.SUCCESS('Successfully seeded Aaramam Contact Page details!'))
