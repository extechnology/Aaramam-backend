from django.db import migrations


def create_inquiry_review_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _ = Group.objects.get_or_create(name='Inquiry & Review Manager')

    target_codenames = [
        # Inquiries (Full access)
        'view_serviceinquiry', 'add_serviceinquiry', 'change_serviceinquiry', 'delete_serviceinquiry',
        'view_admissioninquiry', 'add_admissioninquiry', 'change_admissioninquiry', 'delete_admissioninquiry',
        # Reviews (Get, Create, Update only - NO delete)
        'view_testimonial', 'add_testimonial', 'change_testimonial',
        'view_guestfeedbacksubmission', 'add_guestfeedbacksubmission', 'change_guestfeedbacksubmission',
    ]

    perms = Permission.objects.filter(codename__in=target_codenames)
    group.permissions.set(perms)


def remove_inquiry_review_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Inquiry & Review Manager').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0001_initial'),
        ('Services', '0003_serviceimage'),
        ('Feedback', '0001_initial'),
        ('Contact', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_inquiry_review_group, remove_inquiry_review_group),
    ]
