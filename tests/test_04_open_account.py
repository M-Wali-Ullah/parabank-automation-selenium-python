"""
Test Suite: New Account Opening
"""
import pytest
import allure
from pages.open_account_page import OpenAccountPage
from pages.accounts_overview_page import AccountsOverviewPage


@allure.epic("Account Management")
@allure.feature("Account Creation")
@pytest.mark.regression
@pytest.mark.account_operations
class TestOpenAccount:
    
    @allure.title("Test 04: Open New Savings Account")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_open_new_account(self, driver, logged_in_user):
        """Test complete new account opening with all validations"""
        
        open_account_page = OpenAccountPage(driver)
        accounts_page = AccountsOverviewPage(driver)
        
        # Get initial account count
        with allure.step("Get initial account count"):
            accounts_page.navigate_to_accounts_overview()
            initial_accounts = accounts_page.get_account_numbers()
            initial_count = len(initial_accounts)
        
        # Navigate to open account
        with allure.step("Navigate to open new account page"):
            open_account_page.navigate_to_open_account()
        
        # ASSERTION 1: Title and Button Verification
        with allure.step("Verify page title and open account button"):
            assert open_account_page.verify_page_title("Open New Account")
            assert open_account_page.verify_open_account_button_displayed()
        
        # ASSERTION 2: Mandatory Field Validation (Account Type)
        with allure.step("Verify account type selection is available"):
            # Verify dropdown exists and has options
            assert open_account_page.is_displayed(open_account_page.ACCOUNT_TYPE_DROPDOWN)
            assert open_account_page.is_displayed(open_account_page.FROM_ACCOUNT_DROPDOWN)
        
        # FLOW: Main Account Opening Flow and Save
        with allure.step("Open new savings account"):
            open_account_page.open_new_account(account_type="SAVINGS")
        
        # ASSERTION 3: Verify Account Creation Success and Data
        with allure.step("Verify new account created successfully"):
            new_account_number = open_account_page.verify_account_creation_success()
            assert new_account_number, "New account number not returned"
            
            # Verify new account appears in accounts overview
            accounts_page.navigate_to_accounts_overview()
            updated_accounts = accounts_page.get_account_numbers()
            final_count = len(updated_accounts)
            
            assert final_count == initial_count + 1, "New account not added to accounts list"
            assert new_account_number in updated_accounts, "New account number not found in list"