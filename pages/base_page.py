"""
Base Page class with common methods for all page objects
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from config.config import Config
from utils.logger import get_logger
import allure

logger = get_logger(__name__)


class BasePage:
    """Base page class with common methods"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.EXPLICIT_WAIT)
    
    @allure.step("Navigate to URL: {url}")
    def navigate_to(self, url):
        """Navigate to specified URL"""
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)
    
    @allure.step("Find element: {locator}")
    def find_element(self, locator, timeout=None):
        """Find element with explicit wait"""
        try:
            wait_time = timeout or Config.EXPLICIT_WAIT
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.presence_of_element_located(locator))
            logger.debug(f"Element found: {locator}")
            return element
        except TimeoutException:
            logger.error(f"Element not found: {locator}")
            raise
    
    @allure.step("Find elements: {locator}")
    def find_elements(self, locator):
        """Find multiple elements"""
        return self.driver.find_elements(*locator)
    
    @allure.step("Click element: {locator}")
    def click(self, locator):
        """Click on element"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        logger.info(f"Clicked element: {locator}")
    
    @allure.step("Enter text: '{text}' into {locator}")
    def enter_text(self, locator, text, slow_typing=False):
        """Enter text into input field with optional slow typing"""
        import time
        
        # Wait before interacting with the element
        time.sleep(1)
        
        # Wait until the element is visible and clickable before sending keys
        element = None
        for attempt in range(3):  # Try up to 3 times
            try:
                # Scroll element into view first
                try:
                    temp_element = self.find_element(locator)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", temp_element)
                    time.sleep(0.5)  # Wait for scroll
                except Exception as scroll_e:
                    logger.warning(f"Scroll into view failed: {scroll_e}")
                
                element = self.wait_for_clickable(locator)
                # Try to focus the element
                try:
                    self.driver.execute_script("arguments[0].focus();", element)
                    time.sleep(0.5)
                except Exception as focus_e:
                    logger.warning(f"Focus attempt failed: {focus_e}")
                break
            except Exception as e:
                if attempt == 2:  # Last attempt
                    # Final fallback to just finding the element
                    element = self.wait_for_visibility(locator)
                    logger.warning(f"Fallback to visible element after clickable attempts failed")
                else:
                    logger.warning(f"Attempt {attempt + 1} to get clickable element failed: {e}")
                    time.sleep(1)
        
        if not element:
            raise Exception(f"Could not interact with element: {locator}")
            
        try:
            element.clear()
            time.sleep(0.5)  # Wait after clearing
        except ElementNotInteractableException:
            # element can't be cleared via Selenium; fallback to JS clear
            try:
                self.driver.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input'));", element)
                logger.warning(f"Used JS fallback to clear text for {locator}")
                time.sleep(0.5)  # Wait after JS clear
            except Exception as js_e:
                logger.error(f"Failed to clear via JS for {locator}: {js_e}")
                raise

        try:
            if slow_typing:
                # Try a more robust JS approach first for numeric inputs
                try:
                    # Focus the element
                    self.driver.execute_script("arguments[0].focus();", element)
                    time.sleep(0.5)
                    
                    # Clear using JavaScript
                    self.driver.execute_script(
                        "arguments[0].value = ''; " +
                        "arguments[0].dispatchEvent(new Event('input')); " +
                        "arguments[0].dispatchEvent(new Event('change'));",
                        element
                    )
                    time.sleep(0.5)
                    
                    # Type each character with proper events
                    current_text = ""
                    for char in text:
                        current_text += char
                        self.driver.execute_script(
                            "arguments[0].value = arguments[1];" +
                            "arguments[0].dispatchEvent(new Event('input'));" +
                            "arguments[0].dispatchEvent(new Event('change'));",
                            element, current_text
                        )
                        time.sleep(0.2)  # 200ms delay between characters
                        
                    # Final blur event
                    self.driver.execute_script(
                        "arguments[0].dispatchEvent(new Event('change')); " +
                        "arguments[0].blur();",
                        element
                    )
                    logger.info(f"Set text via enhanced JS approach: {text}")
                    
                except Exception as js_e:
                    logger.warning(f"Enhanced JS input failed: {js_e}, trying normal typing")
                    # Fall back to normal character-by-character typing
                    element.clear()
                    time.sleep(0.5)
                    for char in text:
                        element.send_keys(char)
                        time.sleep(0.2)  # 200ms delay
            else:
                element.send_keys(text)
                
        except ElementNotInteractableException as e:
            logger.error(f"Element not interactable: {e}")
            raise
                
        # Wait after entering text
        time.sleep(1)
        logger.info(f"Entered text into {locator}")
    
    @allure.step("Get text from element: {locator}")
    def get_text(self, locator):
        """Get text from element"""
        element = self.find_element(locator)
        text = element.text
        logger.debug(f"Got text from {locator}: {text}")
        return text
    
    @allure.step("Get attribute '{attribute}' from element: {locator}")
    def get_attribute(self, locator, attribute):
        """Get attribute value from element"""
        element = self.find_element(locator)
        return element.get_attribute(attribute)
    
    @allure.step("Check if element is displayed: {locator}")
    def is_displayed(self, locator, timeout=5):
        """Check if element is displayed"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located(locator))
            return element.is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False
    
    @allure.step("Check if element is enabled: {locator}")
    def is_enabled(self, locator):
        """Check if element is enabled"""
        element = self.find_element(locator)
        return element.is_enabled()
    
    @allure.step("Wait for element to be visible: {locator}")
    def wait_for_visibility(self, locator, timeout=None):
        """Wait for element to be visible"""
        wait_time = timeout or Config.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.visibility_of_element_located(locator))
    
    @allure.step("Wait for element to be clickable: {locator}")
    def wait_for_clickable(self, locator, timeout=None):
        """Wait for element to be clickable"""
        wait_time = timeout or Config.EXPLICIT_WAIT
        wait = WebDriverWait(self.driver, wait_time)
        return wait.until(EC.element_to_be_clickable(locator))
    
    @allure.step("Get page title")
    def get_page_title(self):
        """Get current page title"""
        title = self.driver.title
        logger.info(f"Page title: {title}")
        return title
    
    @allure.step("Get current URL")
    def get_current_url(self):
        """Get current URL"""
        url = self.driver.current_url
        logger.info(f"Current URL: {url}")
        return url
    
    @allure.step("Select dropdown by visible text: '{text}'")
    def select_dropdown_by_text(self, locator, text):
        """Select dropdown option by visible text"""
        from selenium.webdriver.support.ui import Select
        element = self.find_element(locator)
        select = Select(element)
        select.select_by_visible_text(text)
        logger.info(f"Selected '{text}' from dropdown")
    
    @allure.step("Take screenshot: {name}")
    def take_screenshot(self, name):
        """Take screenshot and attach to Allure report"""
        Config.ensure_directories()
        screenshot_path = Config.SCREENSHOTS_DIR / f"{name}.png"
        self.driver.save_screenshot(str(screenshot_path))
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        logger.info(f"Screenshot saved: {name}")