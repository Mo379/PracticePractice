from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from user.models import UserProfile


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


class PasswordResetToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(UserProfile.objects.get(user=user).password_set)
        )
account_activation_token = TokenGenerator()
password_reset_token = PasswordResetToken()

