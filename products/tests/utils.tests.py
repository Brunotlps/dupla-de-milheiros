from django.test import TestCase
from unittest.mock import patch, MagicMock
from products.utils import get_mercadopago_sdk, get_mercadopago_public_key
from products.models import PaymentSettings

class MercadoPagoUtilsTest(TestCase):
    def setUp(self):
        self.payment_settings = PaymentSettings.objects.create(
            is_active=True,
            is_sandbox=True,
            sandbox_public_key = "TEST-public-key",
            sandbox_access_token = "TEST-access-token",
            production_public_key = "PROD-public-key",
            production_access_token = "PROD-access-token"
        )

    def test_get_mercadopago_public_key_sandbox(self):
        with patch('products.utils.PaymentSettings.get_active_settings', return_value=self.payment_settings):
            public_key = get_mercadopago_public_key()
            self.assertEqual(public_key, "TEST-public-key")

            self.payment_settings.is_sandbox = False
            self.payment_settings.save()

            public_key = get_mercadopago_public_key()
            self.assertEqual(public_key, "PROD-public-key")
    
    @patch('products.models.PaymentSettings.get_active_settings')
    def test_get_mercadopago_public_key_production(self,mock_get_active_settings):
        # Configura o mock para retornar as configurações de produção
        pass

    @patch('mercadopago.SDK')
    def test_get_mercadopago_sdk_sandbox(self, mock_sdk):
        # Configurando o mock
        mock_instance = MagicMock()
        mock_sdk.return_value = mock_instance

        # Testar obtenção do SDK em modo sandbox
        sdk = get_mercadopago_sdk()

        # Verifica se o SDK foi chamado com o token de sandbox correto
        mock_sdk.assert_called_once_with("TEST-access-token")
        self.assertEqual(sdk, mock_instance)
    
    @patch('mercadopago.SDK')
    def test_get_mercadopago_sdk_production(self, mock_sdk):
        self.payment_settings.is_sandbox = False
        self.payment_settings.save()

        mock_instance = MagicMock()
        mock_sdk.return_value = mock_instance

        sdk = get_mercadopago_sdk()

        mock_sdk.assert_called_once_with("PROD-access-token")
        self.assertEqual(sdk, mock_instance)
        

    def test_get_mercadopago_sdk_no_token(self):
        self.payment_settings.sandbox_access_token = ""
        self.payment_settings.save()

        with self.assertRaise(ValueError):
            get_mercadopago_sdk()

   