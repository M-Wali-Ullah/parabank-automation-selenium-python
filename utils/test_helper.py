"""
Test helper functions
"""
from datetime import datetime
import uuid
from faker import Faker
from utils.logger import get_logger
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from config.config import Config

logger = get_logger(__name__)


def register_and_login_user(driver, user_data=None):
    """
    Helper function to register a new user and ensure they are logged in
    If no user_data is provided, generates random data.
    Returns the credentials on success
    """
    if user_data is None:
        from datetime import datetime
        import uuid
        from faker import Faker
        fake = Faker()
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        unique_suffix = uuid.uuid4().hex[:6]
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
    register_page = RegisterPage(driver)
    login_page = LoginPage(driver)
    
    # Navigate and register
    register_page.navigate_to_register()
    register_page.fill_registration_form(user_data)
    register_page.submit_registration()
    
    # Verify registration success
    register_page.verify_registration_success(user_data['username'])
    
    # Save credentials for use in subsequent tests
    credentials = {
        'username': user_data['username'],
        'password': user_data['password'],
        'full_data': user_data
    }
    Config.save_temp_credentials(credentials)
    
    logger.info(f"Registered and saved credentials for test user: {user_data['username']}")
    return credentials