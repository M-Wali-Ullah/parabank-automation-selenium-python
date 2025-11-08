"""
Transfer Funds Page Object
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger
from config.config import Config
import allure

logger = get_logger(__name__)


class TransferFundsPage(BasePage):
    """Page object for fund transfer"""
    
    # Locators
    TRANSFER_FUNDS_LINK = (By.LINK_TEXT, "Transfer Funds")
    PAGE_TITLE = (By.CSS_SELECTOR, "h1.title")
    AMOUNT_INPUT = (By.ID, "amount")
    FROM_ACCOUNT_DROPDOWN = (By.ID, "fromAccountId")
    TO_ACCOUNT_DROPDOWN = (By.ID, "toAccountId")
    TRANSFER_BUTTON = (By.CSS_SELECTOR, "input[value='Transfer']")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "div#showResult h1.title")
    TRANSFER_COMPLETE_TEXT = (By.CSS_SELECTOR, "div#showResult p")
    # Use multiple possible error selectors
    AMOUNT_ERROR = (By.CSS_SELECTOR, "#amount.errors, #errors, .error, span.error")
    
    @allure.step("Navigate to transfer funds page")
    def navigate_to_transfer_funds(self):
        """Navigate to transfer funds page"""
        logger.info("Navigating to transfer funds page")
        self.click(self.TRANSFER_FUNDS_LINK)
    
    @allure.step("Verify transfer funds page title")
    def verify_page_title(self, expected="Transfer Funds"):
        """Verify transfer funds page title"""
        actual_title = self.get_text(self.PAGE_TITLE)
        assert expected in actual_title, f"Expected '{expected}' but got '{actual_title}'"
        logger.info(f"Page title verified: {actual_title}")
        return True
    
    @allure.step("Verify transfer button is displayed")
    def verify_transfer_button_displayed(self):
        """Verify transfer button is visible"""
        is_displayed = self.is_displayed(self.TRANSFER_BUTTON)
        assert is_displayed, "Transfer button is not displayed"
        logger.info("Transfer button is displayed")
        return True
    
    @allure.step("Verify amount field is mandatory")
    def verify_amount_field_mandatory(self):
        """Verify amount field shows error when empty"""
        try:
            # Wait for the form to be visible
            self.wait_for_visibility((By.ID, "transferForm"))
            
            # Enter empty amount (just focus and blur)
            amount_field = self.find_element(self.AMOUNT_INPUT)
            amount_field.click()
            amount_field.clear()
            
            # Click transfer button to trigger validation
            self.click(self.TRANSFER_BUTTON)
            
            # Wait a moment for any client-side validation
            self.driver.implicitly_wait(1)
            
            # Look for validation error - try multiple approaches
            error_found = False
            
            # Check for error class on input field
            if "error" in amount_field.get_attribute("class"):
                logger.info("Amount field has error class")
                error_found = True
            
            # Check for error messages
            try:
                error_div = self.find_element(self.AMOUNT_ERROR)
                if error_div.is_displayed():
                    error_text = error_div.text.strip()
                    logger.info(f"Found error message: {error_text}")
                    if error_text and any(keyword in error_text.lower() for keyword in ['required', 'empty', 'invalid']):
                        error_found = True
            except:
                pass
            
            # Check if form submission was prevented (we should still be on transfer page)
            if "transfer.htm" in self.driver.current_url:
                error_found = True
                
            if not error_found:
                logger.warning("No validation error detected for empty amount field")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking amount validation: {str(e)}")
            logger.info("Page source: " + self.driver.page_source)
            return False
    
    @allure.step("Transfer amount: {amount}")
    def transfer_funds(self, amount, from_account_idx=0, to_account_idx=1):
        """
        Transfer funds between accounts
        
        Args:
            amount: Amount to transfer (numeric value)
            from_account_idx: Index of source account in dropdown
            to_account_idx: Index of destination account in dropdown
        """
        logger.info(f"Transferring amount: {amount}")
        
        # Wait for form elements to be ready
        self.wait_for_visibility(self.AMOUNT_INPUT)
        self.wait_for_visibility(self.FROM_ACCOUNT_DROPDOWN)
        self.wait_for_visibility(self.TO_ACCOUNT_DROPDOWN)
        
        # Enter amount first. Accept numeric input (int/float or numeric string).
        # Store formatted amount (with $ and two decimals) for later verification.
        try:
            amt_val = float(amount)
        except Exception:
            # If conversion fails, try to strip non-numeric and convert
            cleaned = ''.join(ch for ch in str(amount) if (ch.isdigit() or ch == '.'))
            amt_val = float(cleaned)
        formatted_amount = f"${amt_val:.2f}"
        # keep for verification
        self._last_transfer_amount = formatted_amount

        # Debug: inspect the amount input before trying to set value
        try:
            amount_elem = self.find_element(self.AMOUNT_INPUT)
            try:
                displayed = amount_elem.is_displayed()
            except Exception:
                displayed = 'unknown'
            try:
                enabled = amount_elem.is_enabled()
            except Exception:
                enabled = 'unknown'
            attrs = {}
            for a in ('readonly', 'class', 'type', 'style', 'value', 'placeholder'):
                try:
                    attrs[a] = amount_elem.get_attribute(a)
                except Exception:
                    attrs[a] = None

            # outerHTML via JS for full context
            try:
                outer = self.driver.execute_script('return arguments[0].outerHTML;', amount_elem)
            except Exception:
                outer = None

            logger.info(f"Amount input debug - displayed={displayed}, enabled={enabled}, attrs={attrs}")
            if outer:
                logger.debug(f"Amount input outerHTML: {outer}")
        except Exception as e:
            logger.warning(f"Could not locate amount input for debug: {e}")

        # Try to set the amount with explicit focus, click and slow typing
        try:
            # Find and ensure the amount field is ready
            amount_field = self.wait_for_visibility(self.AMOUNT_INPUT)
            
            # Try multiple ways to focus the field
            try:
                amount_field.click()
                self.driver.execute_script("arguments[0].focus();", amount_field)
                self.driver.implicitly_wait(1)  # Small wait after focus
            except Exception as focus_e:
                logger.warning(f"Focus attempt failed: {focus_e}")
            
            self.enter_text(self.AMOUNT_INPUT, str(amt_val), slow_typing=True)
            logger.info("Amount set by normal entry with slow typing")
        except Exception as e:
            logger.warning(f"Normal entry failed for amount: {e}. Attempting JS fallback and capturing debug artifacts.")
            # capture screenshot and page source for debugging
            try:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_name = f"amount_input_failure_{timestamp}"
                try:
                    self.take_screenshot(screenshot_name)
                except Exception:
                    # fallback: direct save
                    try:
                        Config.ensure_directories()
                        ss_path = Config.SCREENSHOTS_DIR / f"{screenshot_name}.png"
                        self.driver.save_screenshot(str(ss_path))
                    except Exception:
                        pass

                # save page source
                try:
                    Config.ensure_directories()
                    ps_path = Config.REPORTS_DIR / f"{screenshot_name}.html"
                    with open(ps_path, 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                except Exception:
                    pass
            except Exception:
                pass

            # JS fallback
            try:
                field_id = self.AMOUNT_INPUT[1]
                js = (
                    "var el = document.getElementById(arguments[0]);"
                    "if(el){ el.value = arguments[1]; el.dispatchEvent(new Event('input')); el.dispatchEvent(new Event('change')); }"
                )
                self.driver.execute_script(js, field_id, str(amt_val))
                logger.info(f"Set amount via JS fallback: {amt_val}")
            except Exception as js_e:
                logger.error(f"Failed to set amount via JS: {js_e}")
                raise
        
        # Wait for any dynamic updates after amount entry and ensure form is ready
        self.driver.implicitly_wait(2)
        
        # Select source account with proper waits and retries
        from selenium.webdriver.support.ui import Select
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Wait for dropdown to be both present and interactive
                from_elem = self.wait_for_clickable(self.FROM_ACCOUNT_DROPDOWN, timeout=10)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", from_elem)
                self.driver.implicitly_wait(1)
                
                from_dropdown = Select(from_elem)
                from_dropdown.select_by_index(from_account_idx)
                logger.info(f"Successfully selected from account at index {from_account_idx}")
                break
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed to select from account: {e}")
                if attempt < max_retries - 1:
                    self.driver.implicitly_wait(2)
                else:
                    raise Exception(f"Failed to select from account after {max_retries} attempts: {last_error}")
        
        # Small wait between selections to avoid any race conditions
        self.driver.implicitly_wait(1)
        
        # Select destination account
        to_dropdown = Select(self.wait_for_clickable(self.TO_ACCOUNT_DROPDOWN))
        to_dropdown.select_by_index(to_account_idx)
        
        # Submit transfer
        self.wait_for_clickable(self.TRANSFER_BUTTON).click()
        logger.info("Transfer submitted")
    
    @allure.step("Verify transfer success")
    def verify_transfer_success(self):
        """Verify transfer completed successfully"""
        # Verify the success container exists and is visible
        # Wait for the showResult container
        result_div = self.wait_for_visibility((By.CSS_SELECTOR, "div#showResult"))

        # style should be empty (visible)
        style_attr = result_div.get_attribute('style') or ''
        assert style_attr.strip() == '', f"Expected result container to be visible with empty style, got: '{style_attr}'"

        # h1.title should contain Transfer Complete
        success_msg = self.get_text(self.SUCCESS_MESSAGE)
        assert "Transfer Complete" in success_msg, f"Transfer failed. Message: {success_msg}"

        # Verify amount and account ids populated as expected
        amount_span = self.find_element((By.ID, 'amountResult'))
        from_span = self.find_element((By.ID, 'fromAccountIdResult'))
        to_span = self.find_element((By.ID, 'toAccountIdResult'))

        amount_text = amount_span.text.strip()
        logger.info(f"Amount in result: {amount_text}")

        # If we recorded the last transfer amount, compare; otherwise ensure a dollar value is present
        if hasattr(self, '_last_transfer_amount'):
            assert amount_text == self._last_transfer_amount, f"Amount mismatch: expected {self._last_transfer_amount} but found {amount_text}"
        else:
            assert amount_text.startswith('$'), f"Expected dollar amount in result but found '{amount_text}'"

        # Basic checks for account ids
        from_id = from_span.text.strip()
        to_id = to_span.text.strip()
        assert from_id.isdigit() and to_id.isdigit(), f"Account ids missing or invalid: from={from_id}, to={to_id}"

        logger.info(f"Transfer successful: amount={amount_text}, from={from_id}, to={to_id}")
        return True