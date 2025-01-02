from pathlib import Path
from decouple import config

import os
from dotenv import load_dotenv
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()
APP_NAME = "Bloggy"

AUTH_USER_MODEL = 'users.CustomUser'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['3.145.9.156']

SITE_ID = 1


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',


    #My Apps
    'blog',
    'users',

    
    'django_recaptcha',

    # Django Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',  # Facebook
    'allauth.socialaccount.providers.twitter',   # Twitter
    'allauth.socialaccount.providers.github',    # GitHub
    'allauth.socialaccount.providers.google',    # Google
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',# allauth middleware
]


ROOT_URLCONF = 'myblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required by Allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                  #custom context processor here
                'blog.context_processors.notifications',
            ],
        },
    },
]


AUTHENTICATION_BACKENDS = [
    'users.backends.CustomUserAuthenticationBackend',  # custom backend
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth backend
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "my_cache_table",
    }
}

SECURITY_SALT = os.getenv('SECURITY_SALT')

WSGI_APPLICATION = 'myblog.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

import os
import sys
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('MYSQL_DATABASE_NAME'),
            'USER': os.getenv('MYSQL_DATABASE_USER'),
            'PASSWORD': os.getenv('MYSQL_DATABASE_PASSWORD'),
            'HOST': os.getenv('MYSQL_DATABASE_HOST', default='127.0.0.1'),
            'PORT': os.getenv('MYSQL_DATABASE_PORT', default='3306'),
        }
    }
    
    # Test MySQL connection
    import pymysql
    pymysql.connect(
        host=os.getenv('MYSQL_DATABASE_HOST', default='127.0.0.1'),
        user=os.getenv('MYSQL_DATABASE_USER'),
        password=os.getenv('MYSQL_DATABASE_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE_NAME'),
        port=int(os.getenv('MYSQL_DATABASE_PORT', default='3306')),
    )
except Exception as e:
    print(f"Failed to connect to MySQL: {e}", file=sys.stderr)
    print("Switching to SQLite as fallback database.", file=sys.stderr)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

ACCOUNT_ADAPTER = "users.adapter.CustomAccountAdapter"
SOCIALACCOUNT_ADAPTER = "users.adapter.CustomSocialAccountAdapter"

from decouple import config, UndefinedValueError

ENVIRONMENT = os.getenv('DJANGO_ENV', default='development')

try:
    if ENVIRONMENT == 'production':
        RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
        RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

        # Raise an error if test keys are mistakenly used in production
        if RECAPTCHA_PUBLIC_KEY == "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI" or \
           RECAPTCHA_PRIVATE_KEY == "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe":
            raise ValueError("Test reCAPTCHA keys are not allowed in production.")
    else:
        # Use test keys for development
        RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
        RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
except UndefinedValueError:
    raise ValueError("RECAPTCHA keys are missing. Please define them in your environment.")


SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']


# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"Bloggy <{EMAIL_HOST_USER}>"

# Email settings (optional)
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = True

# Facebook OAuth Credentials
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')

# Google OAuth Credentials 
GOOGLE_client_id = os.getenv('GOOGLE_client_id')
GOOGLE_client_secret = os.getenv('GOOGLE_client_secret')

# Twitter/X OAuth 1.0a Credentials
TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')

# GitHub OAuth Credentials
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

# Social Account Providers Configuration
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'APP': {
            'client_id': FACEBOOK_APP_ID,
            'secret': FACEBOOK_APP_SECRET,
        },
        'SCOPE': ['email', 'public_profile'],
        'VERIFIED_EMAIL': False,
    },
    'google': {
        'APP': {
            'client_id': GOOGLE_client_id,
            'secret': GOOGLE_client_secret,
        },
        'SCOPE': ['profile', 'email'],
        'VERIFIED_EMAIL': True,
    },
    'twitter': {
        'APP': {
            'client_id': TWITTER_CONSUMER_KEY,
            'secret': TWITTER_CONSUMER_SECRET,
        },
    },
    'github': {
        'APP': {
            'client_id': GITHUB_CLIENT_ID,
            'secret': GITHUB_CLIENT_SECRET,
        },
        'SCOPE': ['user', 'user:email'],
        'VERIFIED_EMAIL': True,
    },
}

# Redirect URLs
LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL = 'http://127.0.0.1:8000/'
LOGIN_URL = '/users/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = "/"  # After logout
ACCOUNT_LOGOUT_ON_GET = True
SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'

SOCIALACCOUNT_LOGIN_ON_GET = True




# Configure Allauth to use email for authentication
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"

# Redirects
ACCOUNT_SIGNUP_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_AUTO_SIGNUP = True




# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'


USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
