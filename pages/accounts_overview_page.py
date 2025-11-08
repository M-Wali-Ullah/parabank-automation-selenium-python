"""
Accounts Overview Page Object
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger
import allure

logger = get_logger(__name__)


class AccountsOverviewPage(BasePage):
    """Page object for accounts overview"""
    
    # Locators
    ACCOUNTS_OVERVIEW_LINK = (By.LINK_TEXT, "Accounts Overview")
    PAGE_TITLE = (By.CSS_SELECTOR, "h1.title")
    ACCOUNT_TABLE = (By.ID, "accountTable")
    ACCOUNT_NUMBERS = (By.CSS_SELECTOR, "#accountTable tbody tr td:first-child a")
    ACCOUNT_BALANCES = (By.CSS_SELECTOR, "#accountTable tbody tr td:nth-child(2)")
    TOTAL_BALANCE = (By.CSS_SELECTOR, "#accountTable tfoot tr td:nth-child(2)")
    
    @allure.step("Navigate to accounts overview")
    def navigate_to_accounts_overview(self):
        """Navigate to accounts overview page"""
        logger.info("Navigating to accounts overview")
        self.click(self.ACCOUNTS_OVERVIEW_LINK)
    
    @allure.step("Get account numbers")
    def get_account_numbers(self):
        """Get list of all account numbers"""
        elements = self.find_elements(self.ACCOUNT_NUMBERS)
        account_numbers = [elem.text for elem in elements]
        logger.info(f"Found {len(account_numbers)} accounts")
        return account_numbers
    
    @allure.step("Get account balance for account: {account_number}")
    def get_account_balance(self, account_number):
        """Get balance for specific account"""
        account_numbers = self.find_elements(self.ACCOUNT_NUMBERS)
        balances = self.find_elements(self.ACCOUNT_BALANCES)
        
        for idx, acc_elem in enumerate(account_numbers):
            if acc_elem.text == account_number:
                balance = balances[idx].text
                logger.info(f"Balance for account {account_number}: {balance}")
                return balance
        
        raise ValueError(f"Account {account_number} not found")