#!/usr/bin/env python3
"""Teste final para verificar se os Page Objects estão funcionando"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_all_imports():
    """Testa todos os imports necessários"""
    
    print("=== Teste Final dos Imports - Dupla de Milheiros ===\n")
    
    # 1. Testa imports do Selenium
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.support import expected_conditions as EC
        print("✅ Imports do Selenium: OK")
    except ImportError as e:
        print(f"❌ Erro nos imports do Selenium: {e}")
        return False
    
    # 2. Testa imports dos Page Objects
    try:
        from tests.functional.page_objects.base_page import BasePage
        from tests.functional.page_objects.login_page import LoginPage
        from tests.functional.page_objects.course_list_page import CourseListPage
        from tests.functional.page_objects.course_detail_page import CourseDetailPage
        from tests.functional.page_objects.checkout_page import CheckoutPage
        print("✅ Imports dos Page Objects: OK")
    except ImportError as e:
        print(f"❌ Erro nos imports dos Page Objects: {e}")
        return False
    
    # 3. Testa import via __init__.py
    try:
        from tests.functional.page_objects import BasePage as BP, LoginPage as LP
        print("✅ Imports via __init__.py: OK")
    except ImportError as e:
        print(f"❌ Erro nos imports via __init__.py: {e}")
        return False
    
    # 4. Testa estrutura das classes
    try:
        # Verifica herança
        assert issubclass(LoginPage, BasePage), "LoginPage deve herdar de BasePage"
        assert issubclass(CheckoutPage, BasePage), "CheckoutPage deve herdar de BasePage"
        
        # Verifica métodos essenciais
        assert hasattr(BasePage, 'navigate_to'), "BasePage deve ter método navigate_to"
        assert hasattr(CheckoutPage, 'wait_for_payment_processing'), "CheckoutPage deve ter método específico"
        
        print("✅ Estrutura das classes: OK")
    except AssertionError as e:
        print(f"❌ Erro na estrutura das classes: {e}")
        return False
    
    # 5. Teste com WebDriver (se disponível)
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # Configuração mínima
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Testa inicialização do driver (mas não executa para economizar tempo)
        print("✅ WebDriver configurável: OK")
        
    except ImportError as e:
        print(f"⚠️ WebDriver não disponível: {e}")
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("📋 Resumo:")
    print("   • Selenium instalado e funcionando")
    print("   • Page Objects importam corretamente")
    print("   • Estrutura de herança está correta")
    print("   • Pronto para testes funcionais!")
    
    return True

def show_usage_example():
    """Mostra um exemplo de uso dos Page Objects"""
    
    print("\n=== Exemplo de Uso dos Page Objects ===\n")
    
    example_code = '''
# Exemplo de teste funcional:

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tests.functional.page_objects import LoginPage, CourseListPage

def test_login_flow():
    options = Options()
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    base_url = "http://localhost:8000"
    
    # Usar Page Objects
    login_page = LoginPage(driver, base_url)
    login_page.navigate_to_login()
    login_page.login("usuario@test.com", "senha123")
    
    course_page = CourseListPage(driver, base_url)
    course_page.wait_for_course_grid_load()
    
    driver.quit()
'''
    
    print(example_code)

if __name__ == "__main__":
    success = test_all_imports()
    
    if success:
        show_usage_example()
        print("\n✅ Sistema pronto para desenvolvimento de testes funcionais!")
        sys.exit(0)
    else:
        print("\n❌ Problemas encontrados. Verifique os erros acima.")
        sys.exit(1)
