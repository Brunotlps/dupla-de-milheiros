from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from products.models import Course, Module, Lesson, CheckoutSession, Purchases, PaymentSettings, ComplementaryMaterial
from products.forms import PaymentMethodForm



class CourseModelTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            description="This is a unit test course.",
            price=100.00,
            active=True,
        )

        # Testando a relação de módulos e aulas
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

    def test_course_creation(self):
        self.assertEqual(self.course.title, "Test Course")
        self.assertEqual(self.course.slug, "test-course")
        self.assertEqual(self.course.price, 100.00)
        self.assertTrue(self.course.active)

    def test_course_str_method(self):
        self.assertEqual(str(self.course), "Test Course")
    
    def test_course_module_relationship(self):
        self.assertEqual(self.course.modules.count(), 1)
        self.assertEqual(self.course.modules.first(), self.module)
    
    def test_module_lesson_relationship(self):
        self.assertEqual(self.module.lessons.count(), 1)
        self.assertEqual(self.module.lessons.first(), self.lesson)

class CheckoutSessionModelTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            description="This is a unit test course.",
            price=100.00,
            active=True,
        )

        self.valid_session = CheckoutSession.objects.create(
            session_id="expired-session-id",
            course=self.course,
            expires_at=timezone.now() + timedelta(hours=1)
        )

        self.expired_session = CheckoutSession.objects.create(
            session_id="expired-session-id",
            course=self.course,
            expires_at=timezone.now() - timedelta(hours=1)
        )

    def test_checkout_session_creation(self):
        self.assertEqual(self.valid_session.course, self.course)
        self.assertEqual(self.valid_session.session_id, "valid-session-id")

    def test_is_expired_method(self):
        self.assertFalse(self.valid_session.is_expired())
        self.assertTrue(self.expired_session.is_expired())

    
class PurchaseModelTest(TestCase):
    def setUp(self):
        # Cria um usuário para testar as compras
        self.user = User.objects.create_user(
            username='student', 
            email="student@example.com",
            password='123'
            )
        self.course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            description="This is a unit test course.",
            price=100.00,
            active=True,
        )
        self.purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status="approved",
            transaction_code="test-transaction-code"
        )
    
    def test_purchase_creation(self):
        self.assertEqual(self.purchase.user, self.user)
        self.assertEqual(self.purchase.course, self.course)
        self.assertEqual(self.purchase.value, 100.00)
        self.assertEqual(self.purchase.status, "approved")
        self.assertEqual(self.purchase.transaction_code, "test-transaction-code")

    def test_purchase_str_method(self):
        expected_str = f"{self.user.username} - {self.course.title}"
        self.assertEqual(str(self.purchase), expected_str)

    def test_is_approved(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='approved',
        )
        self.assertTrue(purchase.is_approved())

    def test_is_pending(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='pending',
        )
        self.assertTrue(purchase.is_pending())
    
    def test_is_rejected(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='rejected',
        )
        self.assertTrue(purchase.is_rejected())
    
    def test_is_canceled(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='canceled',
        )
        self.assertTrue(purchase.is_canceled())
    
    def test_is_in_process(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='in_process',
        )
        self.assertTrue(purchase.is_in_process())

    def test_is_refunded(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='refunded',
        )
        self.assertTrue(purchase.is_refunded())
    
    def test_is_in_mediation(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='in_mediation',
        )
        self.assertTrue(purchase.is_in_mediation())
     
    def test_is_charged_back(self):
       purchase = Purchases.objects.create(
           user=self.user,
           course=self.course,
           value=100.00,
           status='charged_back',
       )
       self.assertTrue(purchase.is_charged_back())
    
    def test_get_status_display_class(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='approved',
        )
        self.assertEqual(purchase.get_status_display(), 'Aprovado')
    
    def get_status_display_class(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='approved',
        )
        self.assertEqual(purchase.get_status_display_class(), 'success')

    
    def test_get_payment_method_display(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=100.00,
            status='approved',
            payment_method='credit_card',
        )
        self.assertEqual(purchase.get_payment_method_display(), 'Cartão de Crédito')
    
    def test_unique_purchase_per_user_course(self):
        Purchases.objects.create(user=self.user, course=self.course, value=100)
        with self.assertRaises(IntegrityError):
            Purchases.objects.create(user=self.user, course=self.course, value=100)
    

class PaymentSettingsModelTest(TestCase):
    def setUp(self):
        self.active_settings = PaymentSettings.objects.create(
            is_active=True,
            is_sandbox=True,
            sandbox_public_key="TEST-public-key",
            sandbox_access_token="TEST-access-token",
            production_public_key="PROD-public-key",
            production_access_token="PROD-access-token"
        )

        self.inactive_settings = PaymentSettings.objects.create(
            is_active=False,
            is_sandbox=False,
            sandbox_public_key="TEST-public-key-2",
            sandbox_access_token="TEST-access-token-2",
            production_public_key="PROD-public-key-2",
            production_access_token="PROD-access-token-2"
        )

    def test_get_active_settings(self):
        settings = PaymentSettings.get_active_settings()
        self.assertEqual(settings, self.active_settings)
        self.assertNotEqual(settings, self.inactive_settings)
    

class PaymentMethodFormTest(TestCase):
    def test_payment_method_form_valid(self):
        form_data = {
            'payment_method': 'credit_card',
            'card_number': '4111111111111111',
            'card_expiration': '12/25',
            'card_cvv': '123'
        }
        form = PaymentMethodForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_payment_method_form_invalid(self):
        form_data = {
            'payment_method': '',
            'card_number': '',
            'card_expiration': '',
            'card_cvv': ''
        }
        form = PaymentMethodForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('payment_method', form.errors)
        self.assertIn('card_number', form.errors)
        self.assertIn('card_expiration', form.errors)
        self.assertIn('card_cvv', form.errors)  

    def test_payment_method_form_invalid_card_number(self):
        form_data = {
            'payment_method': 'credit_card',
            'card_number': '1234',
            'card_expiration': '12/25',
            'card_cvv': '123'
        }
        form = PaymentMethodForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('card_number', form.errors)
    
    def test_payment_method_form_invalid_card_expiration(self):
        form_data = {
            'payment_method': 'credit_card',
            'card_number': '4111111111111111',
            'card_expiration': '12/20',  # Expired date
            'card_cvv': '123'
        }
        form = PaymentMethodForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('card_expiration', form.errors)
    
    def test_payment_method_form_invalid_card_cvv(self):
        form_data = {
            'payment_method': 'credit_card',
            'card_number': '4111111111111111',
            'card_expiration': '12/25',
            'card_cvv': '12'  # CVV should be 3 or 4 digits
        }
        form = PaymentMethodForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('card_cvv', form.errors)

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
            material.clean()
    
    def test_clean_requires_link_for_type(self):
        material = ComplementaryMaterial(
            lesson=self.lesson,
            title="Test Material",
            tipo="link",
            file=None,
            link=""
        )
        with self.assertRaises(ValidationError):
            material.clean()