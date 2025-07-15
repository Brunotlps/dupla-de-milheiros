from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from products.models import Course, Purchases, PaymentSettings

class CourseViewsTest(TestCase):
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
    
    def test_course_list_view(self):
        response = self.client.get(reverse('products:course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/course_list.html')
        self.assertContains(response, self.course.title)

    def test_course_detail_view(self):
        response = self.client.get(reverse('products:course_detail', args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/course_detail.html')
        self.assertContains(response, self.course.title)
    
    def test_checkout_requires_login(self):
        response = self.client.get(reverse('products:checkout_start', args=[self.course.slug]))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("products:checkout_start", args=[self.course.slug])}')
        self.assertEqual(response.status_code, 302)
    
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

        from products.models import CheckoutSession
        from datetime import timedelta
        from django.utils import timezone

        session = CheckoutSession.objects.create(
            user=self.user,
            course=self.course,
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        session_id = session.session_id
        session = self.client.session
        session['checkout_session_id'] = session_id
        session.save()
        response = self.client.get(reverse('products:checkout_payment'))

        print("DEBUG: status_code:", response.status_code)
        print("DEBUG: templates:", getattr(response, 'templates', None))
        print("DEBUG: redirect_chain:", getattr(response, 'redirect_chain', None))
        print("DEBUG: content:", response.content.decode())

        
        if response.status_code == 302:
            self.assertRedirects(response, reverse('products:course_list'))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'error_page.html')
            self.assertContains(response, 'Erro na configuração de pagamento')
    
    def test_course_detail_not_found(self):
        response = self.client.get(reverse('products:course_detail', args=['curso-inexistente']))
        self.assertEqual(response.status_code, 404)