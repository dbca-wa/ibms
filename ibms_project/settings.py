import os
import sys
import tomllib
from pathlib import Path

import dj_database_url
from dbca_utils.utils import env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = str(Path(__file__).resolve().parents[1])
PROJECT_DIR = str(Path(__file__).resolve().parents[0])
# Add PROJECT_DIR to the system path.
sys.path.insert(0, PROJECT_DIR)

# Settings defined in environment variables.
DEBUG = env("DEBUG", False)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SECRET_KEY = env("SECRET_KEY", "PlaceholderSecretKey")
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", False)
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", False)
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", False)
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY", None)
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", 0)
if not DEBUG:
    ALLOWED_HOSTS = env("ALLOWED_HOSTS", "localhost").split(",")
else:
    ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1").split(",")
INTERNAL_IPS = ["127.0.0.1", "::1"]
ROOT_URLCONF = "ibms_project.urls"
WSGI_APPLICATION = "ibms_project.wsgi.application"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Use whitenoise to add compression and caching support for static files.
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

INSTALLED_APPS = (
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django_extensions",
    "crispy_forms",
    "crispy_bootstrap5",
    "reversion",
    "webtemplate_dbca",
    "ibms",
    "sfm",
)
MIDDLEWARE = [
    "ibms_project.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "ibms_project.middleware.CurrentRequestUserMiddleware",
    "dbca_utils.middleware.SSOLoginMiddleware",
]
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (os.path.join(BASE_DIR, "ibms_project", "templates"),),
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.template.context_processors.csrf",
                "django.contrib.messages.context_processors.messages",
                "ibms_project.context_processors.standard",
            ],
        },
    }
]
SITE_TITLE = "Integrated Business Management System"
SITE_ACRONYM = "IBMS"
pyproject = open(os.path.join(BASE_DIR, "pyproject.toml"), "rb")
project = tomllib.load(pyproject)
pyproject.close()
APPLICATION_VERSION_NO = project["project"]["version"]
MANAGERS = (
    ("Zen Wee", "zen.wee@dbca.wa.gov.au", "9219 9928"),
    ("Graham Holmes", "graham.holmes@dbca.wa.gov.au", "9881 9212"),
    ("Neil Clancy", "neil.clancy@dbca.wa.gov.au", "9219 9926"),
)
SITE_ID = 1
ANONYMOUS_USER_ID = 1
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
IBM_CODE_UPDATER_URI = env("IBM_CODE_UPDATER_URI", "")
IBM_SERVICE_PRIORITY_URI = env("IBM_SERVICE_PRIORITY_URI", "")
IBM_RELOAD_URI = env("IBM_RELOAD_URI", "")
IBM_DATA_AMEND_URI = env("IBM_DATA_AMEND_URI", "")
DATA_UPLOAD_MAX_NUMBER_FIELDS = None  # Required to allow end-of-month GLPivot bulk deletes.
CSV_FILE_LIMIT = env("CSV_FILE_LIMIT", 100000000)
SHAREPOINT_IBMS = env("SHAREPOINT_IBMS", "")


# Database configuration
DATABASES = {
    # Defined in DATABASE_URL env variable.
    "default": dj_database_url.config(),
}

DATABASES["default"]["TIME_ZONE"] = "Australia/Perth"
# Use PostgreSQL connection pool if using that DB engine (use ConnectionPool defaults).
if "ENGINE" in DATABASES["default"] and any(eng in DATABASES["default"]["ENGINE"] for eng in ["postgresql", "postgis"]):
    if "OPTIONS" in DATABASES["default"]:
        DATABASES["default"]["OPTIONS"]["pool"] = True
    else:
        DATABASES["default"]["OPTIONS"] = {"pool": True}


# Static files (CSS, JavaScript, Images)
# Ensure that the media directory exists:
if not os.path.exists(os.path.join(BASE_DIR, "media")):
    os.mkdir(os.path.join(BASE_DIR, "media"))
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(PROJECT_DIR, "static"),)
WHITENOISE_ROOT = STATIC_ROOT


# Internationalisation.
USE_I18N = False
USE_TZ = True
TIME_ZONE = "Australia/Perth"
LANGUAGE_CODE = "en-us"
DATE_INPUT_FORMATS = ("%d/%m/%y", "%d/%m/%Y", "%d-%m-%y", "%d-%m-%Y", "%d %b %Y", "%d %b, %Y", "%d %B %Y", "%d %B, %Y")
DATETIME_INPUT_FORMATS = (
    "%d/%m/%y %H:%M",
    "%d/%m/%Y %H:%M",
    "%d-%m-%y %H:%M",
    "%d-%m-%Y %H:%M",
)


# Email settings.
EMAIL_HOST = env("EMAIL_HOST", "email.host")
EMAIL_PORT = env("EMAIL_PORT", 25)
NOREPLY_EMAIL = env("NOREPLY_EMAIL", "noreply@dbca.wa.gov.au")


# Logging settings - log to stdout/stderr
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"level": "INFO", "class": "logging.StreamHandler", "stream": sys.stdout, "formatter": "console"},
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
        "ibms": {"handlers": ["console"], "level": "INFO"},
    },
}

# django-crispy-forms config
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
