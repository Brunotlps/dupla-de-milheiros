#!/usr/bin/env python
"""
Script de teste para verificar a configuração do Vimeo API. / Test script to verify Vimeo API configuration.
Execute: python test_vimeo_setup.py / Execute: python test_vimeo_setup.py
"""

import os

import django

from pathlib import Path

# Configurar Django / Configure Django
project_root = Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()


from core.vimeo_config import test_vimeo_connection


def main():
    
    
    print("🎬 TESTE DE CONFIGURAÇÃO VIMEO API")
    print("=" * 50)
    
    # Verificar variáveis de ambiente / Check environment variables
    print("\n📋 Verificando variáveis de ambiente...")
    
    vimeo_vars = {
        'VIMEO_CLIENT_ID': os.getenv('VIMEO_CLIENT_ID'),
        'VIMEO_CLIENT_SECRET': os.getenv('VIMEO_CLIENT_SECRET'),
        'VIMEO_ACCESS_TOKEN': os.getenv('VIMEO_ACCESS_TOKEN')
    }
    
    missing_vars = []
    for var_name, var_value in vimeo_vars.items():
        if var_value:
            # Mostrar apenas os primeiros caracteres por segurança / Show only the first few characters for security
            masked_value = var_value[:8] + "..." if len(var_value) > 8 else "✅ SET"
            print(f"  ✅ {var_name}: {masked_value}")
        else:
            print(f"  ❌ {var_name}: NOT SET")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n❌ ERRO: As seguintes variáveis não estão configuradas:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Por favor, configure-as no arquivo .env e tente novamente.")
        return False
    
    # Testar conexão com Vimeo / Test Vimeo connection
    print("\n🔌 Testando conexão com Vimeo API...")
    
    try:
        success, result = test_vimeo_connection()
        
        if success:
            print("✅ CONEXÃO SUCESSO!")
            print(f"   👤 Usuário: {result.get('name', 'Unknown')}")
            print(f"   📧 Email: {result.get('email', 'Unknown')}")
            print(f"   🔗 Link: {result.get('link', 'Unknown')}")
            print(f"   📊 Vídeos: {result.get('metadata', {}).get('connections', {}).get('videos', {}).get('total', 0)}")
            return True
        else:
            print("❌ CONEXÃO FALHOU!")
            print(f"   Erro: {result}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False


if __name__ == "__main__":
    if main():
        print("\n🎉 CONFIGURAÇÃO VIMEO COMPLETA E FUNCIONAL!")
        print("   Agora você pode prosseguir com a implementação do sistema de vídeos.")
    else:
        print("\n⚠️  CONFIGURAÇÃO INCOMPLETA")
        print("   Por favor, resolva os problemas acima antes de continuar.")
