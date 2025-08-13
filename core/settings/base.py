"""
Configurações base do Django para o projeto Dupla de Milheiros.
"""

from pathlib import Path

from dotenv import load_dotenv

import os


load_dotenv()

# Build paths 
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Validação crítica / Critical validation
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY not found!\n"
        "Execute: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"\n"
        "Add to your .env"
    )

def validate_production_env():


    """ Valida as configurações do ambiente de produção / Validates the production environment settings."""
    required_vars = [
        'DJANGO_SECRET_KEY',
        'DB_NAME',
        'DB_USER', 
        'DB_PASSWORD',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")


NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Apps organizados por categorias / Apps organized by categories
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = []

LOCAL_APPS = [
    'home',
    'news',
    'products',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middlewares base / Base middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.security.SecurityHeadersMiddleware',
    'core.middleware.security.SecurityWebhookMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL de configuração / URL configuration
# Define o módulo de URLs raiz do projeto
ROOT_URLCONF = 'core.urls'

# Configuração de templates / Template configuration
# Define o backend de templates e diretórios de templates / Defines the template backend and directories
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Configuração de arquivos estáticos / Static files configuration
# Define o URL base para arquivos estáticos / Defines the base URL for static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Configuração de arquivos de mídia / Media files configuration
WSGI_APPLICATION = 'core.wsgi.application'


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

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

# Define o tipo de campo primário padrão como BigAutoField / Defines the default primary key field type as BigAutoField
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração de redirecionamento de login e logout / Login and logout redirection configuration
# Define onde o usuário será redirecionado após o login e logout / Defines where the user will be redirected after login and logout
LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = 'login'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuração de logging / Logging configuration
# Define onde os logs serão armazenados e o nível de log / Defines where logs will be stored and the log level
# Logging mais profissional
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'products.views': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}