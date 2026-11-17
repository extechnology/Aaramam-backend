from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model supporting authentication via email or phone number.
    """
    email = models.EmailField(
        _('email address'),
        unique=True,
        null=True,
        blank=True,
        max_length=255,
        db_index=True,
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def clean(self):
        super().clean()
        if not self.email and not self.phone_number:
            raise ValidationError(_('Either an email address or a phone number must be provided.'))

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email).lower()
        else:
            self.email = None

        if self.phone_number:
            self.phone_number = str(self.phone_number).strip()
            if not self.phone_number:
                self.phone_number = None
        else:
            self.phone_number = None

        super().save(*args, **kwargs)

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email or self.phone_number or f"User #{self.pk}"

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.first_name or self.email or self.phone_number or f"User #{self.pk}"

    def __str__(self):
        identifier = self.email or self.phone_number or f"User #{self.pk}"
        if self.first_name or self.last_name:
            return f"{self.full_name} ({identifier})"
        return identifier
