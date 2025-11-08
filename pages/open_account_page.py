"""
Open New Account Page Object
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger
import allure

logger = get_logger(__name__)


class OpenAccountPage(BasePage):
    """Page object for opening new account"""
    
    # Locators
    OPEN_ACCOUNT_LINK = (By.LINK_TEXT, "Open New Account")
    PAGE_TITLE = (By.CSS_SELECTOR, "h1.title")
    ACCOUNT_TYPE_DROPDOWN = (By.ID, "type")
    FROM_ACCOUNT_DROPDOWN = (By.ID, "fromAccountId")
    OPEN_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "input[value='Open New Account']")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "div#openAccountResult h1.title")
    NEW_ACCOUNT_NUMBER = (By.ID, "newAccountId")
    
    @allure.step("Navigate to open new account page")
    def navigate_to_open_account(self):
        """Navigate to open new account page"""
        logger.info("Navigating to open new account page")
        self.click(self.OPEN_ACCOUNT_LINK)
    
    @allure.step("Verify open account page title")
    def verify_page_title(self, expected="Open New Account"):
        """Verify open account page title"""
        actual_title = self.get_text(self.PAGE_TITLE)
        assert expected in actual_title, f"Expected '{expected}' but got '{actual_title}'"
        logger.info(f"Page title verified: {actual_title}")
        return True
    
    @allure.step("Verify open account button is displayed")
    def verify_open_account_button_displayed(self):
        """Verify open account button is visible"""
        is_displayed = self.is_displayed(self.OPEN_ACCOUNT_BUTTON)
        assert is_displayed, "Open Account button is not displayed"
        logger.info("Open Account button is displayed")
        return True
    
    @allure.step("Select account type: {account_type}")
    def select_account_type(self, account_type="SAVINGS"):
        """Select account type from dropdown"""
        logger.info(f"Selecting account type: {account_type}")
        self.select_dropdown_by_text(self.ACCOUNT_TYPE_DROPDOWN, account_type)
    
    @allure.step("Open new account")
    def open_new_account(self, account_type="SAVINGS"):
        """Open a new account"""
        logger.info(f"Opening new {account_type} account")
        
        try:
            # Wait for form to be fully loaded and interactive
            self.wait_for_visibility(self.ACCOUNT_TYPE_DROPDOWN)
            self.wait_for_visibility(self.FROM_ACCOUNT_DROPDOWN)
            self.wait_for_clickable(self.OPEN_ACCOUNT_BUTTON)
            
            # Try to select account type with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.select_account_type(account_type)
                    logger.info(f"Account type selected: {account_type}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed to select account type: {e}")
                    self.driver.implicitly_wait(1)
            
            # Additional verification that account type was selected
            selected_type = self.get_attribute(self.ACCOUNT_TYPE_DROPDOWN, "value")
            logger.info(f"Verified selected account type: {selected_type}")
            
            # Enhanced button click with multiple approaches
            # Wait and scroll the button into view first
            button = self.wait_for_clickable(self.OPEN_ACCOUNT_BUTTON)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            self.driver.implicitly_wait(1)
            
            # Try standard click first
            try:
                button.click()
                logger.info("Standard click succeeded")
            except Exception as click_e:
                logger.warning(f"Standard click failed: {click_e}, trying alternatives")
                
                # Try moving to element first
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(self.driver).move_to_element(button).click().perform()
                    logger.info("ActionChains click succeeded")
                except Exception as action_e:
                    logger.warning(f"ActionChains click failed: {action_e}, trying JS click")
                    
                    # Final fallback to JS click
                    self.driver.execute_script("arguments[0].click();", button)
                    logger.info("JS click executed")
            
            logger.info("New account creation submitted")
            
        except Exception as e:
            logger.error(f"Failed to open new account: {e}")
            self.take_screenshot("open_account_failure")
            raise
    
    @allure.step("Verify account creation success")
    def verify_account_creation_success(self):
        """Verify new account was created successfully"""
        # Wait for success message with longer timeout since it involves backend processing
        self.wait_for_visibility(self.SUCCESS_MESSAGE, timeout=20)
        success_msg = self.get_text(self.SUCCESS_MESSAGE)
        logger.info(f"Found success message: {success_msg}")
        assert "Account Opened!" in success_msg, f"Account creation failed. Message: {success_msg}"
        
        # Wait for the new account number to be displayed
        self.wait_for_visibility(self.NEW_ACCOUNT_NUMBER)
        new_account_number = self.get_text(self.NEW_ACCOUNT_NUMBER)
        logger.info(f"New account created: {new_account_number}")
        return new_account_number