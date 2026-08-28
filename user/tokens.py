from django.conf import settings
from itsdangerous import URLSafeSerializer


RESET_SALT = 'reset-password'
RESET_MAX_AGE = 60 * 60 * 24 * 3

serializer = URLSafeSerializer(settings.SECRET_KEY, RESET_SALT)

def make_reset_password_token(user):
    return serializer.dumps({"uid": user.pk, "pwd": user.password[:16]})

def read_reset_password_token(token):
    return serializer.loads(token, max_age=RESET_MAX_AGE)
