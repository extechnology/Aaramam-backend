from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager where email or phone number can be used as identifiers.
    """

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        """
        Create and return a regular user with an email or phone number and password.
        """
        if not email and not phone_number:
            raise ValueError(_('User must have either an email address or a phone number.'))

        if email:
            email = self.normalize_email(email).lower()
        else:
            email = None

        if phone_number:
            phone_number = str(phone_number).strip()
            if not phone_number:
                phone_number = None
        else:
            phone_number = None

        user = self.model(
            email=email,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, phone_number=None, **extra_fields):
        """
        Create and return a superuser with an email, password, and optional phone number.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        if not email:
            raise ValueError(_('Superuser must have an email address.'))

        return self.create_user(
            email=email,
            phone_number=phone_number,
            password=password,
            **extra_fields
        )
