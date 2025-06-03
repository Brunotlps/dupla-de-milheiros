# Centralizar a lógica de como obter as credenciais corretas do Mercado Pago 
# Inicializar o SDK 'mercadopago' para comunicar a api

import mercadopago
from .models import PaymentSettings

def get_mercadopago_sdk():
    # Busca a configuração de pagamento e se está em modo sandbox no banco de dados 
    settings =PaymentSettings.get_active_settings()

    if settings.is_sandbox:
        access_token = settings.sandbox_access_token
    else:
        access_token = settings.production_access_token

    if not access_token:
        raise ValueError("Access Token do Mercado Pago não configurado nas definições ativas.")
    
    sdk = mercadopago.SDK(access_token)
    return sdk

def get_mercadopago_public_key():
    # A public key é usada para inicializar os componentes visuais do mercado pago (os Bricks) no navegador do utilizador.
    settings = PaymentSettings.get_active_settings()

    if settings.is_sandbox:
        public_key = settings.sandbox_public_key
    else:
        public_key = settings.production_public_key

    if not public_key:
        raise ValueError("Public Key do Mercado Pago não configurada nas definições ativas.")
    
    return public_key