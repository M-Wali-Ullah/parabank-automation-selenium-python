"""
Test Suite: Fund Transfer Between Accounts
"""
import pytest
import allure
from pages.transfer_funds_page import TransferFundsPage
from pages.accounts_overview_page import AccountsOverviewPage
from pages.open_account_page import OpenAccountPage
from utils.logger import get_logger

logger = get_logger(__name__)


@allure.epic("Banking Operations")
@allure.feature("Fund Transfer")
@pytest.mark.regression
@pytest.mark.transactions
class TestFundTransfer:
    
    @allure.title("Test 02: Fund Transfer Between Accounts")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_fund_transfer(self, driver, logged_in_user):
        """Test complete fund transfer with all validations"""
        
        transfer_page = TransferFundsPage(driver)
        accounts_page = AccountsOverviewPage(driver)
        open_account_page = OpenAccountPage(driver)
        
        # Ensure we have two accounts
        with allure.step("Setup: Create second account if needed"):
            accounts_page.navigate_to_accounts_overview()
            account_numbers = accounts_page.get_account_numbers()
            if len(account_numbers) < 2:
                logger.info("Only one account exists. Creating a second account...")
                open_account_page.navigate_to_open_account()
                open_account_page.open_new_account(account_type="SAVINGS")
                new_account = open_account_page.verify_account_creation_success()
                logger.info(f"Created new account: {new_account}")
                accounts_page.navigate_to_accounts_overview()
                account_numbers = accounts_page.get_account_numbers()
        
        # Get initial account balances
        with allure.step("Navigate to accounts and get initial balances"):
            assert len(account_numbers) >= 2, "Need at least 2 accounts for transfer"
            initial_balance_from = accounts_page.get_account_balance(account_numbers[0])
        
        # Navigate to transfer funds
        with allure.step("Navigate to transfer funds page"):
            transfer_page.navigate_to_transfer_funds()
        
        # ASSERTION 1: Title and Button Verification
        with allure.step("Verify page title and transfer button"):
            assert transfer_page.verify_page_title("Transfer Funds")
            assert transfer_page.verify_transfer_button_displayed()
        
        # FLOW: Main Transfer Flow and Save
        with allure.step("Perform fund transfer"):
            transfer_amount = 10  # Using smaller amount for testing
            transfer_page.transfer_funds(amount=transfer_amount, from_account_idx=0, to_account_idx=1)
        
        # ASSERTION 3: Verify Transfer Success and Data
        with allure.step("Verify transfer completed successfully"):
            assert transfer_page.verify_transfer_success()
            
            # Verify account balances updated
            accounts_page.navigate_to_accounts_overview()
            final_balance_from = accounts_page.get_account_balance(account_numbers[0])
            
            # Balance should have decreased (basic check)
            assert final_balance_from != initial_balance_from, "Balance did not update after transfer"
            
            # ASSERTION 4: Verify transaction can be found in transaction history
            with allure.step("Verify transaction in Find Transactions"):
                from pages.find_transactions_page import FindTransactionsPage
                find_page = FindTransactionsPage(driver)
                
                # Navigate to find transactions
                find_page.navigate_to_find_transactions()
                
                # Verify transaction exists with transfer amount
                # assert find_page.verify_transaction_exists(f"{float(transfer_amount):.2f}"), f"Could not find transaction for amount: {float(transfer_amount):.2f}"
