from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UIConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App.UI'
    verbose_name = _('Home & UI Management')
