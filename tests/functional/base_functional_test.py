import os
import logging
from datetime import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver

from products.models import Course, PaymentSettings


# Logging configuration for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseFunctionalTest(StaticLiveServerTestCase):
    """Base class for all functional tests."""

    @classmethod
    def setUpClass(cls):
        """Runs ONCE when the class is loaded, sets up WebDriver and test data."""
        super().setUpClass()
        cls.setup_webdriver()
        cls.setup_test_data()

    @classmethod
    def setup_webdriver(cls):
        """WebDriver setup."""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service as ChromeService

            options = cls.get_chrome_options()
            chrome_service = ChromeService(ChromeDriverManager().install())
            cls.driver = webdriver.Chrome(service=chrome_service, options=options)

        except ImportError:
            # Fallback to local ChromeDriver
            options = cls.get_chrome_options()
            cls.driver = webdriver.Chrome(options=options)

        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            cls.driver = None  
    
    @classmethod
    def get_chrome_options(cls):
        """Chrome options for different environments."""
        from selenium.webdriver.chrome.options import Options

        options = Options()

        # Settings for CI/CD or production environments
        if os.getenv('CI'):
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

        # General settings
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')

        return options

    @classmethod
    def setup_test_data(cls):
        """Set up test data once for all tests."""
        # Create payment settings
        cls.payment_settings = PaymentSettings.objects.create(
            is_active=True,
            is_sandbox=True,
            sandbox_public_key="TEST-public-key",
            sandbox_access_token="TEST-access-token",
            production_public_key="PROD-public-key",
            production_access_token="PROD-access-token"
        )
        
        # Create test course
        cls.test_course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            description="This is a test course for functional testing.",
            price=100.00,
            active=True
        )
    
    def setUp(self):
        """Initial setup for each test."""
        if not self.driver:
            self.skipTest("WebDriver not configured correctly. Check dependencies.")
        
        self.driver.delete_all_cookies()
        self.driver.implicitly_wait(10)  # Implicit wait time
        logger.info(f"Starting test: {self._testMethodName} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def tearDown(self):
        """Cleanup after each test."""
        if hasattr(self, 'driver') and self.driver:
            if hasattr(self, '_outcome'):
                if not self._outcome.success:
                    self.take_screenshot()

        logger.info(f"Finishing test: {self._testMethodName} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests."""
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()
        super().tearDownClass()

    def take_screenshot(self):
        """Takes a screenshot of the current browser state."""
        if self.driver:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"failure_{self._testMethodName}_{timestamp}.png"
            filepath = os.path.join("test_screenshots", filename)

            os.makedirs("test_screenshots", exist_ok=True)

            self.driver.save_screenshot(filepath)
            logger.error(f"Screenshot saved at: {filepath}")
            
    def create_test_user(self, username='testuser', password='testpass123'):
        """Helper method to create test users."""
        return User.objects.create_user(username=username, password=password)
