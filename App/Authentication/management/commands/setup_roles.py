from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Creates and configures the "Inquiry & Review Manager" group with permissions '
        'to access all inquiries (Services & Admissions) and only get, create, and update reviews (no delete).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--assign-user',
            type=str,
            help='Email or phone number of an existing user to add to this group and mark as is_staff=True.',
        )

    def handle(self, *args, **options):
        group_name = 'Inquiry & Review Manager'
        group, created = Group.objects.get_or_create(name=group_name)

        # Precise permissions:
        # 1. Inquiries: Full access (get, create, update, delete)
        # 2. Reviews: Only get (view), create (add), and update (change) — DELETE permanently excluded
        target_permissions = [
            # Inquiries (Services Package Inquiries) - Full Access
            ('Services', 'serviceinquiry', 'view_serviceinquiry'),
            ('Services', 'serviceinquiry', 'add_serviceinquiry'),
            ('Services', 'serviceinquiry', 'change_serviceinquiry'),
            ('Services', 'serviceinquiry', 'delete_serviceinquiry'),
            # Inquiries (Contact Admission & Doctor Consultation Inquiries) - Full Access
            ('Contact', 'admissioninquiry', 'view_admissioninquiry'),
            ('Contact', 'admissioninquiry', 'add_admissioninquiry'),
            ('Contact', 'admissioninquiry', 'change_admissioninquiry'),
            ('Contact', 'admissioninquiry', 'delete_admissioninquiry'),
            # Reviews (Guest Testimonials) - View, Add, Change ONLY (NO delete)
            ('Feedback', 'testimonial', 'view_testimonial'),
            ('Feedback', 'testimonial', 'add_testimonial'),
            ('Feedback', 'testimonial', 'change_testimonial'),
            # Reviews (Guest Feedback Submissions) - View, Add, Change ONLY (NO delete)
            ('Feedback', 'guestfeedbacksubmission', 'view_guestfeedbacksubmission'),
            ('Feedback', 'guestfeedbacksubmission', 'add_guestfeedbacksubmission'),
            ('Feedback', 'guestfeedbacksubmission', 'change_guestfeedbacksubmission'),
        ]

        perms_to_set = []
        for app_label, model, codename in target_permissions:
            perm = Permission.objects.filter(
                content_type__app_label=app_label,
                content_type__model=model,
                codename=codename,
            ).first()
            if perm:
                perms_to_set.append(perm)
            else:
                self.stdout.write(
                    self.style.WARNING(f"Permission not found: {app_label}.{codename}")
                )

        group.permissions.set(perms_to_set)

        status_word = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f'{status_word} group "{group.name}" with {group.permissions.count()} permissions:\n'
                f'  • Inquiries (Services & Contact): Full access (Get, Create, Update, Delete)\n'
                f'  • Reviews (Testimonials & Submissions): Get, Create, and Update ONLY (Delete restricted)'
            )
        )

        assign_target = options.get('assign_user')
        if assign_target:
            user = (
                User.objects.filter(email__iexact=assign_target).first()
                or User.objects.filter(phone_number=assign_target).first()
            )
            if user:
                user.groups.add(group)
                user.is_staff = True
                user.save(update_fields=['is_staff'])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned user "{user.get_full_name() or user.email}" to group "{group.name}" '
                        f'and enabled is_staff=True for admin portal access.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'User with identifier "{assign_target}" not found.')
                )
