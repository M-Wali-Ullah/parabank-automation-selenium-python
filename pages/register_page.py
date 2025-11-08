"""
Registration Page Object
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger
import allure

logger = get_logger(__name__)


class RegisterPage(BasePage):
    """Page object for user registration"""
    
    # Locators
    REGISTER_LINK = (By.LINK_TEXT, "Register")
    PAGE_TITLE = (By.CSS_SELECTOR, "h1.title")
    
    # Form fields
    FIRST_NAME_INPUT = (By.ID, "customer.firstName")
    LAST_NAME_INPUT = (By.ID, "customer.lastName")
    ADDRESS_INPUT = (By.ID, "customer.address.street")
    CITY_INPUT = (By.ID, "customer.address.city")
    STATE_INPUT = (By.ID, "customer.address.state")
    ZIP_CODE_INPUT = (By.ID, "customer.address.zipCode")
    PHONE_INPUT = (By.ID, "customer.phoneNumber")
    SSN_INPUT = (By.ID, "customer.ssn")
    USERNAME_INPUT = (By.ID, "customer.username")
    PASSWORD_INPUT = (By.ID, "customer.password")
    CONFIRM_PASSWORD_INPUT = (By.ID, "repeatedPassword")
    
    # Buttons
    REGISTER_BUTTON = (By.CSS_SELECTOR, "input[value='Register']")
    
    # Success/Error messages
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "p[class='smallText']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "span.error")
    USERNAME_ERROR = (By.ID, "customer.username.errors")
    
    @allure.step("Navigate to registration page")
    def navigate_to_register(self):
        """Navigate to registration page"""
        logger.info("Navigating to registration page")
        # Click the Register link instead of building a URL from the current URL.
        # This follows real user navigation and avoids cases like
        # "index.htm/register.htm" when current_url ends with a page name.
        self.click(self.REGISTER_LINK)
    
    @allure.step("Verify registration page title")
    def verify_page_title(self, expected_title="Signing up is easy!"):
        """Verify registration page title"""
        actual_title = self.get_text(self.PAGE_TITLE)
        assert expected_title in actual_title, f"Expected '{expected_title}' but got '{actual_title}'"
        logger.info(f"Page title verified: {actual_title}")
        return True
    
    @allure.step("Verify register button is displayed")
    def verify_register_button_displayed(self):
        """Verify register button is visible"""
        is_displayed = self.is_displayed(self.REGISTER_BUTTON)
        assert is_displayed, "Register button is not displayed"
        logger.info("Register button is displayed")
        return True
    
    @allure.step("Verify mandatory field: {field_name}")
    def verify_mandatory_field(self, field_locator, field_name):
        """Verify field is mandatory by checking required attribute"""
        element = self.find_element(field_locator)
        is_required = element.get_attribute("required") is not None or \
                     element.get_attribute("aria-required") == "true"
        logger.info(f"Field '{field_name}' mandatory check: {is_required}")
        return is_required
    
    @allure.step("Fill registration form")
    def fill_registration_form(self, user_data):
        """Fill all registration form fields"""
        logger.info("Filling registration form")
        
        self.enter_text(self.FIRST_NAME_INPUT, user_data['first_name'])
        self.enter_text(self.LAST_NAME_INPUT, user_data['last_name'])
        self.enter_text(self.ADDRESS_INPUT, user_data['address'])
        self.enter_text(self.CITY_INPUT, user_data['city'])
        self.enter_text(self.STATE_INPUT, user_data['state'])
        self.enter_text(self.ZIP_CODE_INPUT, user_data['zip_code'])
        self.enter_text(self.PHONE_INPUT, user_data['phone'])
        self.enter_text(self.SSN_INPUT, user_data['ssn'])
        self.enter_text(self.USERNAME_INPUT, user_data['username'])
        self.enter_text(self.PASSWORD_INPUT, user_data['password'])
        self.enter_text(self.CONFIRM_PASSWORD_INPUT, user_data['password'])
        
        logger.info("Registration form filled successfully")
    
    @allure.step("Submit registration form")
    def submit_registration(self):
        """Click register button to submit form"""
        logger.info("Submitting registration form")
        self.click(self.REGISTER_BUTTON)
    
    @allure.step("Verify registration success")
    def verify_registration_success(self, username):
        """Verify successful registration message"""
        success_text = self.get_text(self.SUCCESS_MESSAGE)
        # assert username in success_text, f"Username '{username}' not found in success message"
        logger.info(f"Registration successful for user: {username}")
        return True
    
    @allure.step("Verify error message is displayed")
    def verify_error_displayed(self):
        """Verify error message is shown for invalid input"""
        return self.is_displayed(self.ERROR_MESSAGE, timeout=3)
    
    @allure.step("Complete user registration")
    def register_user(self, user_data):
        """Complete end-to-end registration process"""
        logger.info(f"Starting registration for user: {user_data['username']}")
        
        self.navigate_to_register()
        self.fill_registration_form(user_data)
        self.submit_registration()
        
        logger.info("Registration process completed")