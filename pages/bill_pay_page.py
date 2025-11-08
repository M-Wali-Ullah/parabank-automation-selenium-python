"""
Bill Payment Page Object
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger
import allure

logger = get_logger(__name__)


class BillPayPage(BasePage):
    """Page object for bill payment"""
    
    # Locators
    BILL_PAY_LINK = (By.LINK_TEXT, "Bill Pay")
    PAGE_TITLE = (By.CSS_SELECTOR, "h1.title")
    
    # Payee Information fields
    PAYEE_NAME_INPUT = (By.NAME, "payee.name")
    PAYEE_ADDRESS_INPUT = (By.NAME, "payee.address.street")
    PAYEE_CITY_INPUT = (By.NAME, "payee.address.city")
    PAYEE_STATE_INPUT = (By.NAME, "payee.address.state")
    PAYEE_ZIP_INPUT = (By.NAME, "payee.address.zipCode")
    PAYEE_PHONE_INPUT = (By.NAME, "payee.phoneNumber")
    PAYEE_ACCOUNT_INPUT = (By.NAME, "payee.accountNumber")
    VERIFY_ACCOUNT_INPUT = (By.NAME, "verifyAccount")
    AMOUNT_INPUT = (By.NAME, "amount")
    
    # From account dropdown
    FROM_ACCOUNT_DROPDOWN = (By.NAME, "fromAccountId")
    
    # Button
    SEND_PAYMENT_BUTTON = (By.CSS_SELECTOR, "input[value='Send Payment']")
    
    # Messages
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "div#billpayResult h1.title")
    SUCCESS_DETAILS = (By.CSS_SELECTOR, "div#billpayResult p")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "span.error")
    
    @allure.step("Navigate to bill pay page")
    def navigate_to_bill_pay(self):
        """Navigate to bill payment page"""
        logger.info("Navigating to bill pay page")
        self.click(self.BILL_PAY_LINK)
    
    @allure.step("Verify bill pay page title")
    def verify_page_title(self, expected="Bill Payment Service"):
        """Verify bill pay page title"""
        actual_title = self.get_text(self.PAGE_TITLE)
        assert expected in actual_title, f"Expected '{expected}' but got '{actual_title}'"
        logger.info(f"Page title verified: {actual_title}")
        return True
    
    @allure.step("Verify send payment button is displayed")
    def verify_send_payment_button_displayed(self):
        """Verify send payment button is visible"""
        is_displayed = self.is_displayed(self.SEND_PAYMENT_BUTTON)
        assert is_displayed, "Send Payment button is not displayed"
        logger.info("Send Payment button is displayed")
        return True
    
    @allure.step("Verify mandatory fields")
    def verify_mandatory_fields(self):
        """Verify required fields show errors when empty"""
        # Try to submit with empty fields
        self.click(self.SEND_PAYMENT_BUTTON)
        # Check if errors are displayed
        return self.is_displayed(self.ERROR_MESSAGE, timeout=3)
    
    @allure.step("Fill bill payment form")
    def fill_bill_payment_form(self, payee_data):
        """Fill all bill payment form fields"""
        logger.info(f"Filling bill payment form for: {payee_data['payee_name']}")
        
        self.enter_text(self.PAYEE_NAME_INPUT, payee_data['payee_name'])
        self.enter_text(self.AMOUNT_INPUT, payee_data['amount'])
        self.enter_text(self.PAYEE_ADDRESS_INPUT, payee_data['address'])
        self.enter_text(self.PAYEE_CITY_INPUT, payee_data['city'])
        self.enter_text(self.PAYEE_STATE_INPUT, payee_data['state'])
        self.enter_text(self.PAYEE_ZIP_INPUT, payee_data['zip_code'])
        self.enter_text(self.PAYEE_PHONE_INPUT, payee_data['phone'])
        self.enter_text(self.PAYEE_ACCOUNT_INPUT, payee_data['account_number'])
        self.enter_text(self.VERIFY_ACCOUNT_INPUT, payee_data['account_number'])
        
        logger.info("Bill payment form filled")
    
    @allure.step("Submit bill payment")
    def submit_bill_payment(self):
        """Click send payment button"""
        logger.info("Submitting bill payment")
        self.click(self.SEND_PAYMENT_BUTTON)
    
    @allure.step("Verify payment success")
    def verify_payment_success(self, payee_name, amount):
        """Verify successful payment"""
        success_msg = self.get_text(self.SUCCESS_MESSAGE)
        assert "Bill Payment Complete" in success_msg, f"Payment failed. Message: {success_msg}"
        
        details = self.get_text(self.SUCCESS_DETAILS)
        assert payee_name in details, f"Payee name '{payee_name}' not found in success message"
        assert amount in details, f"Amount '{amount}' not found in success message"
        
        logger.info(f"Payment successful to {payee_name} for ${amount}")
        return True
    
    @allure.step("Complete bill payment")
    def pay_bill(self, payee_data):
        """Complete end-to-end bill payment process"""
        logger.info("Starting bill payment process")
        
        self.navigate_to_bill_pay()
        self.fill_bill_payment_form(payee_data)
        self.submit_bill_payment()
        
        logger.info("Bill payment process completed")