from datetime import date

from django.conf import settings
from django.utils import six
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class SignupTokenGenerator(object):
    """
    Strategy object used to generate and check tokens for the signup
    mechanism.
    """
    def make_token(self, user):
        """
        Returns a token that can be used once to do a signup for the
        given user.
        """
        return self._make_token_with_timestamp(user, self._num_days(self._today()))

    def check_token(self, user, token):
        """
        Check that a signup token is correct for a given user.
        """
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit
        if (self._num_days(self._today()) - ts) > settings.MYUSER_SIGNUP_TIMEOUT_DAYS:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)

        # By hashing on the internal state of the user and using state
        # that is sure to change (when user signup the is_active change),
        # we produce a hash that will be invalid as soon as it is used.
        # We limit the hash to 20 chars to keep URL short
        key_salt = "myuser.tokens.SignupTokenGenerator"

        # Ensure results are consistent across DB backends
        signup_timestamp = '' if user.date_joined is None else user.date_joined.replace(microsecond=0, tzinfo=None)

        value = (six.text_type(user.pk) + user.password +
                six.text_type(signup_timestamp) + six.text_type(timestamp))
        hash = salted_hmac(key_salt, value).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        # Used for mocking in tests
        return date.today()

signup_token_generator = SignupTokenGenerator()
