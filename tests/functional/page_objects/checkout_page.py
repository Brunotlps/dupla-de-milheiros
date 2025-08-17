import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from .base_page import BasePage

logger = logging.getLogger(__name__)


class CheckoutPage(BasePage):
    
    
    # URLs das páginas / Page URLs
    CHECKOUT_START_URL = "/products/checkout/{course_slug}/"
    CHECKOUT_PAYMENT_URL = "/products/checkout/payment/"
    
    
    class Locators:
        
        
        # Cabeçalho / Header
        PAGE_TITLE = (By.TAG_NAME, "h1")
        BREADCRUMB = (By.CLASS_NAME, "breadcrumb")
        
        # Resumo do pedido / Order summary
        ORDER_SUMMARY = (By.CLASS_NAME, "card")
        PRODUCT_NAME = (By.XPATH, "//p[contains(@innerHTML, '<strong>Produto:</strong>')]")
        PRODUCT_DESCRIPTION = (By.XPATH, "//p[contains(@innerHTML, '<strong>Descrição:</strong>')]")
        PRODUCT_PRICE = (By.XPATH, "//p[contains(@innerHTML, '<strong>Preço:</strong>')]")
        TOTAL_PRICE = (By.XPATH, "//p[contains(@innerHTML, '<strong>Total:</strong>')]")
        
        # Formulário de pagamento / Payment form
        PAYMENT_FORM = (By.ID, "paymentForm")
        PAYMENT_BRICK_CONTAINER = (By.ID, "paymentBrick_container")
        
        # Campos de pagamento (se visíveis) / Payment fields (if visible)
        CARD_NUMBER_FIELD = (By.NAME, "cardNumber")
        EXPIRY_DATE_FIELD = (By.NAME, "expiryDate")
        CVV_FIELD = (By.NAME, "cvv")
        CARDHOLDER_NAME_FIELD = (By.NAME, "cardholderName")
        
        # Botões / Buttons
        SUBMIT_PAYMENT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
        BACK_BUTTON = (By.XPATH, "//a[contains(text(), 'Voltar')]")
        
        # Mensagens / Messages
        LOADING_MESSAGE = (By.XPATH, "//div[contains(text(), 'Processando')]")
        SUCCESS_MESSAGE = (By.CSS_SELECTOR, ".alert-success")
        ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
        
        # Estados / States
        PAYMENT_PROCESSING = (By.CLASS_NAME, "payment-processing")
        PAYMENT_SUCCESS = (By.CLASS_NAME, "payment-success")
        PAYMENT_ERROR = (By.CLASS_NAME, "payment-error")
    
    def __init__(self, driver, base_url):
        
        
        super().__init__(driver, base_url)
    
    def navigate_to_checkout_start(self, course_slug):
        """
        Navega para o início do checkout / Navigate to checkout start
        
        Args:
            course_slug: Slug do curso
        """
        
        
        url = f"/products/checkout/{course_slug}/"
        self.navigate_to(url)
    
    def navigate_to_checkout_payment(self):
        

        self.navigate_to(self.CHECKOUT_PAYMENT_URL)
    
    def get_page_title(self):
        

        return self.get_text(self.Locators.PAGE_TITLE)
    
    def get_product_name(self):
        

        return self.get_text(self.Locators.PRODUCT_NAME)
    
    def get_product_price(self):
        

        return self.get_text(self.Locators.PRODUCT_PRICE)
    
    def get_total_price(self):
        

        return self.get_text(self.Locators.TOTAL_PRICE)
    
    def is_payment_form_present(self):
        
        
        return self.is_element_present(self.Locators.PAYMENT_FORM)
    
    def is_payment_brick_present(self):
        
        
        return self.is_element_present(self.Locators.PAYMENT_BRICK_CONTAINER)
    
    def wait_for_payment_brick_load(self, timeout=30):
        
        
        try:
            self.long_wait.until(
                lambda driver: self.is_element_present(self.Locators.PAYMENT_BRICK_CONTAINER)
            )
        except:
            logger.warning("Payment Brick não carregou no tempo esperado")
    
    def enter_card_number(self, card_number):
        

        self.send_keys_to_element(self.Locators.CARD_NUMBER_FIELD, card_number)
    
    def enter_expiry_date(self, expiry_date):
        

        self.send_keys_to_element(self.Locators.EXPIRY_DATE_FIELD, expiry_date)
    
    def enter_cvv(self, cvv):
      

        self.send_keys_to_element(self.Locators.CVV_FIELD, cvv)
    
    def enter_cardholder_name(self, name):
        
        
        self.send_keys_to_element(self.Locators.CARDHOLDER_NAME_FIELD, name)
    
    def click_submit_payment(self):
        
        
        self.click_element(self.Locators.SUBMIT_PAYMENT_BUTTON)
    
    def click_back_button(self):
        
        
        self.click_element(self.Locators.BACK_BUTTON)
    
    def wait_for_payment_processing(self, timeout=30):
        
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                lambda driver: self.is_element_present(self.Locators.PAYMENT_PROCESSING) or
                              self.is_element_present(self.Locators.PAYMENT_SUCCESS) or
                              self.is_element_present(self.Locators.PAYMENT_ERROR)
            )
        except TimeoutException:
            logger.error("Timeout aguardando processamento do pagamento")
            raise
    
    def is_payment_successful(self):
        
        
        return self.is_element_present(self.Locators.PAYMENT_SUCCESS)
    
    def is_payment_error(self):
        
        
        return self.is_element_present(self.Locators.PAYMENT_ERROR)
    
    def get_success_message(self):
        
        
        if self.is_element_present(self.Locators.SUCCESS_MESSAGE):
            return self.get_text(self.Locators.SUCCESS_MESSAGE)
        return None
    
    def get_error_message(self):
        
        
        if self.is_element_present(self.Locators.ERROR_MESSAGE):
            return self.get_text(self.Locators.ERROR_MESSAGE)
        return None