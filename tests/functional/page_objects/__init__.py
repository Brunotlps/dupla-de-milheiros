"""Page Objects package for functional tests"""

# Import dos Page Objects principais
from .base_page import BasePage
from .login_page import LoginPage
from .course_list_page import CourseListPage
from .course_detail_page import CourseDetailPage
from .checkout_page import CheckoutPage

__all__ = [
    'BasePage',
    'LoginPage',
    'CourseListPage',
    'CourseDetailPage',
    'CheckoutPage'
]