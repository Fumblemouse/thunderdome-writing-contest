"""Settings for production environment"""
import os
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PWD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'TEST': {
            'NAME': os.getenv('DATABASE_TEST_NAME'),
        },
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }

    }
}
ALLOWED_HOSTS = ['fumblemouse.pythonanywhere.com']
