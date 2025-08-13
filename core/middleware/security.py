"""Implementação de headers de segurança conforme boas práticas OWASP e Django. / Implementation of security headers according to OWASP and Django best practices."""


from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
        Middleware que adiciona headers de segurança a todas as respostas HTTP. / Middleware that adds security headers to all HTTP responses.

        Headers implementados / Implemented headers:
        - X-Content-Type-Options: Previne MIME type sniffing / Prevents MIME type sniffing
        - X-Frame-Options: Previne clickjacking / Prevents clickjacking
        - X-XSS-Protection: Proteção contra XSS (browsers legados) / Protection against XSS (legacy browsers)
        - Referrer-Policy: Controla informações de referrer / Controls referrer information
        - Permissions-Policy: Controla APIs do browser / Controls browser APIs
        - Strict-Transport-Security: HTTPS obrigatório (só em produção) / HTTPS required (only in production)
    
    """

    def process_response(self, request, response):


        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Desabilita APIs perigosas por padrão / Disables dangerous APIs by default
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'fullscreen=(self), '
            'payment=()'
        )

        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://sdk.mercadopago.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.mercadopago.com; "
                "frame-src https://secure.mlstatic.com;"
            )

        if not settings.DEBUG and request.is_secure():
            response['Strict-Transport-Security'] = ('max-age=31536000; includeSubDomains; preload')
        
        return response

class SecurityWebhookMiddleware(MiddlewareMixin):
    """
        Middleware específico para endpoints de webhooks, incluindo headers adicionais de segurança. / Specific middleware for webhook endpoints, including additional security headers.
    """

    def process_response(self, request, response):

        # Apenas para endpoints de webhook / Only for webhook endpoints
        if '/webhook/' in request.path:
            # Previne caching de webhooks / Prevents caching of webhooks
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Específico para APIs / Specific for APIs
            response['X-Robots-Tag'] = 'noindex, nofollow'

        return response
    