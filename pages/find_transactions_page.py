"""
Find Transactions Page Object
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger
import allure
import time

logger = get_logger(__name__)


class FindTransactionsPage(BasePage):
    """Page object for finding transactions"""
    
    # Locators
    FIND_TRANSACTIONS_LINK = (By.LINK_TEXT, "Find Transactions")
    PAGE_TITLE = (By.CSS_SELECTOR, "h1.title")
    
    # Form elements
    ACCOUNT_DROPDOWN = (By.ID, "accountId")
    AMOUNT_INPUT = (By.ID, "amount")
    FIND_BY_AMOUNT_BUTTON = (By.ID, "findByAmount")
    
    # Results
    TRANSACTION_TABLE = (By.ID, "transactionTable")
    TRANSACTION_ROWS = (By.CSS_SELECTOR, "#transactionTable tr.transaction")
    AMOUNT_COLUMN = (By.CSS_SELECTOR, "td.amount")
    NO_RESULTS_MESSAGE = (By.CSS_SELECTOR, "td.error")
    
    @allure.step("Navigate to find transactions page")
    def navigate_to_find_transactions(self):
        """Navigate to find transactions page"""
        logger.info("Navigating to find transactions page")
        self.click(self.FIND_TRANSACTIONS_LINK)
        self.wait_for_visibility(self.AMOUNT_INPUT)
    
    @allure.step("Search for transaction by amount: {amount}")
    def find_transaction_by_amount(self, amount, account_idx=None):
        """
        Search for a transaction by amount
        Args:
            amount: Amount to search for
            account_idx: Optional index in account dropdown. If None, uses default selected account.
        """
        # Format amount for search (strip $ and ensure 2 decimal places)
        try:
            amount_val = float(str(amount).replace('$', ''))
            formatted_amount = f"{amount_val:.2f}"
        except ValueError:
            formatted_amount = amount
            
        logger.info(f"Searching for transaction with amount: {formatted_amount}")
        
        # Select account if specified
        if account_idx is not None:
            from selenium.webdriver.support.ui import Select
            account_select = Select(self.find_element(self.ACCOUNT_DROPDOWN))
            account_select.select_by_index(account_idx)
            time.sleep(1)  # wait for any dynamic updates
        
        # Enter amount and search
        self.enter_text(self.AMOUNT_INPUT, formatted_amount)
        time.sleep(1)  # wait for input to settle
        self.click(self.FIND_BY_AMOUNT_BUTTON)
        
        # Wait for results (either table or no results message)
        try:
            self.wait_for_visibility(self.TRANSACTION_TABLE)
        except:
            # Check for no results message
            if self.is_displayed(self.NO_RESULTS_MESSAGE):
                logger.info("No transactions found")
                return []
            raise
        
        # Get all transaction rows
        rows = self.find_elements(self.TRANSACTION_ROWS)
        transactions = []
        
        for row in rows:
            try:
                amount_cell = row.find_element(*self.AMOUNT_COLUMN)
                amount_text = amount_cell.text.strip()
                if amount_text:
                    transactions.append({
                        'amount': amount_text,
                        'row': row
                    })
            except:
                continue
                
        logger.info(f"Found {len(transactions)} transactions")
        return transactions

    @allure.step("Verify transaction exists with amount: {amount}")
    def verify_transaction_exists(self, amount):
        """
        Verify a transaction with the given amount exists in search results
        Args:
            amount: Amount to verify (will be formatted for comparison)
        Returns:
            True if transaction found, False otherwise
        """
        # Format amount for comparison
        try:
            amount_val = float(str(amount).replace('$', ''))
            formatted_amount = f"${amount_val:.2f}"
        except ValueError:
            formatted_amount = amount
            
        transactions = self.find_transaction_by_amount(formatted_amount)
        
        # Check if any transaction matches the amount
        for transaction in transactions:
            if transaction['amount'] == formatted_amount:
                logger.info(f"Found matching transaction with amount {formatted_amount}")
                return True
                
        logger.warning(f"No transaction found with amount {formatted_amount}")
        return False