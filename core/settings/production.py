"""
Configurações de produção do Django para o projeto Dupla de Milheiros. / Production settings for the Django project Dupla de Milheiros.
"""

from .base import *


DEBUG = False 

# Validação do ambiente de produção / Production environment validation
validate_production_env()

ALLOWED_HOSTS = [
    os.getenv('DJANGO_ALLOWED_HOSTS'),
    # Domínios aqui / Domains here
]

# Configuração de banco de dados, será implementada no deploy / Database configuration, will be implemented on deploy
DATABASES = {
    'default': {
        # Implementar a configuração do banco de dados aqui / Implement the database configuration here
    }
}


# Cache Redis para produção / Redis cache for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}


# Headers de segurança / Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# Configuração de email para produção / Email configuration for production
# Usar SMTP com variáveis de ambiente / Use SMTP with environment variables
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')


# Configuração de arquivos estáticos / Static files configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Headers HSTS adicionais / Additional HSTS headers
SECURE_HSTS_SECONDS = 31536000  # 1 ano / 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
