"""
Test Suite: Bill Payment Processing
"""
import pytest
import allure
from pages.bill_pay_page import BillPayPage


@allure.epic("Banking Operations")
@allure.feature("Bill Payment")
@pytest.mark.regression
@pytest.mark.transactions
class TestBillPayment:
    
    @allure.title("Test 03: Complete Bill Payment Processing")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_complete_bill_payment(self, driver, logged_in_user, bill_payment_data):
        """Test complete bill payment with all validations"""
        
        bill_pay_page = BillPayPage(driver)
        
        # Navigate to bill pay
        with allure.step("Navigate to bill payment page"):
            bill_pay_page.navigate_to_bill_pay()
        
        # ASSERTION 1: Title and Button Verification
        with allure.step("Verify page title and send payment button"):
            assert bill_pay_page.verify_page_title("Bill Payment Service")
            assert bill_pay_page.verify_send_payment_button_displayed()
        
        # ASSERTION 2: Mandatory Field Validation
        with allure.step("Verify mandatory fields validation"):
            assert bill_pay_page.verify_mandatory_fields(), "Mandatory field validation failed"
        
        # FLOW: Main Bill Payment Flow and Save
        with allure.step("Fill and submit bill payment"):
            bill_pay_page.fill_bill_payment_form(bill_payment_data)
            bill_pay_page.submit_bill_payment()
        
        # ASSERTION 3: Verify Payment Success and Data
        with allure.step("Verify bill payment completed successfully"):
            assert bill_pay_page.verify_payment_success(
                bill_payment_data['payee_name'],
                bill_payment_data['amount']
            )