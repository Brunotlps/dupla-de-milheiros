#!/usr/bin/env python3
"""Exemplo prático de teste funcional - Dupla de Milheiros"""

from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from tests.functional.page_objects import BasePage, LoginPage
from products.models import Course


class ExampleFunctionalTest(LiveServerTestCase):
    """Exemplo prático de teste funcional usando Page Objects"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Configurações do Chrome para testes
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Remove para debug visual
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Configura dados para cada teste"""
        # Cria usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Cria curso de teste (se necessário)
        self.course = Course.objects.create(
            title="Curso Teste de Milhas",
            slug="curso-teste-milhas", 
            description="Descrição do curso de teste",
            price=199.99,
            active=True
        )
    
    def test_homepage_loads(self):
        """Testa se a página inicial carrega corretamente"""
        base_page = BasePage(self.driver, self.live_server_url)
        base_page.navigate_to("/")
        
        # Verifica se chegou na página correta
        self.assertIn(self.live_server_url, self.driver.current_url)
        
        # Verifica título da página
        title = self.driver.title
        self.assertIn("Dupla de Milheiros", title)
    
    def test_login_page_elements(self):
        """Testa elementos da página de login"""
        login_page = LoginPage(self.driver, self.live_server_url)
        login_page.navigate_to_login()
        
        # Verifica se está na página de login
        self.assertIn("/accounts/login/", self.driver.current_url)
        
        # Verifica se o formulário está presente
        self.assertTrue(login_page.is_login_form_present())
        
    def test_user_login_flow(self):
        """Testa fluxo completo de login"""
        login_page = LoginPage(self.driver, self.live_server_url)
        login_page.navigate_to_login()
        
        # Tenta fazer login
        login_page.login(self.user.username, "testpass123")
        
        # Verifica se o login foi bem-sucedido
        # (Pode verificar redirecionamento ou presença de elementos de usuário logado)
        # Este teste pode precisar ser ajustado baseado no comportamento real da aplicação


# Para executar este teste:
# python manage.py test tests.functional.example_test
