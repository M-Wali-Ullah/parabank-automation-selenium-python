"""
Pytest configuration and fixtures
"""
import pytest
import allure
from datetime import datetime
import uuid
import time
from faker import Faker
from selenium.common.exceptions import WebDriverException

from config.config import Config
from utils.driver_factory import DriverFactory
from utils.logger import get_logger
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
import os

logger = get_logger(__name__)
fake = Faker()


@pytest.fixture(scope="session", autouse=True)
def setup_directories():
    """Ensure all necessary directories exist"""
    Config.ensure_directories()
    logger.info("Test directories initialized")


@pytest.fixture(scope="function")
def driver(request):
    """
    Fixture to initialize and quit WebDriver
    Scope: function - creates new driver for each test
    """
    logger.info(f"Initializing WebDriver for test: {request.node.name}")
    
    driver_instance = None
    try:
        driver_instance = DriverFactory.get_driver()
        driver_instance.maximize_window()
        
        yield driver_instance
        
    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
        raise
    
    finally:
        if driver_instance:
            logger.info(f"Closing WebDriver for test: {request.node.name}")
            driver_instance.quit()


@pytest.fixture(scope="function")
def login_page(driver):
    """Fixture for LoginPage"""
    page = LoginPage(driver)
    page.navigate_to_login()
    return page


@pytest.fixture(scope="function")
def register_page(driver):
    """Fixture for RegisterPage"""
    page = RegisterPage(driver)
    page.navigate_to_login()
    return page


