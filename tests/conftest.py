"""Configurações pytest para o projeto Dupla de Milheiros. / Pytest configurations for the Dupla de Milheiros project."""


import pytest

from django.contrib.auth.models import User

from products.models import Course, PaymentSettings

@pytest.fixture
def test_user():


    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_course():
    

    return Course.objects.create(
        title="Curso de Milhas Teste",
        slug="curso-milhas-teste",
        description="Descrição do curso de milhas para testes.",
        price=199.99,
        active=True
    )


@pytest.fixture
def payment_settings():
    

    return PaymentSettings.objects.create(
        is_active=True,
        is_sandbox=True,
        sandbox_public_key="TEST-public-key",
        sandbox_access_token="TEST-access-token"
    )


