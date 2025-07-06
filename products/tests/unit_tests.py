from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Course, Purchases

class CourseModelTest(TestCase):
    def test_course_creation(self):
        # Testa se o curso é criado corretamente e se o slug é gerado automaticamente
        course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            description="This is a unit test course.",
            price=100.00,
            active=True,
        )

        self.assertEqual(course.title, "Test Course")
        self.assertEqual(course.slug, "test-course")
        self.assertTrue(course.active)

class PurchaseModelTest(TestCase):
    def setUp(self):
        # Cria um usuário para testar as compras
        self.user = User.objects.create_user(username='student', password='123')
        self.course = Course.objects.create(
            title="Django Course",
            slug="django-course",
            description="This is a unit test course.",
            price=200.00,
            active=True,
        )

    def test_is_approved(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='approved',
        )
        self.assertTrue(purchase.is_approved())

    def test_is_pending(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='pending',
        )
        self.assertTrue(purchase.is_pending())
    
    def test_is_rejected(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='rejected',
        )
        self.assertTrue(purchase.is_rejected())
    
    def test_is_canceled(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='canceled',
        )
        self.assertTrue(purchase.is_canceled())
    
    def test_is_in_process(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='in_process',
        )
        self.assertTrue(purchase.is_in_process())

    def test_is_refunded(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='refunded',
        )
        self.assertTrue(purchase.is_refunded())
    
    def test_is_in_mediation(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='in_mediation',
        )
        self.assertTrue(purchase.is_in_mediation())
     
    def test_is_charged_back(self):
       purchase = Purchases.objects.create(
           user=self.user,
           course=self.course,
           value=200.00,
           stutus='charged_back',
       )
       self.assertTrue(purchase.is_charged_back())
    
    def test_get_status_display(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='approved',
        )
        self.assertEqual(purchase.get_status_display(), 'Aprovado')
    
    def test_get_payment_method_display(self):
        purchase = Purchases.objects.create(
            user=self.user,
            course=self.course,
            value=200.00,
            stutus='approved',
            payment_method='credit_card',
        )
        self.assertEqual(purchase.get_payment_method_display(), 'Cartão de Crédito')
    
    
    
