"""
Django settings for complaints_portal project.
PythonAnywhere-friendly + local-dev friendly.
"""

from pathlib import Path
import os

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------
# Core env helpers
# ------------------------------------------------------------
def env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "y", "on")


def env_list(name: str, default=None):
    val = os.getenv(name)
    if not val:
        return default or []
    # comma-separated
    return [x.strip() for x in val.split(",") if x.strip()]


# ------------------------------------------------------------
# Security / Debug
# ------------------------------------------------------------
# IMPORTANT: On PythonAnywhere set SECRET_KEY in "Web" tab -> Environment variables
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-change-me")

DEBUG = env_bool("DJANGO_DEBUG", True)

# On PythonAnywhere set:
# DJANGO_ALLOWED_HOSTS = springtimes.pythonanywhere.com
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=[])

# If you want local dev without env vars:
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# ------------------------------------------------------------
# Applications
# ------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tickets",
]


# ------------------------------------------------------------
# Middleware
# ------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ------------------------------------------------------------
# URLs / WSGI
# ------------------------------------------------------------
ROOT_URLCONF = "complaints_portal.urls"
WSGI_APPLICATION = "complaints_portal.wsgi.application"


# ------------------------------------------------------------
# Templates
# ------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]


# ------------------------------------------------------------
# Database (SQLite for demo)
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ------------------------------------------------------------
# Password validation
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ------------------------------------------------------------
# Internationalization
# ------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------
# Static + Media  (Fixes collectstatic STATIC_ROOT error)
# ------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Optional: keep this ONLY if you actually have a /static folder.
# This avoids the warning: "STATICFILES_DIRS ... does not exist"
_static_dir = BASE_DIR / "static"
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ------------------------------------------------------------
# Auth redirects
# ------------------------------------------------------------
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/post-login/"   # or "/staff/tickets/" if that's your default staff page
LOGOUT_REDIRECT_URL = "/accounts/login/"


# ------------------------------------------------------------
# Email (safe defaults)
# ------------------------------------------------------------
EMAIL_BACKEND = os.getenv(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "DISCO Complaints <no-reply@example.com>")

# Handy for building absolute links in emails
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "http://127.0.0.1:8000")


# ------------------------------------------------------------
# Security settings for production (when DEBUG=False)
# ------------------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

    # If you're on PythonAnywhere with https://<username>.pythonanywhere.com
    CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])


# ------------------------------------------------------------
# Default primary key type
# ------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
