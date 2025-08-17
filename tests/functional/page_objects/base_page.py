"""Classe base para todos os Page Objects / Base class for all Page Objects."""


import logging

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


logger = logging.getLogger(__name__)


class BasePage:
    

    def __init__(self, driver, base_url):
        """
            Inicializa a página base / Initialize base page

            Args:
                driver: WebDriver instance
                base_url: URL base do servidor de teste
        """


        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)
        self.long_wait = WebDriverWait(driver, 30) # Tempo de espera mais longo para elementos que demoram mais para carregar / Longer wait time for elements that take longer to load

    
    def navigate_to(self, path=""):
        """Navega para uma URL específica / Navigate to a specific URL."""


        url = f"{self.base_url}{path}"
        logger.info(f"Navegando para: {url}")
        self.driver.get(url)
        self.wait_for_page_load()
    

    def wait_for_page_load(self):


        try:
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"   
            )
        except TimeoutException:
            logger.warning("Timeout esperando o carregamento da página.")

    
    def find_element(self, locator, timeout=10):
        """Encontra um elemento com wait implicito / Find an element with implicit wait."""

        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            logger.error(f"Elemento não encontrado: {locator}")
            raise

    
    def click_element(self, locator, timeout=10):


        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            element.click()

            logger.debug(f"Clicado no elemento: {locator}")
        except TimeoutException:
            logger.error(f"Elemento não clicável: {locator}")
            raise 


    def send_keys_to_element(self, locator, text, timeout=10, clear_first=True):
        """Envia texto para um elemento, limpando o campo primeiro se necessário / Sends text to an element, clearing the field first if necessary."""

        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))

            if clear_first:
                element.clear()
            
            element.send_keys(text)
            logger.debug(f"Texto enviado para o elemento: {locator} - Texto: {text}")
        except TimeoutException:
            logger.error(f"Não foi possível enviar texto para o elemento: {locator}")
            raise
    

    def get_text(self, locator, timeout=10):


        element = self.find_element(locator, timeout)
        return element.text if element else None
    

    def is_element_present(self, locator, timeout=5):


        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            logger.debug(f"Elemento não encontrado: {locator}")
            return False
    

    def wait_for_url_contains(self, text, timeout=10):
        """Espera que a URL contenha um texto específico / Waits for the URL to contain a specific text."""

        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.url_contains(text))
        except TimeoutException:
            logger.error(f"URL não contém o texto: {text} após {timeout} segundos.")
            raise 
    

    class CommonLocators:
        """Locators comuns usados em várias páginas / Common locators used on multiple pages."""

        # Navegação / Navigation
        NAVBAR = (By.CLASS_NAME, "navbar")
        HOME_LINK = (By.XPATH, "//a[@href='/']")
        PRODUCTS_LINK = (By.XPATH, "//a[@href='/products/cursos/']")
        NEWS_LINK = (By.XPATH, "//a[@href='/news/']")
        
        # Usuário / User
        USER_DROPDOWN = (By.ID, "configMenu")
        LOGOUT_BUTTON = (By.XPATH, "//button[contains(text(), 'Sair')]")
        
        # Mensagens / Messages
        ALERT_SUCCESS = (By.CSS_SELECTOR, ".alert-success")
        ALERT_ERROR = (By.CSS_SELECTOR, ".alert-danger")




    




