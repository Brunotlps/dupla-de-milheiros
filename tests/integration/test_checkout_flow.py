
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from products.models import Course, Purchases, PaymentSettings


class CheckoutFlowTest(TestCase):
    def setUp(self):
        PaymentSettings.objects.create(
            is_active=True,
            is_sandbox=True,
            sandbox_public_key="TEST-public-key",
            sandbox_access_token="TEST-access-token",
            production_public_key="PROD-public-key",
            production_access_token="PROF-access-token"

        )

        self.user = User.objects.create_user(username='student', password='123')
        self.course = Course.objects.create(
            title="Django Course",
            slug="django-course",
            description="This is a test course.",
            price=200.00,
            active=True,
        )

    
    def test_checkout_authenticated(self):
        
        
        self.client.login(username='student', password='123')
        response = self.client.get(reverse('products:checkout_start', args=[self.course.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('products:checkout_payment'))

        # Simulando o acesso à tela de pagamento
        session = self.client.session
        self.assertIn('checkout_session_id', session)
        response = self.client.get(reverse('products:checkout_payment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/checkout/payment.html')

    def test_authenticated_purchase_flow(self):
        
        
        self.client.login(username='student', password='123')
        response = self.client.get(reverse('products:checkout_start', args=[self.course.slug]))
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, reverse('products:checkout_payment'))

        # Simula o acesso à tela de pagamento
        session = self.client.session
        self.assertIn('checkout_session_id', session)
        response = self.client.get(reverse('products:checkout_payment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/checkout/payment.html')

    def test_duplicate_purchase_not_allowed(self):
        
        
        self.client.login(username='student', password='123')
        Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status="approved"
        )

        response = self.client.get(reverse('products:checkout_start', args=[self.course.slug]))
        self.assertRedirects(response, reverse('products:course_detail', args=[self.course.slug]))
    

    def test_checkout_expired_session(self):
        
        
        self.client.login(username='student', password='123')

        from datetime import timedelta
        from unittest.mock import patch
        from django.utils import timezone
        from products.models import CheckoutSession

        session_expires_at = timezone.now() + timedelta(hours=1)

        session = CheckoutSession.objects.create(
            user=self.user,
            course=self.course,
            expires_at=session_expires_at
        )

        session_id = session.session_id
        client_session = self.client.session
        client_session['checkout_session_id'] = session_id
        client_session.save()

        fake_current_time = session_expires_at + timedelta(hours=1)
        with patch('django.utils.timezone.now', return_value=fake_current_time):
            print(f"DEBUG: Session expires_at: {session.expires_at}")
            print(f"DEBUG: Mocked current time: {fake_current_time}")
            print(f"DEBUG: Is expired: {session.is_expired()}")

            response = self.client.get(reverse('products:checkout_payment'))

            print("DEBUG: status code:", response.status_code)

            self.assertTrue(session.is_expired())
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('products:course_list'))
    
    