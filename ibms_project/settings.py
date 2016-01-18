'''
Django settings for the DPaW IBMS application.
'''
from confy import database
import os
import sys
from unipath import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).ancestor(2)
PROJECT_DIR = os.path.join(BASE_DIR, 'ibms_project')
# Add PROJECT_DIR to the system path.
sys.path.insert(0, PROJECT_DIR)


# Settings defined in environment variables.
SECRET_KEY = os.environ['SECRET_KEY'] if os.environ.get('SECRET_KEY', False) else 'foo'
DEBUG = True if os.environ.get('DEBUG', False) == 'True' else False
CSRF_COOKIE_SECURE = True if os.environ.get('CSRF_COOKIE_SECURE', False) == 'True' else False
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True if os.environ.get('SESSION_COOKIE_SECURE', False) == 'True' else False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
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
APPLICATION_VERSION_NO = '2.0.2'
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
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.core.context_processors.request",
                "ibms_project.context_processors.standard",
            ],
        },
    }
]
DEBUG_INSTALLED_APPS = ('debug_toolbar',)
CONFLUENCE_URL = os.environ.get('CONFLUENCE_URL')
# URLs to the IBM Code Updater spreadsheets on Confluence, so that the Custodian
# can update them without a code change.
IBM_CODE_UPDATER_URI = '{}/login.action?os_destination={}/download/attachments/16646472/IBMS_CodeUpdate.xls'.format(CONFLUENCE_URL, CONFLUENCE_URL)
IBM_SERVICE_PRIORITY_URI = '{}/login.action?os_destination={}/download/attachments/16646472/IBMS_Service_Priorities_Update.xls'.format(CONFLUENCE_URL, CONFLUENCE_URL)
IBM_RELOAD_URI = '{}/login.action?os_destination={}/download/attachments/16646472/IBMS_BudgetTemplate.xls'.format(CONFLUENCE_URL, CONFLUENCE_URL)
IBM_DATA_AMEND_URI = '{}/login.action?os_destination={}/download/attachments/16646472/IBMS_Amendments.xls'.format(CONFLUENCE_URL, CONFLUENCE_URL)
SFM_OUTCOMETEMPLATE_URI = '{}/login.action?os_destination={}/download/attachments/16646472/sfmoutcometemplate.xls'.format(CONFLUENCE_URL, CONFLUENCE_URL)
HELP_URL = '{}'.format(CONFLUENCE_URL, CONFLUENCE_URL)
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
    if os.environ.get('INTERNAL_IP', False):  # Optionally add developer local IP
        INTERNAL_IPS.append(os.environ['INTERNAL_IP'])
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES
