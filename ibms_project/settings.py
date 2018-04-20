'''
Django settings for the IBMS application.
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
SECRET_KEY = env('SECRET_KEY', 'PlaceholderSecretKey')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', False)
if not DEBUG:
    ALLOWED_HOSTS = env('ALLOWED_DOMAINS', '').split(',')
else:
    ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1', '::1']
ROOT_URLCONF = 'ibms_project.urls'
WSGI_APPLICATION = 'ibms_project.wsgi.application'
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django_extensions',
    'crispy_forms',
    'webtemplate_dbca',
    'ibms',
    'sfm',
)
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dpaw_utils.middleware.SSOLoginMiddleware',
]
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
SITE_TITLE = 'Integrated Business Management System'
SITE_ACRONYM = 'IBMS'
APPLICATION_VERSION_NO = '2.3'
ADMINS = ('asi@dbca.wa.gov.au',)
MANAGERS = (
    ('Zen Wee', 'zen.wee@dbca.wa.gov.au', '9219 9928'),
    ('Neil Clancy', 'neil.clancy@dbca.wa.gov.au', '9219 9926'),
)
SITE_ID = 1
ANONYMOUS_USER_ID = 1
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
CONFLUENCE_URL = env('CONFLUENCE_URL', '')
# URLs to the IBM Code Updater spreadsheets on Confluence, so that the Custodian
# can update them without a code change.
IBM_CODE_UPDATER_URI = env('IBM_CODE_UPDATER_URI', '')
IBM_SERVICE_PRIORITY_URI = env('IBM_SERVICE_PRIORITY_URI', '')
IBM_RELOAD_URI = env('IBM_RELOAD_URI', '')
IBM_DATA_AMEND_URI = env('IBM_DATA_AMEND_URI', '')
HELP_URL = '{}'.format(CONFLUENCE_URL)
CRISPY_TEMPLATE_PACK = 'bootstrap3'
DATA_UPLOAD_MAX_NUMBER_FIELDS = None  # Required to allow end-of-month GLPivot bulk deletes.


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


# Email settings.
EMAIL_HOST = env('EMAIL_HOST', 'email.host')
EMAIL_PORT = env('EMAIL_PORT', 25)


# Logging settings
# Ensure that the logs directory exists:
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.mkdir(os.path.join(BASE_DIR, 'logs'))
LOGGING = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'ibms.log'),
            'formatter': 'simple',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
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
