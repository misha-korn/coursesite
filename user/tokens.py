from django.conf import settings
from itsdangerous import URLSafeTimedSerializer

RESET_PASSWORD_SALT = "reset-password"
CHANGE_EMAIL_SALT = "change-email"
VERIFY_EMAIL_SALT = "verify-email"
RESET_PASSWORD_MAX_AGE = 60 * 60 * 24 * 3
CHANGE_EMAIL_MAX_AGE = 60 * 60 * 24
VERIFY_EMAIL_MAX_AGE = 60 * 60 * 24

reset_password_serializer = URLSafeTimedSerializer(settings.SECRET_KEY, RESET_PASSWORD_SALT)
change_email_serializer = URLSafeTimedSerializer(settings.SECRET_KEY, CHANGE_EMAIL_SALT)
verify_email_serializer = URLSafeTimedSerializer(settings.SECRET_KEY, VERIFY_EMAIL_SALT)


def make_reset_password_token(user):
    return reset_password_serializer.dumps({"uid": user.pk, "pwd": user.password[:16]})


def read_reset_password_token(token):
    return reset_password_serializer.loads(token, max_age=RESET_PASSWORD_MAX_AGE)


def make_change_email_token(user, new_email):
    return change_email_serializer.dumps(
        {"uid": user.pk, "new_email": new_email, "pwd": user.password[:16]}
    )


def read_change_email_token(token):
    return change_email_serializer.loads(token, max_age=CHANGE_EMAIL_MAX_AGE)


def make_verify_email_token(user):
    return verify_email_serializer.dumps({"uid": user.pk, "pwd": user.password[:16]})


def read_verify_email_token(token):
    return verify_email_serializer.loads(token, max_age=VERIFY_EMAIL_MAX_AGE)
