from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from products.models import Course, Purchases, PaymentSettings


class AuthenticationFlowsTest(TestCase):
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

    
    def test_checkout_requires_login(self):
        
        
        response = self.client.get(reverse('products:checkout_start', args=[self.course.slug]))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("products:checkout_start", args=[self.course.slug])}')
        self.assertEqual(response.status_code, 302)
    
    