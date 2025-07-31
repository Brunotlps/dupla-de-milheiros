"""
Configurações de desenvolvimento do Django para o projeto Dupla de Milheiros. / Development settings for the Django project Dupla de Milheiros.
"""


from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    # ngrok URLs
]


CSRF_TRUSTED_ORIGINS = [
    # ngrok URLs
    'http://localhost:8000',
]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# Configuração de banco de dados / Database configuration
# Define o banco de dados padrão como SQLite / Defines the default database as SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# https://docs.djangoproject.com/en/5.1/topics/cache/
# Configuração de cache / Cache configuration
# Define o cache padrão como SQLite / Defines the default cache as SQLite
# Isso é útil para desenvolvimento, mas em produção deve ser configurado com um cache mais robusto / This is useful for development, but in production it should be configured with a more robust cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'