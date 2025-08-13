# Centralizar a lógica de como obter as credenciais corretas do Mercado Pago 
# Inicializar o SDK 'mercadopago' para comunicar a api

import mercadopago
import hmac
import hashlib
import logging
from .models import PaymentSettings

logger = logging.getLogger(__name__)

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


def validate_mp_signature(signature_header, request_body):
    """
    Valida a assinatura do webhook do Mercado Pago para garantir autenticidade.
    
    Args:
        signature_header (str): Cabeçalho X-Signature do webhook
        request_body (bytes): Corpo da requisição do webhook
        
    Returns:
        bool: True se a assinatura for válida, False caso contrário
    """
    if not signature_header:
        logger.warning("Webhook recebido sem cabeçalho X-Signature")
        return False
    
    try:
        # Obtém as configurações ativas do Mercado Pago
        settings = PaymentSettings.get_active_settings()
        
        # Usa o webhook secret do ambiente correto
        if settings.is_sandbox:
            webhook_secret = settings.sandbox_webhook_secret
        else:
            webhook_secret = settings.production_webhook_secret
            
        if not webhook_secret:
            logger.error("Webhook secret não configurado nas definições ativas")
            return False
        
        # Parse do cabeçalho X-Signature
        # Formato: "ts=timestamp,v1=signature"
        signature_parts = {}
        for part in signature_header.split(','):
            if '=' in part:
                key, value = part.strip().split('=', 1)
                signature_parts[key] = value
        
        timestamp = signature_parts.get('ts')
        signature = signature_parts.get('v1')
        
        if not timestamp or not signature:
            logger.warning("Formato inválido do cabeçalho X-Signature")
            return False
        
        # Cria a string para validação
        payload = f"{timestamp}.{request_body.decode('utf-8')}"
        
        # Calcula a assinatura esperada
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compara as assinaturas de forma segura
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.warning(f"Assinatura inválida do webhook. Hash esperado: {expected_signature[:8]}..., Hash recebido: {signature[:8]}...")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Erro ao validar assinatura do webhook: {str(e)}")
        return False