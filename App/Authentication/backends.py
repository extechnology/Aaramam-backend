from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrPhoneBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate using
    either their email address or phone number along with their password.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username is None:
            username = kwargs.get('email') or kwargs.get('phone_number') or kwargs.get(UserModel.USERNAME_FIELD)

        if not username or not password:
            return None

        username = str(username).strip()

        try:
            # Query by case-insensitive email or matching phone number
            user = UserModel.objects.filter(
                Q(email__iexact=username) | Q(phone_number__iexact=username)
            ).first()
        except Exception:
            user = None

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        # Run password hasher even if user not found to prevent timing attacks
        UserModel().set_password(password)
        return None
