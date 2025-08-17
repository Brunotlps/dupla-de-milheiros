#!/usr/bin/env python3
"""Teste completo da estrutura dos Page Objects - Dupla de Milheiros"""

import unittest
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class TestPageObjectsStructure(unittest.TestCase):
    """Testa a estrutura e imports dos Page Objects"""
    
    def test_imports_selenium(self):
        """Testa se todos os imports do Selenium funcionam"""
        print("\n🔧 Testando imports do Selenium...")
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.common.exceptions import TimeoutException
            from selenium.webdriver.support import expected_conditions as EC
            print("✅ Imports do Selenium: OK")
        except ImportError as e:
            self.fail(f"Falha nos imports do Selenium: {e}")
    
    def test_imports_page_objects_individual(self):
        """Testa imports individuais dos Page Objects"""
        print("\n📦 Testando imports individuais dos Page Objects...")
        
        # Testa cada Page Object individualmente
        try:
            from tests.functional.page_objects.base_page import BasePage
            print("✅ BasePage importado")
        except ImportError as e:
            self.fail(f"Falha ao importar BasePage: {e}")
        
        try:
            from tests.functional.page_objects.login_page import LoginPage
            print("✅ LoginPage importado")
        except ImportError as e:
            self.fail(f"Falha ao importar LoginPage: {e}")
        
        try:
            from tests.functional.page_objects.course_list_page import CourseListPage
            print("✅ CourseListPage importado")
        except ImportError as e:
            self.fail(f"Falha ao importar CourseListPage: {e}")
        
        try:
            from tests.functional.page_objects.course_detail_page import CourseDetailPage
            print("✅ CourseDetailPage importado")
        except ImportError as e:
            self.fail(f"Falha ao importar CourseDetailPage: {e}")
        
        try:
            from tests.functional.page_objects.checkout_page import CheckoutPage
            print("✅ CheckoutPage importado")
        except ImportError as e:
            self.fail(f"Falha ao importar CheckoutPage: {e}")
    
    def test_imports_via_init(self):
        """Testa imports através do __init__.py"""
        print("\n📦 Testando imports via __init__.py...")
        
        try:
            from tests.functional.page_objects import (
                BasePage,
                LoginPage,
                CourseListPage,
                CourseDetailPage,
                CheckoutPage
            )
            print("✅ Imports via __init__.py: OK")
        except ImportError as e:
            self.fail(f"Falha nos imports via __init__.py: {e}")
    
    def test_class_inheritance(self):
        """Testa se a herança das classes está correta"""
        print("\n🔗 Testando herança das classes...")
        
        from tests.functional.page_objects import (
            BasePage,
            LoginPage,
            CourseListPage,
            CourseDetailPage,
            CheckoutPage
        )
        
        # Verifica herança
        self.assertTrue(issubclass(LoginPage, BasePage), "LoginPage deve herdar de BasePage")
        self.assertTrue(issubclass(CourseListPage, BasePage), "CourseListPage deve herdar de BasePage")
        self.assertTrue(issubclass(CourseDetailPage, BasePage), "CourseDetailPage deve herdar de BasePage")
        self.assertTrue(issubclass(CheckoutPage, BasePage), "CheckoutPage deve herdar de BasePage")
        
        print("✅ Herança das classes: OK")
    
    def test_base_page_methods(self):
        """Testa se BasePage tem os métodos essenciais"""
        print("\n🔧 Testando métodos do BasePage...")
        
        from tests.functional.page_objects.base_page import BasePage
        
        # Métodos essenciais
        essential_methods = [
            'navigate_to',
            'wait_for_page_load',
            'find_element',
            'click_element',
            'send_keys_to_element',
            'get_text',
            'is_element_present',
            'wait_for_url_contains'
        ]
        
        for method in essential_methods:
            self.assertTrue(hasattr(BasePage, method), f"BasePage deve ter o método {method}")
            print(f"✅ Método {method}: OK")
    
    def test_page_objects_methods(self):
        """Testa se cada Page Object tem seus métodos específicos"""
        print("\n🎯 Testando métodos específicos dos Page Objects...")
        
        from tests.functional.page_objects import (
            LoginPage,
            CourseListPage,
            CourseDetailPage,
            CheckoutPage
        )
        
        # LoginPage
        login_methods = ['navigate_to_login', 'login', 'logout']
        for method in login_methods:
            self.assertTrue(hasattr(LoginPage, method), f"LoginPage deve ter o método {method}")
            print(f"✅ LoginPage.{method}: OK")
        
        # CourseListPage
        course_list_methods = ['navigate_to_course_list', 'wait_for_course_grid_load', 'get_course_count']
        for method in course_list_methods:
            self.assertTrue(hasattr(CourseListPage, method), f"CourseListPage deve ter o método {method}")
            print(f"✅ CourseListPage.{method}: OK")
        
        # CourseDetailPage
        course_detail_methods = ['get_course_title', 'get_course_price', 'click_buy_button']
        for method in course_detail_methods:
            self.assertTrue(hasattr(CourseDetailPage, method), f"CourseDetailPage deve ter o método {method}")
            print(f"✅ CourseDetailPage.{method}: OK")
        
        # CheckoutPage
        checkout_methods = ['navigate_to_checkout_start', 'wait_for_payment_processing', 'is_payment_successful']
        for method in checkout_methods:
            self.assertTrue(hasattr(CheckoutPage, method), f"CheckoutPage deve ter o método {method}")
            print(f"✅ CheckoutPage.{method}: OK")


