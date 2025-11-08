"""
WebDriver Factory for browser initialization
"""
import os
import sys
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from config.config import Config


class DriverFactory:
    """Factory class for creating WebDriver instances"""
    
    @staticmethod
    def get_driver(browser=None):
        """
        Get WebDriver instance based on browser type
        
        Args:
            browser (str): Browser name (chrome, firefox, edge)
            
        Returns:
            WebDriver: Configured WebDriver instance
        """
        browser = browser or Config.BROWSER
        browser = browser.lower()
        
        if browser == "chrome":
            return DriverFactory._get_chrome_driver()
        elif browser == "firefox":
            return DriverFactory._get_firefox_driver()
        elif browser == "edge":
            return DriverFactory._get_edge_driver()
        else:
            raise ValueError(f"Unsupported browser: {browser}")
    
    @staticmethod
    def _get_chrome_version():
        """Get the installed Chrome version"""
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                return version
            except:
                return None
        return None

    @staticmethod
    def _get_chrome_driver():
        """Configure and return Chrome WebDriver"""
        options = webdriver.ChromeOptions()
        
        if Config.HEADLESS:
            options.add_argument("--headless=new")
        
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        try:
            # Download specific version of ChromeDriver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Create Chrome service with specific settings
            service = Service()
            
            # Set up logging
            if not os.path.exists(Config.LOGS_DIR):
                os.makedirs(Config.LOGS_DIR)
            service.log_file = os.path.join(Config.LOGS_DIR, "chromedriver.log")
            
            # Create and return the driver instance
            driver = webdriver.Chrome(options=options)
            
            DriverFactory._configure_driver(driver)
            return driver
            
        except Exception as e:
            print(f"✗ Error initializing Chrome driver: {str(e)}")
            print(f"✗ Additional info: Python: {sys.version}, OS: {os.name}, Platform: {sys.platform}")
            raise
    
    @staticmethod
    def _get_firefox_driver():
        """Configure and return Firefox WebDriver"""
        options = webdriver.FirefoxOptions()
        
        if Config.HEADLESS:
            options.add_argument("--headless")
        
        try:
            gecko_driver_path = GeckoDriverManager().install()
            
            if not os.path.exists(gecko_driver_path):
                raise FileNotFoundError(f"GeckoDriver not found at: {gecko_driver_path}")
            
            print(f"✓ Using GeckoDriver: {gecko_driver_path}")
            
            service = FirefoxService(gecko_driver_path)
            driver = webdriver.Firefox(service=service, options=options)
            driver.maximize_window()
            
            DriverFactory._configure_driver(driver)
            return driver
            
        except Exception as e:
            print(f"✗ Error initializing Firefox driver: {str(e)}")
            raise
    
    @staticmethod
    def _get_edge_driver():
        """Configure and return Edge WebDriver"""
        options = webdriver.EdgeOptions()
        
        if Config.HEADLESS:
            options.add_argument("--headless")
        
        options.add_argument("--start-maximized")
        
        try:
            # Download EdgeDriver
            edge_driver_path = EdgeChromiumDriverManager().install()
            
            if not os.path.exists(edge_driver_path):
                raise FileNotFoundError(f"EdgeDriver not found at: {edge_driver_path}")
            
            print(f"✓ Using EdgeDriver: {edge_driver_path}")
            
            service = EdgeService(edge_driver_path)
            driver = webdriver.Edge(service=service, options=options)
            
            DriverFactory._configure_driver(driver)
            return driver
            
        except Exception as e:
            print(f"✗ Error initializing Edge driver: {str(e)}")
            raise
    
    @staticmethod
    def _configure_driver(driver):
        """Apply common configurations to WebDriver"""
        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)