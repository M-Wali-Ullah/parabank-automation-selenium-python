"""
Test Suite: User Registration & Account Creation
"""
import pytest
import allure
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from utils.logger import get_logger
from config.config import Config

logger = get_logger(__name__)


@allure.epic("User Management")
@allure.feature("User Registration")
@pytest.mark.smoke
@pytest.mark.critical
class TestUserRegistration:
    
    @allure.title("Test 01: Complete User Registration Workflow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_user_registration(self, driver, generate_user_data):
        """Test complete user registration with all validations"""
        
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)
        
        # Navigate to registration page
        with allure.step("Navigate to ParaBank and Registration page"):
            login_page.navigate_to_login()
            register_page.navigate_to_register()
        
        # ASSERTION 1: Title and Button Verification
        with allure.step("Verify page title and register button"):
            assert register_page.verify_page_title("Signing up is easy!")
            assert register_page.verify_register_button_displayed()
        
        # ASSERTION 2: Mandatory Field Validation
        with allure.step("Verify mandatory fields are required"):
            # Test that form shows errors without required fields
            register_page.click(register_page.REGISTER_BUTTON)
            assert register_page.verify_error_displayed(), "Mandatory field validation failed"
        
        # FLOW: Main Registration Flow and Save
        with allure.step("Fill and submit registration form"):
            register_page.fill_registration_form(generate_user_data)
            register_page.submit_registration()
        
        # ASSERTION 3: Verify Data After Save
        with allure.step("Verify registration success and account creation"):
            # After successful registration, user is automatically logged in
            assert register_page.verify_registration_success(generate_user_data['username'])
            
            # Save credentials for other tests to use
            logger.info(f"Saving credentials for future tests: {generate_user_data['username']}")
            Config.save_temp_credentials({
                'username': generate_user_data['username'],
                'password': generate_user_data['password'],
                'full_data': generate_user_data
            })