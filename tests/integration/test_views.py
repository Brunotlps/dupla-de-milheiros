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
        """Test course list view displays active courses"""
        # Clear cache to ensure fresh data
        from django.core.cache import cache
        cache.clear()
        
        response = self.client.get(reverse('products:course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/course_list.html')
        self.assertContains(response, self.course.title)

    
    def test_course_detail_view(self):
        
        
        response = self.client.get(reverse('products:course_detail', args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/course_detail.html')
        self.assertContains(response, self.course.title)
    
    
    def test_course_detail_not_found(self):
        
        
        response = self.client.get(reverse('products:course_detail', args=['curso-inexistente']))
        self.assertEqual(response.status_code, 404)