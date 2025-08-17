import logging
from selenium.webdriver.common.by import By
from .base_page import BasePage

logger = logging.getLogger(__name__)


class CourseListPage(BasePage):
    """Page Object para a página de lista de cursos / Page Object for course list page"""
    

    PAGE_URL = "/products/cursos/"
    
   
    class Locators:
        
        
        PAGE_TITLE = (By.TAG_NAME, "h1")
        BREADCRUMB = (By.CLASS_NAME, "breadcrumb")
        
        
        COURSE_GRID = (By.CLASS_NAME, "courses-grid")
        COURSE_CARDS = (By.CLASS_NAME, "course-card")
        COURSE_TITLE = (By.CLASS_NAME, "course-title")
        COURSE_DESCRIPTION = (By.CLASS_NAME, "course-description")
        COURSE_PRICE = (By.CLASS_NAME, "course-price")
        COURSE_DETAILS_BUTTON = (By.CLASS_NAME, "btn-course-details")
        COURSE_IMAGE = (By.CLASS_NAME, "course-image")
        
        # Estado vazio / Empty state
        NO_COURSES_MESSAGE = (By.XPATH, "//p[contains(text(), 'Nenhum curso disponível')]")
    
    def __init__(self, driver, base_url):
        
        
        super().__init__(driver, base_url)
    
    def navigate_to_course_list(self):
        

        self.navigate_to(self.PAGE_URL)
    
    def wait_for_course_grid_load(self, timeout=10):
        """Espera o grid de cursos carregar / Waits for course grid to load"""
        
        try:
            self.wait.until(
                lambda driver: self.is_element_present(self.Locators.COURSE_GRID) or
                              self.is_element_present(self.Locators.NO_COURSES_MESSAGE)
            )
        except Exception as e:
            logger.warning(f"Timeout esperando o grid de cursos carregar: {e}")
    
    def get_page_title(self):


        return self.get_text(self.Locators.PAGE_TITLE)
    
    def get_course_cards(self):
        
        
        return self.driver.find_elements(*self.Locators.COURSE_CARDS)
    
    def get_course_count(self):
        

        return len(self.get_course_cards())
    
    def get_course_titles(self):
        

        title_elements = self.driver.find_elements(*self.Locators.COURSE_TITLE)
        return [element.text for element in title_elements]
    
    def click_course_details(self, course_index=0):
        """
        Clica no botão 'Ver Detalhes' de um curso / Click 'View Details' button of a course
        
        Args:
            course_index: Índice do curso (0 = primeiro curso)
        """


        detail_buttons = self.driver.find_elements(*self.Locators.COURSE_DETAILS_BUTTON)
        if detail_buttons and course_index < len(detail_buttons):
            detail_buttons[course_index].click()
        else:
            raise IndexError(f"Curso no índice {course_index} não encontrado")
    
    def click_course_by_title(self, title):
        """
        Clica em um curso específico pelo título / Click specific course by title
        
        Args:
            title: Título do curso
        """


        course_link = (By.XPATH, f"//a[contains(@href, '/products/cursos/') and .//h5[contains(text(), '{title}')]]")
        self.click_element(course_link)
    
    def is_courses_grid_present(self):
        """Verifica se o grid de cursos está presente / Check if courses grid is present"""
        
        
        return self.is_element_present(self.Locators.COURSE_GRID)
    
    def is_no_courses_message_present(self):
        """Verifica se mensagem 'sem cursos' está presente / Check if 'no courses' message is present"""
        
        
        return self.is_element_present(self.Locators.NO_COURSES_MESSAGE)
    
    def get_course_info_by_index(self, index):
        """
        Obtém informações de um curso por índice / Get course information by index
        
        Args:
            index: Índice do curso
            
        Returns:
            Dict com informações do curso
        """
        
        
        course_cards = self.get_course_cards()
        if index >= len(course_cards):
            raise IndexError(f"Curso no índice {index} não encontrado")
        
        card = course_cards[index]
        
        try:
            title = card.find_element(*self.Locators.COURSE_TITLE).text
            description = card.find_element(*self.Locators.COURSE_DESCRIPTION).text
            price = card.find_element(*self.Locators.COURSE_PRICE).text
            
            return {
                'title': title,
                'description': description,
                'price': price,
                'index': index
            }
        except Exception as e:
            return {
                'title': 'N/A',
                'description': 'N/A',
                'price': 'N/A',
                'index': index,
                'error': str(e)
            }