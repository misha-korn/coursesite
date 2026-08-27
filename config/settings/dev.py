from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

INSTALLED_APPS += ["debug_toolbar", "corsheaders"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")
INTERNAL_IPS = ["127.0.0.1"]

CORS_ALLOWED_ORIGINS=env.list("CORS_ALLOWED_ORIGINS", default=["http://127.0.0.1:5173"])
