from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Course, Purchases

class CourseViewsTest(TestCase):
    def setUp(self):
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
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/checkout.html')
        self.assertContains(response, self.course.title)

        