"""
Django settings for inquitv project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# '.example.com' will match example.com, www.example.com, and
# any other subdomain of example.com
# ALLOWED_HOSTS = ['.inquitv.com']
ALLOWED_HOSTS = []
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#12horas
SESSION_COOKIE_AGE = (60*60*12)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'LOCATION': '127.0.0.1:11211',
        'LOCATION': 'unix:/tmp/memcached.sock',
        'TIMEOUT': SESSION_COOKIE_AGE,
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    #'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tv',
    'myuser',
    'captcha',
    'constance',
    'constance.backends.database',
    'axes',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.FailedLoginMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'inquitv.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tv.context_processors.days_subscription',
            ],
        },
    },
]

WSGI_APPLICATION = 'inquitv.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es' #en-us'

TIME_ZONE = 'Europe/Madrid'  #'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#Para cambiar formato a las fechas en el admin
from django.conf.locale.en import formats as en_formats
en_formats.DATE_FORMAT = "d/m/Y"
en_formats.DATETIME_FORMAT = "d/m/Y, H:i"
en_formats.DATE_INPUT_FORMATS = ('%d/%m/%Y', '%Y-%m-%d')
en_formats.DATETIME_INPUT_FORMATS = ('%d/%m/%Y %H:%M', '%Y-%m-%d %H:%M')



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_PATH = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    STATIC_PATH,
    )


# The page you want users to arrive at after they successful log in
LOGIN_REDIRECT_URL = '/tv/'
# The page users are directed to if they are not logged in,
# and are trying to access pages requiring authentication
LOGIN_URL = '/'
                                                           
## Used for django.core.mail
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True

## For django.contrib.auth password reset mechanism.
PASSWORD_RESET_TIMEOUT_DAYS = 1

## For my custom User
AUTH_USER_MODEL = 'myuser.MyUser'
# Timeout for the register email link
MYUSER_SIGNUP_TIMEOUT_DAYS = 1

## For django-constance[database]
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'V1_EMAIL_PAYMENT_HOST': ('imap.gmail.com', 'IMAP server of payment email.'),
    'V2_EMAIL_PAYMENT_USER': ('', 'Payment email address.'),
    'V3_EMAIL_PAYMENT_PASSWORD': ('', 'Payment email password.'),
    'V4_PRICE': (9.99, 'Price of the subscription.'),
    'V5_CURRENCY': ('EUR', 'Currency of the payment.'),
    'V6_SUBSCRIPTION_DAYS': (30, 'Days of subscription'),
    'V7_WORLD_FREE_ACCESS': (False, 'Free access for everybody.'),
}

## For django-axes
AXES_LOGIN_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = 1  #1 hour blocked
AXES_LOCKOUT_TEMPLATE = 'locked.html'
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True


try:
    from inquitv.settings_production import *
except ImportError:
    print('You need to define a settings_production.py')
    exit()
