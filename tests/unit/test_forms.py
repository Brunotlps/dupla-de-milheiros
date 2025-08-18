from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from products.models import Course, Module, Lesson, CheckoutSession, Purchases, PaymentSettings, ComplementaryMaterial
from products.forms import PaymentMethodForm



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
            'payment_method': 'credit_card',
            'card_number': '',
            'card_expiration': '',
            'card_cvv': ''
        }
        form = PaymentMethodForm(data=form_data)
        self.assertFalse(form.is_valid())
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
