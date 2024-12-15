"""
Django settings for SolidSteel project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(bco9)^g@zu52)zwrq8ms=zt@y6n62$1x4muag=f*chr4n+^06'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#NOOOOOOO BORRAAAR POORFAVOOOOOOR
ALLOWED_HOSTS = ['*'] 

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login',
    'menu',
    'register',
    'cart',
    'pay',
    'product',
    'recycler',
    'shipping',
    'supplier',
    'static',
    'client' ,
    
    #Google
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

#se refiere a tomar informacion básica del profile and email para poder iniciar sesion
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

#id en el sitio de administrador de django
SITE_ID = 3 

#Para evitar el menú o pantalla intermedia de Google con inicio de sesion o registro
SOCIALACCOUNT_LOGIN_ON_GET = True

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Para autenticación convencional
    'allauth.account.auth_backends.AuthenticationBackend',  # Para Google
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', #también estop
]

ROOT_URLCONF = 'SolidSteel.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # Ruta para plantillas generales
        ],
        'APP_DIRS': True,  # Permite buscar plantillas en las carpetas de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_items_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'SolidSteel.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

#NOOOOOOO BORRAAAR POORFAVOOOOOOR
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'solid_db',  # El nombre que aparece en tu lista
        'USER': 'root',     # Debe ser el nombre de tu usuario 
        'PASSWORD': '',
        'HOST': '',  # Tu host de MySQL 
        'PORT': '3306',  # Puerto estándar para MySQL
        'OPTIONS': {
           'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Static files directories (carpeta de desarrollo para archivos estáticos)
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Carpeta general para archivos estáticos en desarrollo
]

# Carpeta donde se recopilarán todos los archivos estáticos para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Directorio donde collectstatic guardará los archivos estáticos

# Configuración para archivos de medios (si usas archivos subidos por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # Directorio donde se guardarán los archivos de medios subidos por los usuarios


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'solidsteel117@gmail.com'  # Pon tu correo de Gmail aquí
EMAIL_HOST_PASSWORD = ''  # La contraseña de aplicación de Google
DEFAULT_FROM_EMAIL = 'noreply@solidsteel.com'

#Redirect para google
LOGIN_REDIRECT_URL = '/products/'  # Redirige a la página de cliente
LOGOUT_REDIRECT_URL = '/login/'  # Redirige a la página de login

#acceso para rekognition en aws
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_REGION = 'us-west-2'  # Cambia esto según tu región

#Stripe
STRIPE_PUBLIC_KEY = ""
STRIPE_SECRET_KEY_TEST = ""
STRIPE_WEBHOOK_SECRET = ""
REDIRECT_DOMAIN = 'https://solid-steels.com'

#PayPal
PAYPAL_CLIENT_ID = ''
PAYPAL_CLIENT_SECRET = ''
PAYPAL_MODE = 'sandbox'

#ship24
SHIP24_API_KEY = ''
SHIP24_WEBHOOK_SECRET = ''
SHIP24_WEBHOOK_URL = 'https://solid-steels.com/shipping/webhook/ship24/' 

#ngrok pruebas
CSRF_TRUSTED_ORIGINS = [
    'https://solid-steels.com/', 
]
CSRF_COOKIE_SECURE = False