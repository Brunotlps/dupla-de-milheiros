import logging
from selenium.webdriver.common.by import By
from .base_page import BasePage

logger = logging.getLogger(__name__)



class LoginPage(BasePage):
    """Classe para a página de login / Class for the login page."""

    PAGE_URL = "/accounts/login/"

    
    class Locators:


        USERNAME_FIELD = (By.NAME, "username")
        PASSWORD_FIELD = (By.NAME, "password")
        LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
        LOGIN_FORM = (By.TAG_NAME, "form")
        ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-warning")
        SIGNUP_LINK = (By.XPATH, "//a[contains(text(), 'Cadastre-se')]")
        
        # Mensagens de erro específicas / Specific error messages
        USERNAME_ERROR = (By.CSS_SELECTOR, ".invalid-feedback")
        PASSWORD_ERROR = (By.CSS_SELECTOR, ".invalid-feedback")
        
        # Elementos para logout / Logout elements
        USER_DROPDOWN = (By.ID, "configMenu")
        LOGOUT_BUTTON = (By.XPATH, "//button[contains(text(), 'Sair')]")
    


    def __init__(self, driver, base_url):


        super().__init__(driver, base_url)
    
    
    def navigate_to_login(self):


        self.navigate_to(self.PAGE_URL)

    
    def enter_username(self, username):


        self.send_keys_to_element(self.Locators.USERNAME_FIELD, username)

    
    def enter_password(self, password):


        self.send_keys_to_element(self.Locators.PASSWORD_FIELD, password)
    

    def click_login_button(self):


        self.click_element(self.Locators.LOGIN_BUTTON)
    

    def login(self, username, password):


        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

    
    def get_error_message(self):


        if self.is_element_present(self.Locators.ERROR_MESSAGE):
            return self.get_text(self.Locators.ERROR_MESSAGE)
        return None
    

    def is_login_form_present(self):


        return self.is_element_present(self.Locators.LOGIN_FORM)


    def click_signup_link(self):
        
        
        self.click_element(self.Locators.SIGNUP_LINK)

    def logout(self):
        """Faz logout do usuário / Logs out the user"""
        
        try:
            # Clica no dropdown do usuário
            self.click_element(self.Locators.USER_DROPDOWN)
            
            # Clica no botão de logout
            self.click_element(self.Locators.LOGOUT_BUTTON)
            
            # Aguarda redirecionamento para a página de login
            self.wait_for_url_contains("/accounts/login/")
            
        except Exception as e:
            logger.warning(f"Erro ao fazer logout: {e}")
