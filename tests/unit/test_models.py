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
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='123'
        )

        self.course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            description="This is a unit test course.",
            price=100.00,
            active=True,
        )

        self.valid_session = CheckoutSession.objects.create(
            user=self.user,
            session_id="valid-session-id",
            course=self.course,
            expires_at=timezone.now() + timedelta(hours=1)
        )

        self.expired_session = CheckoutSession.objects.create(
            user=self.user,
            session_id="expired-session-id",
            course=self.course,
            expires_at=timezone.now() - timedelta(hours=1)
        )

    def test_checkout_session_creation(self):
        self.assertEqual(self.valid_session.user.username, "test_user")
        self.assertEqual(self.valid_session.course, self.course)
        self.assertIsNotNone(self.valid_session.session_id)
        

    def test_is_expired_method(self):
        self.assertFalse(self.valid_session.is_expired())

        expired_session = CheckoutSession.objects.create(
            user=self.user,
            course=self.course,
        )

        expired_session.expires_at = timezone.now() - timedelta(hours=1)
        expired_session.save(update_fields=['expires_at'])

        self.assertTrue(expired_session.is_expired())

    
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
        new_user = User.objects.create_user(username='student_approved', password='123')
        new_course = Course.objects.create(title="Course Approved", slug="course-approved", price=50.00)
        
        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='approved',
        )
        self.assertTrue(purchase.is_approved())

    def test_is_pending(self):
        new_user = User.objects.create_user(username='student_pending', password='123')
        new_course = Course.objects.create(title="Course Pendig", slug="course-pending", price=50.00)
        
        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='pending',
        )
        self.assertTrue(purchase.is_pending())
    
    def test_is_rejected(self):
        new_user = User.objects.create_user(username='student_rejected', password='123')
        new_course = Course.objects.create(title="Course rejected", slug="course-rejected", price=50.00)

        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='rejected',
        )
        self.assertTrue(purchase.is_rejected())
    
    def test_is_canceled(self):
        new_user = User.objects.create_user(username='student_canceled', password='123')
        new_course = Course.objects.create(title="Course canceled", slug="course-canceled", price=50.00)

        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='canceled',
        )
        self.assertTrue(purchase.is_canceled())
    
    def test_is_in_process(self):
        new_user = User.objects.create_user(username='student_process', password='123')
        new_course = Course.objects.create(title="Course process", slug="course-process", price=50.00)

        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='in_process',
        )
        self.assertTrue(purchase.is_in_process())

    def test_is_refunded(self):
        new_user = User.objects.create_user(username='student_refunded', password='123')
        new_course = Course.objects.create(title="Course refunded", slug="course-refunded", price=50.00)

        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='refunded',
        )
        self.assertTrue(purchase.is_refunded())
    
    def test_is_in_mediation(self):
        new_user = User.objects.create_user(username='student_mediation', password='123')
        new_course = Course.objects.create(title="Course mediation", slug="course-mediation", price=50.00)

        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='in_mediation',
        )
        self.assertTrue(purchase.is_in_mediation())
     
    def test_is_charged_back(self):
       new_user = User.objects.create_user(username='student_charged_back', password='123')
       new_course = Course.objects.create(title="Course charged back", slug="course-charged-back", price=50.00)
       
       purchase = Purchases.objects.create(
           user=new_user,
           course=new_course,
           value=100.00,
           status='charged_back',
       )
       self.assertTrue(purchase.is_charged_back())
    
    def test_get_status_display_class(self):
        new_user = User.objects.create_user(username='student_status', password='123')
        new_course = Course.objects.create(title="Course Status", slug="course-status", price=100.00)

        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='approved',
        )
        self.assertEqual(purchase.get_status_display_class(), 'success')

    
    def test_get_payment_method_display(self):
        new_user = User.objects.create_user(username='payment_user', password='123')
        new_course = Course.objects.create(title="Payment Course", slug="payment-course", price=100.00)
        
        purchase = Purchases.objects.create(
            user=new_user,
            course=new_course,
            value=100.00,
            status='approved',
            payment_method='credit_card',
        )
        self.assertEqual(purchase.get_payment_method_display(), 'Cartão de Crédito')
    
    def test_unique_purchase_per_user_course(self):
        new_user = User.objects.create_user(username='student2', password='123')
        new_course = Course.objects.create(title="Course 2", slug="course-2", price=50.00)
        # Primeira compra - deve funcionar
        Purchases.objects.create(user=new_user, course=new_course, value=100)
        with self.assertRaises(IntegrityError):
            Purchases.objects.create(user=new_user, course=new_course, value=100)
    

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
   