class TestSeleniumIntegration(unittest.TestCase):
    """Testa integração com Selenium WebDriver"""
    
    @classmethod
    def setUpClass(cls):
        """Configura o WebDriver para os testes"""
        print("\n🔧 Configurando WebDriver para testes...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)
        
        print("✅ WebDriver configurado")
    
    @classmethod
    def tearDownClass(cls):
        """Fecha o WebDriver"""
        cls.driver.quit()
        print("✅ WebDriver fechado")
    
    def test_base_page_initialization(self):
        """Testa se BasePage pode ser inicializado com WebDriver"""
        print("\n🏗️ Testando inicialização do BasePage...")
        
        from tests.functional.page_objects.base_page import BasePage
        
        base_page = BasePage(self.driver, "https://www.google.com")
        self.assertIsNotNone(base_page)
        self.assertEqual(base_page.driver, self.driver)
        self.assertEqual(base_page.base_url, "https://www.google.com")
        
        print("✅ BasePage inicializado com sucesso")
    
    def test_page_objects_initialization(self):
        """Testa se todos os Page Objects podem ser inicializados"""
        print("\n🏗️ Testando inicialização dos Page Objects...")
        
        from tests.functional.page_objects import (
            LoginPage,
            CourseListPage,
            CourseDetailPage,
            CheckoutPage
        )
        
        base_url = "http://localhost:8000"
        
        # Testa cada Page Object
        login_page = LoginPage(self.driver, base_url)
        self.assertIsNotNone(login_page)
        print("✅ LoginPage inicializado")
        
        course_list_page = CourseListPage(self.driver, base_url)
        self.assertIsNotNone(course_list_page)
        print("✅ CourseListPage inicializado")
        
        course_detail_page = CourseDetailPage(self.driver, base_url)
        self.assertIsNotNone(course_detail_page)
        print("✅ CourseDetailPage inicializado")
        
        checkout_page = CheckoutPage(self.driver, base_url)
        self.assertIsNotNone(checkout_page)
        print("✅ CheckoutPage inicializado")
    
    def test_navigation_functionality(self):
        """Testa funcionalidade básica de navegação"""
        print("\n🌐 Testando navegação básica...")
        
        from tests.functional.page_objects.base_page import BasePage
        
        base_page = BasePage(self.driver, "https://www.google.com")
        
        # Testa navegação
        base_page.navigate_to("")
        
        # Verifica se navegou corretamente
        current_url = self.driver.current_url
        self.assertIn("google.com", current_url)
        
        print(f"✅ Navegação funcionando: {current_url}")


def run_all_tests():
    """Executa todos os testes e mostra um resumo"""
    
    print("=" * 70)
    print("🧪 EXECUTANDO TESTES COMPLETOS DOS PAGE OBJECTS")
    print("=" * 70)
    
    # Cria suite de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adiciona testes de estrutura
    suite.addTests(loader.loadTestsFromTestCase(TestPageObjectsStructure))
    
    # Adiciona testes de integração com Selenium
    suite.addTests(loader.loadTestsFromTestCase(TestSeleniumIntegration))
    
    # Executa os testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostra resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success = total_tests - failures - errors
    
    print(f"✅ Sucessos: {success}/{total_tests}")
    print(f"❌ Falhas: {failures}")
    print(f"🚫 Erros: {errors}")
    
    if result.wasSuccessful():
        print("\n🎉 TODOS OS TESTES PASSARAM! A estrutura está pronta para uso.")
        return True
    else:
        print("\n❌ Alguns testes falharam. Verifique os detalhes acima.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
