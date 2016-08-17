'''
Django settings for the DPaW IBMS application.
'''
from confy import database, env
import os
import sys
from unipath import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).ancestor(2)
PROJECT_DIR = os.path.join(BASE_DIR, 'ibms_project')
# Add PROJECT_DIR to the system path.
sys.path.insert(0, PROJECT_DIR)


# Settings defined in environment variables.
DEBUG = env('DEBUG', False)
SECRET_KEY = env('SECRET_KEY')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', False)
INTERNAL_IPS = ['127.0.0.1', '::1']
if not DEBUG:
    # Localhost, UAT and Production hosts
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        'ibms.dpaw.wa.gov.au',
        'ibms.dpaw.wa.gov.au.',
        'ibms-uat.dpaw.wa.gov.au',
        'ibms-uat.dpaw.wa.gov.au.',
    ]


# Database configuration
DATABASES = {
    # Defined in DATABASE_URL env variable.
    'default': database.config(),
}


# Setup directories for content.
STATICFILES_DIRS = (os.path.join(PROJECT_DIR, 'static'), )
# Ensure that the media directory exists:
if not os.path.exists(os.path.join(BASE_DIR, 'media')):
    os.mkdir(os.path.join(BASE_DIR, 'media'))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'


# Internationalisation.
USE_I18N = False
USE_TZ = True
TIME_ZONE = 'Australia/Perth'
LANGUAGE_CODE = 'en-us'
DATE_INPUT_FORMATS = (
    '%d/%m/%y',
    '%d/%m/%Y',
    '%d-%m-%y',
    '%d-%m-%Y',
    '%d %b %Y',
    '%d %b, %Y',
    '%d %B %Y',
    '%d %B, %Y')
DATETIME_INPUT_FORMATS = (
    '%d/%m/%y %H:%M',
    '%d/%m/%Y %H:%M',
    '%d-%m-%y %H:%M',
    '%d-%m-%Y %H:%M',)


# Project settings.
SITE_TITLE = 'Integrated Business Management System'
SITE_ACRONYM = 'IBMS'
APPLICATION_VERSION_NO = '2.1'
ADMINS = ('asi@dpaw.wa.gov.au',)
MANAGERS = (
    ('Zen Wee', 'zen.wee@dpaw.wa.gov.au', '9219 9928'),
    ('Neil Clancy', 'neil.clancy@dpaw.wa.gov.au', '9219 9926'),
)
ROOT_URLCONF = 'ibms_project.urls'
WSGI_APPLICATION = 'ibms_project.wsgi.application'
SITE_ID = 1
ANONYMOUS_USER_ID = 1
EMAIL_HOST = 'alerts.corporateict.domain'
EMAIL_PORT = 25
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django_extensions',
    'crispy_forms',
    'webtemplate_dpaw',
    'ibms',
    'sfm',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dpaw_utils.middleware.SSOLoginMiddleware',
)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'ibms_project', 'templates'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.template.context_processors.csrf',
                'django.contrib.messages.context_processors.messages',
                "ibms_project.context_processors.standard",
            ],
        },
    }
]
CONFLUENCE_URL = env('CONFLUENCE_URL', '')
# URLs to the IBM Code Updater spreadsheets on Confluence, so that the Custodian
# can update them without a code change.
IBM_CODE_UPDATER_URI = env('IBM_CODE_UPDATER_URI')
IBM_SERVICE_PRIORITY_URI = env('IBM_SERVICE_PRIORITY_URI')
IBM_RELOAD_URI = env('IBM_RELOAD_URI')
IBM_DATA_AMEND_URI = env('IBM_DATA_AMEND_URI')
HELP_URL = '{}'.format(CONFLUENCE_URL)
CRISPY_TEMPLATE_PACK = 'bootstrap3'


# Logging settings
# Ensure that the logs directory exists:
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.mkdir(os.path.join(BASE_DIR, 'logs'))
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'ibms.log'),
            'formatter': 'verbose',
            'maxBytes': '16777216'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'INFO'
        },
        'log': {
            'handlers': ['file'],
            'level': 'INFO'
        },
    }
}
DEBUG_LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'debug-ibms.log'),
            'formatter': 'verbose',
            'maxBytes': '16777216'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
        'log': {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
    }
}


# Supplement some settings when DEBUG is True.
if DEBUG:
    LOGGING = DEBUG_LOGGING
    if env('INTERNAL_IP', False):  # Optionally add developer local IP
        INTERNAL_IPS.append(env('INTERNAL_IP'))
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES
