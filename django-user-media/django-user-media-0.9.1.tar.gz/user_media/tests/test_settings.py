"""Settings that need to be set in order to run the tests."""
import os


PROJECT_ROOT = os.path.dirname(__file__)

DEBUG = True
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'user_media.tests.urls'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(__file__, '../../../static/')
MEDIA_ROOT = os.path.join(__file__, '../../../media/')
STATICFILES_DIRS = (
    os.path.join(__file__, 'test_static'),
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), '../templates'),
)

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), 'coverage')
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'test_app', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django_jasmine',
    'django_nose',
    'easy_thumbnails',
    'django_libs',
    'generic_positions',
]

INTERNAL_APPS = [
    'user_media',
    'user_media.tests.test_app',
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS
COVERAGE_MODULE_EXCLUDES += EXTERNAL_APPS

SECRET_KEY = 'xxx'
