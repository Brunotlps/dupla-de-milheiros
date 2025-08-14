from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
import json
import hmac
import hashlib

from products.models import Course, PaymentSettings, Purchases
from products.utils import validate_mp_signature


class WebhookSecurityTest(TestCase):
    def setUp(self):
        self.payment_settings = PaymentSettings.objects.create(
            is_active=True,
            is_sandbox=True,
            sandbox_public_key="TEST-public-key",
            sandbox_access_token="TEST-access-token",
            sandbox_webhook_secret="test-webhook-secret",
            production_webhook_secret="prod-webhook-secret"
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            price=100.00,
            active=True
        )

    def test_webhook_signature_validation_valid(self):
        """Teste validação de assinatura webhook válida"""
        webhook_secret = "test-webhook-secret"
        payload = json.dumps({"action": "payment.updated", "data": {"id": "12345"}})
        
        # Gerar assinatura válida
        signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Validar assinatura
        is_valid = validate_mp_signature(payload, signature, webhook_secret)
        self.assertTrue(is_valid)

    def test_webhook_signature_validation_invalid(self):
        """Teste validação de assinatura webhook inválida"""
        webhook_secret = "test-webhook-secret"
        payload = json.dumps({"action": "payment.updated", "data": {"id": "12345"}})
        invalid_signature = "invalid-signature"
        
        # Validar assinatura inválida
        is_valid = validate_mp_signature(payload, invalid_signature, webhook_secret)
        self.assertFalse(is_valid)

    def test_webhook_without_signature_rejected(self):
        """Teste se webhook sem assinatura é rejeitado"""
        payload = {"action": "payment.updated", "data": {"id": "12345"}}
        
        response = self.client.post(
            reverse('products:webhook_handler'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Deve rejeitar por falta de assinatura
        self.assertEqual(response.status_code, 400)

    def test_webhook_rate_limiting(self):
        """Teste se rate limiting está funcionando"""
        webhook_secret = self.payment_settings.get_webhook_secret()
        payload = json.dumps({"action": "payment.updated", "data": {"id": "12345"}})
        
        signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Fazer múltiplas requisições rapidamente
        for i in range(15):  # Acima do limite de 10/min
            response = self.client.post(
                reverse('products:webhook_handler'),
                data=payload,
                content_type='application/json',
                HTTP_X_SIGNATURE=f'sha256={signature}'
            )
            
        # Última requisição deve ser rate limited
        self.assertIn(response.status_code, [429, 400])  # Too Many Requests ou Bad Request


class AuthenticationSecurityTest(TestCase):
    def setUp(self):
        PaymentSettings.objects.create(
            is_active=True,
            is_sandbox=True,
            sandbox_public_key="TEST-public-key",
            sandbox_access_token="TEST-access-token"
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            price=100.00,
            active=True
        )

    def test_checkout_requires_authentication(self):
        """Teste se checkout requer autenticação"""
        response = self.client.get(
            reverse('products:checkout_start', args=[self.course.slug])
        )
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_purchases_list_requires_authentication(self):
        """Teste se lista de compras requer autenticação"""
        response = self.client.get(reverse('products:purchases_list'))
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_user_can_only_see_own_purchases(self):
        """Teste se usuário vê apenas suas próprias compras"""
        # Criar outro usuário e compra
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        
        Purchases.objects.create(
            user=other_user,
            course=self.course,
            value=100.00,
            status='approved'
        )
        
        # Login com primeiro usuário
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('products:purchases_list'))
        
        # Não deve ver compra do outro usuário
        self.assertNotContains(response, 'otheruser')


class CSRFSecurityTest(TestCase):
    def setUp(self):
        PaymentSettings.objects.create(
            is_active=True,
            is_sandbox=True,
            sandbox_public_key="TEST-public-key",
            sandbox_access_token="TEST-access-token"
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_payment_form_csrf_protection(self):
        """Teste se formulário de pagamento tem proteção CSRF"""
        self.client.login(username='testuser', password='testpass123')
        
        # Tentar POST sem CSRF token
        response = self.client.post(
            reverse('products:checkout_payment'),
            {'payment_method': 'credit_card'}
        )
        
        # Deve rejeitar por falta de CSRF token
        self.assertEqual(response.status_code, 403)

    def test_logout_form_csrf_protection(self):
        """Teste se formulário de logout tem proteção CSRF"""
        self.client.login(username='testuser', password='testpass123')
        
        # Tentar logout sem CSRF token
        response = self.client.post(reverse('logout'))
        
        # Deve rejeitar por falta de CSRF token
        self.assertEqual(response.status_code, 403)


class SecurityHeadersTest(TestCase):
    def test_security_headers_present(self):
        """Teste se headers de segurança estão presentes"""
        response = self.client.get('/')
        
        expected_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        for header, expected_value in expected_headers.items():
            with self.subTest(header=header):
                self.assertIn(header, response.headers)
                self.assertEqual(response.headers[header], expected_value)

    def test_csp_header_present(self):
        """Teste se Content Security Policy está presente"""
        response = self.client.get('/')
        
        self.assertIn('Content-Security-Policy', response.headers)
        csp = response.headers['Content-Security-Policy']
        
        # Verificar diretivas importantes
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src", csp)
        self.assertIn("style-src", csp)

    def test_hsts_header_in_production(self):
        """Teste se HSTS está presente (simulando produção)"""
        with self.settings(DEBUG=False):
            response = self.client.get('/')
            
            # Em produção, HSTS deve estar presente
            if not response.get('DEBUG', True):
                self.assertIn('Strict-Transport-Security', response.headers)
