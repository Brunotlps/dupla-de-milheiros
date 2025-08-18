from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from products.models import Course, Module, Lesson, CheckoutSession, Purchases, PaymentSettings, ComplementaryMaterial
from products.forms import PaymentMethodForm



class ComplementaryMaterialModelTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            description="This is a unit test course.",
            price=100.00,
            active=True,
        )

        self.module = Module.objects.create(
            course=self.course,
            title="Introduction Module",
            order=1
        )

        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Introduction Lesson",
            order=1,
            video_url="http://example.com/video.mp4",
            duration=30
        )

    def test_clean_requires_file_for_type(self):
        material = ComplementaryMaterial(
            lesson=self.lesson,
            title="Test Material",
            tipo="file",
            file=None,
            link=""
        )
        with self.assertRaises(ValidationError):
            material.full_clean()
    
    def test_clean_requires_link_for_type(self):
        material = ComplementaryMaterial(
            lesson=self.lesson,
            title="Test Material",
            tipo="link",
            file=None,
            link=""
        )
        with self.assertRaises(ValidationError):
            material.full_clean()