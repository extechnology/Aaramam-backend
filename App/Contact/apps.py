from django.apps import AppConfig


class ContactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App.Contact'
    label = 'Contact'
    verbose_name = 'Contact & Doctor Inquiries'
