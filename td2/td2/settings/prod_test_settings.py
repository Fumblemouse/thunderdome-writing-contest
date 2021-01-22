"""Settings for production environment"""
import os
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False
DEBUG_LOGGING = False
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_TEST_TEST_ENGINE'),
        'NAME': os.getenv('DATABASE_TEST_TEST_NAME'),

    }
}
ALLOWED_HOSTS = ['fumblemouse.pythonanywhere.com']

SECURE_HSTS_SECONDS = 2592000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True

## that requests over HTTP are redirected to HTTPS. aslo can config in webserver
SECURE_SSL_REDIRECT = False

# for more security
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Strict'
