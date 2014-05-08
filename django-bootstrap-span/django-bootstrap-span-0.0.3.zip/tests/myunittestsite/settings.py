"Unit test settings for dummy sqlite3 tests for django-bootstrap-span"

# This file was copied from...
# https://raw.githubusercontent.com/django/django/master/tests/test_sqlite.py

# This is an example test settings file for use with the Django test suite.
#
# The 'sqlite3' backend requires only the ENGINE setting (an in-
# memory database will be used). All other backends will require a
# NAME and potentially authentication information. See the
# following section in the docs for more information:
#
# https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/unit-tests/
#
# The different databases that Django supports behave differently in certain
# situations, so it is recommended to run the test suite against as many
# database backends as possible.  You may want to create a separate settings
# file for each of the backends you test against.

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'NAME' : 'db.default',
        'ENGINE': 'django.db.backends.sqlite3'
    },
    'other': {
        'NAME' : 'db.other',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

SECRET_KEY = "django_tests_secret_key"

# Use a fast hasher to speed up tests.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2',
    'django.contrib.admindocs',
    'bootstrap_toolkit',
    'bootstrap_span',
    'myunittestsite',
    'tinymce',
)

ROOT_URLCONF = 'myunittestsite.urls'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/_static_files/'
STATIC_ROOT = os.path.join(BASE_DIR, '_static_files')
STATICFILES_DIRS = (

)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