@pytest.fixture(scope="function")
def generate_user_data():
    """Generate random user data for registration"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # include milliseconds
    unique_suffix = uuid.uuid4().hex[:6]

    # Simpler unique username: timestamp + short uuid suffix
    username = f"robo_{unique_suffix}"

    user_data = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'zip_code': fake.zipcode(),
        'phone': fake.numerify(text='###-###-####'),
        'ssn': fake.ssn(),
        'username': username,
        'password': Config.DEFAULT_PASSWORD
    }
    
    logger.info(f"Generated test user data: {user_data['username']}")
    return user_data


@pytest.fixture(scope="function")
def registered_user(driver, generate_user_data):
    """
    Fixture that registers a new user and returns credentials
    Use this when you need a fresh registered user for testing
    """
    register_page = RegisterPage(driver)
    login_page = LoginPage(driver)
    
    # Navigate and register with retry if username collision occurs
    attempts = 0
    success = False
    while attempts < Config.MAX_RETRY_ATTEMPTS and not success:
        attempts += 1
        logger.info(f"Registration attempt {attempts} for user: {generate_user_data['username']}")

        login_page.navigate_to_login()
        register_page.navigate_to_register()
        register_page.fill_registration_form(generate_user_data)
        register_page.submit_registration()

        # If username-specific error is present, regenerate username and retry
        try:
            if register_page.is_displayed(register_page.USERNAME_ERROR, timeout=2):
                logger.warning(f"Username collision detected for {generate_user_data['username']}. Retrying with a new username.")
                # regenerate a short unique suffix and update username (simpler)
                new_suffix = uuid.uuid4().hex[:6]
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
                generate_user_data['username'] = f"testuser_{timestamp}_{new_suffix}"
                # small delay before retry
                time.sleep(1)
                continue
        except Exception:
            # If checking the username error raised, ignore and try to verify success below
            pass

        # Verify registration by message; if that fails, attempt to login as a fallback
        try:
            register_page.verify_registration_success(generate_user_data['username'])
            success = True
        except Exception:
            logger.warning(f"Registration success message not found for {generate_user_data['username']}, attempting login as fallback check")
            try:
                # try logging in to verify the account was created
                login_page.navigate_to_login()
                login_page.login(generate_user_data['username'], generate_user_data['password'])
                login_page.verify_login_success()
                logger.info(f"Verified registration by logging in as {generate_user_data['username']}")
                success = True
            except Exception:
                logger.warning(f"Fallback login verification failed for {generate_user_data['username']}")
                time.sleep(1)

    if not success:
        raise RuntimeError(f"Failed to register unique user after {Config.MAX_RETRY_ATTEMPTS} attempts")
    
    logger.info(f"Registered test user: {generate_user_data['username']}")
    
    return {
        'username': generate_user_data['username'],
        'password': generate_user_data['password'],
        'full_data': generate_user_data
    }


@pytest.fixture(scope="function")
def logged_in_user(driver, request):
    """
    Fixture that provides a logged-in user session.
    Priority:
    1. Use temp credentials if available
    2. If not found or login fails, register new user (auto-logs in)
    """
    login_page = LoginPage(driver)
    register_page = RegisterPage(driver)
    
    # Try to load existing credentials first
    saved_credentials = Config.load_temp_credentials()

    if saved_credentials:
        try:
            logger.info(f"Found saved credentials for user: {saved_credentials['username']}")
            login_page.navigate_to_login()
            login_page.login(saved_credentials['username'], saved_credentials['password'])
            if login_page.verify_login_success():
                logger.info("Successfully logged in with saved credentials")
                return saved_credentials
            logger.warning("Login with saved credentials failed")
        except Exception as e:
            logger.error(f"Error using saved credentials: {str(e)}")

    logger.info("No usable saved credentials found; attempting to create or wait for credentials")

    from utils.test_helper import register_and_login_user

    # Try to acquire lock to register a new user. If another worker is registering,
    # wait for the credentials file to appear instead.
    lock_acquired = Config.acquire_temp_creds_lock(timeout=30)
    try:
        if lock_acquired:
            # double-check in case a race caused creds to be created just before lock
            saved_credentials = Config.load_temp_credentials()
            if saved_credentials:
                try:
                    login_page.navigate_to_login()
                    login_page.login(saved_credentials['username'], saved_credentials['password'])
                    if login_page.verify_login_success():
                        logger.info("Successfully logged in with credentials created by another worker")
                        return saved_credentials
                except Exception:
                    pass

            # Register a new user and save credentials
            logger.info("Registering new user...")
            credentials = register_and_login_user(driver)
            return credentials
        else:
            # Could not acquire lock; wait for the credentials file to appear
            logger.info("Another worker may be creating credentials; waiting for file to appear")
            wait_deadline = time.time() + 30
            while time.time() < wait_deadline:
                saved_credentials = Config.load_temp_credentials()
                if saved_credentials:
                    try:
                        login_page.navigate_to_login()
                        login_page.login(saved_credentials['username'], saved_credentials['password'])
                        if login_page.verify_login_success():
                            logger.info("Successfully logged in with credentials created by another worker")
                            return saved_credentials
                    except Exception:
                        pass
                time.sleep(1)
            raise RuntimeError("Timed out waiting for temp credentials to be created by another worker")
    finally:
        if lock_acquired:
            Config.release_temp_creds_lock()


@pytest.fixture(scope="function")
def bill_payment_data():
    """Generate bill payment test data"""
    return {
        'payee_name': fake.company(),
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state_abbr(),
        'zip_code': fake.zipcode(),
        'phone': fake.numerify(text='###-###-####'),
        'account_number': fake.numerify(text='##########'),
        'amount': fake.numerify(text='###.##')
    }


# Pytest hooks for better reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results and take screenshots on failure
    """
    outcome = yield
    report = outcome.get_result()
    
    # Add test result to item for use in fixtures
    setattr(item, f"report_{report.when}", report)
    
    # Take screenshot on test failure
    if report.when == "call" and report.failed:
        driver = item.funcargs.get('driver')
        if driver:
            try:
                test_name = item.name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_name = f"{test_name}_{timestamp}_FAILED"
                
                # Save screenshot
                Config.ensure_directories()
                screenshot_path = Config.SCREENSHOTS_DIR / f"{screenshot_name}.png"
                driver.save_screenshot(str(screenshot_path))
                
                # Attach to Allure report
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name=screenshot_name,
                    attachment_type=allure.attachment_type.PNG
                )
                
                logger.error(f"Test failed: {test_name}. Screenshot saved: {screenshot_name}")
                
            except Exception as e:
                logger.error(f"Failed to take screenshot: {str(e)}")


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "smoke: Mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: Mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "critical: Mark test as critical path test"
    )


@pytest.fixture(scope="session", autouse=True)
def test_execution_logger():
    """Log test execution start and end, and cleanup temp files"""
    logger.info("=" * 80)
    logger.info("TEST EXECUTION STARTED")
    logger.info("=" * 80)
    
    yield
    
    # Clean up temp credentials unless user requested persistence across runs
    keep = os.getenv("KEEP_TEMP_CREDS", "true").lower()
    if keep not in ("1", "true", "yes"):
        Config.clear_temp_credentials()
    
    logger.info("=" * 80)
    logger.info("TEST EXECUTION COMPLETED")
    logger.info("=" * 80)