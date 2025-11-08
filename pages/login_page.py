"""
Login Page Object
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import Config
from utils.logger import get_logger
import allure

logger = get_logger(__name__)


class LoginPage(BasePage):
    """Page object for login functionality"""
    
    # Locators
    # Note: Login form uses name="username" and name="password" while registration uses "customer.*"
    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "input[value='Log In']")
    LOGOUT_LINK = (By.LINK_TEXT, "Log Out")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "p.error")
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "p.smallText")
    
    @allure.step("Navigate to login page")
    def navigate_to_login(self):
        """Navigate to login page"""
        logger.info("Navigating to login page")
        self.navigate_to(f"{Config.BASE_URL}/index.htm")
    
    @allure.step("Login with username: {username}")
    def login(self, username, password):
        """Perform login"""
        logger.info(f"Logging in as: {username}")
        
        self.enter_text(self.USERNAME_INPUT, username)
        self.enter_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        
        logger.info("Login submitted")
    
    @allure.step("Verify login success")
    def verify_login_success(self):
        """Verify successful login by checking welcome message"""
        is_logged_in = self.is_displayed(self.WELCOME_MESSAGE, timeout=10)
        assert is_logged_in, "Login failed - welcome message not displayed"
        logger.info("Login successful")
        return True
    
    @allure.step("Logout")
    def logout(self):
        """Perform logout"""
        logger.info("Logging out")
        self.click(self.LOGOUT_LINK)
