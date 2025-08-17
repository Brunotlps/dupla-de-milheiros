#!/usr/bin/env python3
"""Teste básico dos Page Objects"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

def test_page_objects_import():
    """Testa se todos os Page Objects podem ser importados corretamente"""
    
    try:
        # Testa BasePage
        from tests.functional.page_objects.base_page import BasePage
        print("✅ BasePage importado com sucesso")
        
        # Testa LoginPage
        from tests.functional.page_objects.login_page import LoginPage
        print("✅ LoginPage importado com sucesso")
        
        # Testa CourseListPage
        from tests.functional.page_objects.course_list_page import CourseListPage
        print("✅ CourseListPage importado com sucesso")
        
        # Testa CourseDetailPage
        from tests.functional.page_objects.course_detail_page import CourseDetailPage
        print("✅ CourseDetailPage importado com sucesso")
        
        # Testa CheckoutPage
        from tests.functional.page_objects.checkout_page import CheckoutPage
        print("✅ CheckoutPage importado com sucesso")
        
        print("\n🎉 Todos os Page Objects foram importados com sucesso!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar Page Object: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_page_objects_structure():
    """Testa a estrutura básica dos Page Objects"""
    
    try:
        from tests.functional.page_objects.base_page import BasePage
        from tests.functional.page_objects.checkout_page import CheckoutPage
        
        # Verifica se CheckoutPage herda de BasePage
        if issubclass(CheckoutPage, BasePage):
            print("✅ CheckoutPage herda corretamente de BasePage")
        else:
            print("❌ CheckoutPage não herda de BasePage")
            return False
            
        # Verifica se tem os métodos básicos
        checkout_methods = [
            'navigate_to_checkout_start',
            'get_page_title',
            'is_payment_form_present',
            'wait_for_payment_processing'
        ]
        
        for method in checkout_methods:
            if hasattr(CheckoutPage, method):
                print(f"✅ CheckoutPage tem o método: {method}")
            else:
                print(f"❌ CheckoutPage não tem o método: {method}")
                return False
        
        print("\n🎉 Estrutura dos Page Objects está correta!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste de Imports dos Page Objects ===\n")
    
    import_success = test_page_objects_import()
    
    print("\n=== Teste de Estrutura dos Page Objects ===\n")
    
    structure_success = test_page_objects_structure()
    
    if import_success and structure_success:
        print("\n✅ Todos os testes passaram! Os Page Objects estão prontos para uso.")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)
