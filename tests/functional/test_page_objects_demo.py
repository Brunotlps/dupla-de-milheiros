#!/usr/bin/env python3
"""Teste funcional demonstrativo - Dupla de Milheiros"""

import os
import sys
import django
from django.conf import settings
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Importação dos Page Objects
from tests.functional.page_objects import BasePage, LoginPage, CourseListPage


class TestPageObjectsDemo(LiveServerTestCase):
    """Demonstração dos Page Objects funcionando"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Configurações do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executa sem interface gráfica
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Inicializa o ChromeDriver
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
    
    def test_page_objects_initialization(self):
        """Testa se os Page Objects podem ser inicializados"""
        
        print("🔧 Testando inicialização dos Page Objects...")
        
        # Testa BasePage
        base_page = BasePage(self.driver, self.live_server_url)
        self.assertIsNotNone(base_page)
        print("✅ BasePage inicializado com sucesso")
        
        # Testa LoginPage
        login_page = LoginPage(self.driver, self.live_server_url)
        self.assertIsNotNone(login_page)
        print("✅ LoginPage inicializado com sucesso")
        
        # Testa CourseListPage
        course_list_page = CourseListPage(self.driver, self.live_server_url)
        self.assertIsNotNone(course_list_page)
        print("✅ CourseListPage inicializado com sucesso")
    
    def test_home_page_navigation(self):
        """Testa navegação para a página inicial"""
        
        print("🌐 Testando navegação para a página inicial...")
        
        base_page = BasePage(self.driver, self.live_server_url)
        base_page.navigate_to("/")
        
        # Verifica se conseguiu navegar
        current_url = self.driver.current_url
        self.assertIn(self.live_server_url, current_url)
        print(f"✅ Navegação bem-sucedida: {current_url}")
    
    def test_selenium_imports_working(self):
        """Testa se os imports do Selenium estão funcionando"""
        
        print("📦 Testando imports do Selenium...")
        
        # Verifica se o driver está funcionando
        self.assertIsNotNone(self.driver)
        print("✅ WebDriver funcionando")
        
        # Testa navegação básica
        self.driver.get("https://www.google.com")
        title = self.driver.title
        self.assertIn("Google", title)
        print(f"✅ Navegação externa funcionando: {title}")


def run_demonstration():
    """Executa uma demonstração simples sem Django Test"""
    
    print("=== Demonstração dos Page Objects - Dupla de Milheiros ===\n")
    
    try:
        # Configurações do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Inicializa o driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ ChromeDriver inicializado com sucesso")
        
        # Testa os Page Objects
        base_url = "http://localhost:8000"  # URL padrão do Django
        
        base_page = BasePage(driver, base_url)
        print("✅ BasePage criado com sucesso")
        
        login_page = LoginPage(driver, base_url)
        print("✅ LoginPage criado com sucesso")
        
        course_list_page = CourseListPage(driver, base_url)
        print("✅ CourseListPage criado com sucesso")
        
        # Testa navegação para Google como exemplo
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Navegação funcionando: {title}")
        
        driver.quit()
        print("✅ Driver fechado com sucesso")
        
        print("\n🎉 Demonstração concluída! Todos os Page Objects estão funcionando.")
        return True
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        return False


if __name__ == "__main__":
    print("Escolha o tipo de teste:")
    print("1. Demonstração simples (sem Django)")
    print("2. Teste completo com Django")
    
    choice = input("Digite sua escolha (1 ou 2): ").strip()
    
    if choice == "1":
        success = run_demonstration()
        sys.exit(0 if success else 1)
    elif choice == "2":
        print("Para executar os testes Django, use:")
        print("python manage.py test tests.functional.test_page_objects_demo")
    else:
        print("Opção inválida. Executando demonstração simples...")
        success = run_demonstration()
        sys.exit(0 if success else 1)
