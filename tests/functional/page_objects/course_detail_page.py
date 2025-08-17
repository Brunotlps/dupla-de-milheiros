from selenium.webdriver.common.by import By
from .base_page import BasePage


class CourseDetailPage(BasePage):
    """Page Object para a página de detalhes do curso / Page Object for course detail page"""
    
    

    class Locators:
        
        
        # Cabeçalho / Header
        PAGE_TITLE = (By.TAG_NAME, "h1")
        BREADCRUMB = (By.CLASS_NAME, "breadcrumb")
        

        # Imagem e compra / Image and purchase
        COURSE_IMAGE = (By.CLASS_NAME, "course-image-large")
        COURSE_PRICE = (By.CLASS_NAME, "course-price-large")
        BUY_BUTTON = (By.LINK_TEXT, "Comprar Agora")
        ACCESS_COURSE_BUTTON = (By.LINK_TEXT, "Acessar Curso")
        PURCHASE_STATUS = (By.CLASS_NAME, "purchase-status")
        

        # Descrição / Description
        COURSE_DESCRIPTION_SECTION = (By.CLASS_NAME, "course-description-section")
        COURSE_DESCRIPTION_CONTENT = (By.CLASS_NAME, "course-description-content")
        

        # Conteúdo do curso / Course content
        COURSE_CONTENT_SECTION = (By.CLASS_NAME, "course-content-section")
        COURSE_MODULES = (By.ID, "courseModules")
        MODULE_HEADERS = (By.CLASS_NAME, "accordion-header")
        MODULE_BUTTONS = (By.CLASS_NAME, "accordion-button")
        LESSON_LIST = (By.CLASS_NAME, "lesson-list")
        LESSON_ITEMS = (By.CLASS_NAME, "lesson-item")
        LESSON_TITLES = (By.CLASS_NAME, "lesson-title")
        LESSON_DURATIONS = (By.CLASS_NAME, "lesson-duration")
        

        # Estados / States
        ALREADY_PURCHASED = (By.XPATH, "//span[contains(text(), 'Você já adquiriu este curso')]")
    
    def __init__(self, driver, base_url):


        super().__init__(driver, base_url)
    
    def navigate_to_course_detail(self, course_slug):
        """
        Navega para a página de detalhes de um curso específico / Navigate to course detail page
        
        Args:
            course_slug: Slug do curso
        """


        url = f"/products/cursos/{course_slug}/"
        self.navigate_to(url)
    
    def get_course_title(self):
        

        return self.get_text(self.Locators.PAGE_TITLE)
    
    def get_course_price(self):
        

        return self.get_text(self.Locators.COURSE_PRICE)
    
    def get_course_description(self):
        

        return self.get_text(self.Locators.COURSE_DESCRIPTION_CONTENT)
    
    def click_buy_button(self):
        

        self.click_element(self.Locators.BUY_BUTTON)
    
    def click_access_course_button(self):
        

        self.click_element(self.Locators.ACCESS_COURSE_BUTTON)
    
    def is_buy_button_present(self):
        

        return self.is_element_present(self.Locators.BUY_BUTTON, timeout=3)
    
    def is_access_button_present(self):
        

        return self.is_element_present(self.Locators.ACCESS_COURSE_BUTTON, timeout=3)
    
    def is_already_purchased(self):
        

        return self.is_element_present(self.Locators.ALREADY_PURCHASED, timeout=3)
    
    def get_module_count(self):
        
        
        modules = self.driver.find_elements(*self.Locators.MODULE_HEADERS)
        return len(modules)
    
    def click_module(self, module_index=0):
        """
        Clica em um módulo para expandir / Click module to expand
        
        Args:
            module_index: Índice do módulo (0 = primeiro)
        """
        
        
        module_buttons = self.driver.find_elements(*self.Locators.MODULE_BUTTONS)
        if module_buttons and module_index < len(module_buttons):
            module_buttons[module_index].click()
        else:
            raise IndexError(f"Módulo no índice {module_index} não encontrado")
    
    def get_lessons_from_module(self, module_index=0):
        """
        Obtém lista de aulas de um módulo / Get list of lessons from a module
        
        Args:
            module_index: Índice do módulo
            
        Returns:
            Lista de informações das aulas
        """
        
        
        # Expandir módulo se necessário
        self.click_module(module_index)
        
        # Aguardar expansão
        self.wait.until(lambda d: self.is_element_present(self.Locators.LESSON_ITEMS))
        
        lesson_items = self.driver.find_elements(*self.Locators.LESSON_ITEMS)
        lessons = []
        
        for item in lesson_items:
            try:
                title_element = item.find_element(*self.Locators.LESSON_TITLES)
                title = title_element.text
                
                # Tentar obter duração
                try:
                    duration_element = item.find_element(*self.Locators.LESSON_DURATIONS)
                    duration = duration_element.text
                except:
                    duration = None
                
                lessons.append({
                    'title': title,
                    'duration': duration
                })
            except Exception as e:
                continue
        
        return lessons
    
    def is_course_image_present(self):
        

        return self.is_element_present(self.Locators.COURSE_IMAGE)
    
    def scroll_to_course_content(self):
        
        
        self.scroll_to_element(self.Locators.COURSE_CONTENT_SECTION)