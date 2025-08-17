#!/usr/bin/env python3
"""Teste funcional demonstrativo com Django - Dupla de Milheiros"""

import os
import sys
import django
from django.conf import settings
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuração do Django para testes standalone
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from tests.functional.page_objects import BasePage, LoginPage, CourseListPage


class TestDjangoFunctional(LiveServerTestCase):
    """Teste funcional demonstrativo usando Django LiveServerTestCase"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Configurações do Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Para CI/CD
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Inicializa o WebDriver
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)
        
        print(f"🌐 Servidor de teste iniciado em: {cls.live_server_url}")
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
        print("✅ WebDriver fechado")
    
    def setUp(self):
        """Cria dados de teste para cada teste"""
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"👤 Usuário de teste criado: {self.test_user.username}")
    
    def test_home_page_access(self):
        """Testa acesso à página inicial"""
        print("\n🏠 Testando acesso à página inicial...")
        
        base_page = BasePage(self.driver, self.live_server_url)
        base_page.navigate_to("/")
        
        # Verifica se conseguiu navegar
        current_url = self.driver.current_url
        self.assertIn(self.live_server_url, current_url)
        
        # Verifica se a página carregou (título)
        page_title = self.driver.title
        self.assertIsNotNone(page_title)
        
        print(f"✅ Página inicial acessada: {current_url}")
        print(f"✅ Título da página: {page_title}")
    
    def test_login_page_structure(self):
        """Testa se a página de login tem a estrutura correta"""
        print("\n🔐 Testando estrutura da página de login...")
        
        login_page = LoginPage(self.driver, self.live_server_url)
        login_page.navigate_to_login()
        
        # Verifica se está na página de login
        current_url = self.driver.current_url
        self.assertIn("/accounts/login/", current_url)
        
        # Verifica se o formulário de login está presente
        form_present = login_page.is_login_form_present()
        self.assertTrue(form_present, "Formulário de login deve estar presente")
        
        print("✅ Página de login carregada corretamente")
        print("✅ Formulário de login presente")
    
    def test_course_list_page(self):
        """Testa navegação para a lista de cursos"""
        print("\n📚 Testando página de lista de cursos...")
        
        course_list_page = CourseListPage(self.driver, self.live_server_url)
        course_list_page.navigate_to_course_list()
        
        # Verifica se está na página correta
        current_url = self.driver.current_url
        self.assertIn("/products/cursos/", current_url)
        
        # Verifica se o grid de cursos ou mensagem de "sem cursos" está presente
        course_list_page.wait_for_course_grid_load()
        
        # Pode ter cursos ou não, mas uma das duas condições deve ser verdadeira
        has_courses_grid = course_list_page.is_courses_grid_present()
        has_no_courses_msg = course_list_page.is_no_courses_message_present()
        
        self.assertTrue(
            has_courses_grid or has_no_courses_msg,
            "Deve ter grid de cursos OU mensagem de 'sem cursos'"
        )
        
        print("✅ Página de cursos carregada corretamente")
        
        if has_courses_grid:
            course_count = course_list_page.get_course_count()
            print(f"✅ Grid de cursos presente ({course_count} cursos)")
        else:
            print("✅ Mensagem 'sem cursos' presente")
    
    def test_page_objects_integration(self):
        """Testa integração entre diferentes Page Objects"""
        print("\n🔗 Testando integração entre Page Objects...")
        
        # Navega pela sequência: Home -> Login -> Cursos
        
        # 1. Página inicial
        base_page = BasePage(self.driver, self.live_server_url)
        base_page.navigate_to("/")
        print("✅ Navegou para página inicial")
        
        # 2. Página de login
        login_page = LoginPage(self.driver, self.live_server_url)
        login_page.navigate_to_login()
        self.assertIn("/accounts/login/", self.driver.current_url)
        print("✅ Navegou para página de login")
        
        # 3. Página de cursos
        course_list_page = CourseListPage(self.driver, self.live_server_url)
        course_list_page.navigate_to_course_list()
        self.assertIn("/products/cursos/", self.driver.current_url)
        print("✅ Navegou para página de cursos")
        
        print("✅ Integração entre Page Objects funcionando")


def run_django_tests():
    """Executa os testes Django"""
    
    print("=" * 70)
    print("🧪 EXECUTANDO TESTES FUNCIONAIS COM DJANGO")
    print("=" * 70)
    
    # Importa e executa os testes Django
    import unittest
    
    # Cria suite de testes
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDjangoFunctional)
    
    # Executa os testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostra resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES DJANGO")
    print("=" * 70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success = total_tests - failures - errors
    
    print(f"✅ Sucessos: {success}/{total_tests}")
    print(f"❌ Falhas: {failures}")
    print(f"🚫 Erros: {errors}")
    
    if result.wasSuccessful():
        print("\n🎉 TODOS OS TESTES DJANGO PASSARAM!")
        print("📋 Page Objects estão totalmente integrados com Django!")
        return True
    else:
        print("\n❌ Alguns testes falharam.")
        if result.failures:
            print("Falhas:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        if result.errors:
            print("Erros:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
        return False


if __name__ == "__main__":
    success = run_django_tests()
    sys.exit(0 if success else 1)
