import os
import logging
 

from datetime import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase # serve arquivos estáticos e permite acesso via URL real para o Selenium / serves static files and allows access via real URL for Selenium
from django.contrib.auth.models import User

from products.models import Course, PaymentSettings



# Configuração de logging para testes / Logging configuration for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseFunctionalTest(StaticLiveServerTestCase):
    """Classe base para todos os testes funcionais. / Base class for all functional tests."""


    @classmethod # Executa uma ÚNICA vez quando a classe é carregada, não recria WebDriver para cada teste, vai configurar PaymentSettings, Courses, etc uma única vez / Runs ONCE when the class is loaded, does not recreate WebDriver for each test, sets up PaymentSettings, Courses, etc. once
    def setUpClass(cls):
        
        
        super().setUpClass()
        cls.setup_webdriver()
        cls.setup_test_data()

    @classmethod
    def setup_webdriver(cls):
        """Configurações do webdriver / Webdriver setup."""


        try:
            from webdriver_manager.chrome import ChromeDriverManager # Baixa automaticamente a versão correta do ChromeDriver / Automatically downloads the correct version of ChromeDriver
            from selenium.webdriver.chrome.service import Service as ChromeService # Interface entre Selenium e o ChromeDriver / Interface between Selenium and ChromeDriver

            options = cls.get_chrome_options() # Configurações do navegador / Browser settings
            chrome_service = ChromeService(ChromeDriverManager().install())
            cls.driver = webdriver.Chrome(service=chrome_service, options=options)

        except ImportError:
            # Fallback para ChromeDriver local / Fallback to local ChromeDriver
            options = cls.get_chrome_options()
            cls.driver = webdriver.Chrome(options=options)

        except Exception as e:
            logger.error(f"Erro ao configurar o WebDriver: {e}")
            cls.driver = None  
    
    @classmethod
    def get_chrome_options(cls):
        """Opções do Chrome para diferentes ambientes / Chrome options for different environments."""

        from selenium.webdriver.chrome.options import Options

        options = Options()

        # Configurações para CI/CD ou ambientes de produção / Settings for CI/CD or production environments
        if os.getenv('CI'):
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

        # Configurações gerais / General settings
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')

        return options

    
    
    def setUp(self):
        """Configuração inicial para cada teste / Initial setup for each test."""
        

        if not self.driver:
            self.skipTest("WebDriver não configurado corretamente. Verifique as dependências.")
        
        self.driver.delete_all_cookies()
        self.driver.implicit_wait = 10  # Tempo de espera implícito / Implicit wait time
        logger.info(f"Iniciando teste: {self._testMethodName} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    
    def tearDown(self):
        """Limpeza após cada teste / Cleanup after each test."""
        
        
        if hasattr(self, 'driver') and self.driver:
            if hasattr(self, '_outcome'):
                if not self._outcome.success:
                    self.take_screenshot()

        logger.info(f"Finalizando teste: {self._testMethodName} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    

    def take_screenshot(self):
        """Tira uma captura de tela do estado atual do navegador / Takes a screenshot of the current browser state."""
        

        if self.driver:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"failure_{self._testMethodName}_{timestamp}.png"
            filepath = os.path.join("test_screenshots", filename)

            os.makedirs("test_screenshots", exist_ok=True)

            self.driver.save_screenshot(filepath)
            logger.error(f"Captura de tela salva em: {filepath}")






    