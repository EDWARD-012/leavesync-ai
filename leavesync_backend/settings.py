from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------
# BASIC CONFIG
# ------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "changeme")
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "leavesync-ai.onrender.com",
    "localhost",
    "127.0.0.1",
]

SITE_ID = 1

# ------------------------------------------------------------
# INSTALLED APPS
# ------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party
    "rest_framework",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",

    # local app
    "core",
]

ROOT_URLCONF = "leavesync_backend.urls"
WSGI_APPLICATION = "leavesync_backend.wsgi.application"

# ------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # only once
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(default=os.getenv("DATABASE_URL"))
}

# ------------------------------------------------------------
# AUTH
# ------------------------------------------------------------
AUTH_USER_MODEL = "core.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/logout/success/"

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_ADAPTER = "core.adapters.CustomSocialAccountAdapter"

# ------------------------------------------------------------
# GOOGLE PROVIDER
# ------------------------------------------------------------
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_SECRET"),   # mapped to your env
            "key": "",
        },
        "SCOPE": ["email", "profile"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

# ------------------------------------------------------------
# EMAIL CONFIG
# ------------------------------------------------------------
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER
)

ACCOUNT_EMAIL_CONFIRMATION_TEMPLATE = "account/email/email_confirmation_message.html"
ACCOUNT_EMAIL_HTML_TEMPLATE = "account/email/email_confirmation_message.html"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

# ------------------------------------------------------------
# STATIC FILES
# ------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------------------------------------
# TEMPLATES
# ------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "leavesync_backend.wsgi.application"

# ------------------------------------------------------------
# AI CONFIG
# ------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
