# prof
###### Full Django User Registration System (signup, login, logout, change username, change password, reset password)

[![prof](https://img.shields.io/badge/build-stopped-red.svg)]()
[![version](https://img.shields.io/badge/version-1.0.0-green.svg)]()
[![status](https://img.shields.io/badge/status-failed-red.svg)]()
[![python](https://img.shields.io/badge/python-3-blue.svg)](http://www.python.org/download/)
[![django](https://img.shields.io/badge/django-3-blue.svg)](https://pypi.org/project/Django/)
[![windows](https://img.shields.io/badge/windows-tested-brightgreen.svg)]()

## REQUIREMENTS
- Python-3 --> http://www.python.org/download/
- Django-3 --> https://pypi.org/project/Django/
- six --> https://pypi.org/project/six/
- django-crispy-forms --> https://pypi.org/project/django-crispy-forms/

## Notes
- You can easily edit templates (or project).
- Very simple and easy to use.
- Created for educational purposes.

## Installation

- Clone this repo:
	
	```
	$ git clone https://github.com/AI35/prof
	```

## Configuration

#### Settings.py:
- INSTALLED_APPS :
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'prof',
    'crispy_forms',
    'six',
]
```
- TEMPLATES :
```
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'prof/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```
- Add LOGIN_URL :
```
LOGIN_URL = '/login/'
```
- Add EMAIL settings:
	- if you want use gmail account don't forget enable low secure app in your google account settings.
```
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'example@gmail.com'
EMAIL_HOST_PASSWORD = '*****'
EMAIL_PORT = 587
```
#### Project urls.py:
```
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('prof.urls')),
]

```

###### ALI .B .OTH