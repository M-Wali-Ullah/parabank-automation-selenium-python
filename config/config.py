"""
Configuration Management for ParaBank Test Automation
"""
import os
import json
from pathlib import Path
import tempfile
import os
import time

class Config:
    """Central configuration management"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    REPORTS_DIR = BASE_DIR / "reports"
    SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Application URL
    BASE_URL = "https://parabank.parasoft.com/parabank"
    
    # Browser settings
    BROWSER = os.getenv("BROWSER", "chrome")  # chrome, firefox, edge
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    IMPLICIT_WAIT = 5
    EXPLICIT_WAIT = 10
    PAGE_LOAD_TIMEOUT = 15
    
    # Screenshot settings
    SCREENSHOT_ON_FAILURE = True
    
    # Retry settings
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY = 2
    
    # Test data
    DEFAULT_USERNAME_PREFIX = "testuser"
    DEFAULT_PASSWORD = "Test@123"
    TEMP_CREDS_FILE = BASE_DIR / "config" / "temp_credentials.json"
    TEMP_CREDS_LOCK = BASE_DIR / "config" / "temp_credentials.lock"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def save_temp_credentials(cls, credentials):
        """Save credentials to temporary file"""
        # Write atomically to avoid partial writes when multiple workers run
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(cls.TEMP_CREDS_FILE.parent))
        try:
            with os.fdopen(tmp_fd, 'w') as f:
                json.dump(credentials, f)
            # Atomic replace
            os.replace(tmp_path, str(cls.TEMP_CREDS_FILE))
        finally:
            # Ensure temporary file removed if something failed
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
    
    @classmethod
    def load_temp_credentials(cls):
        """Load credentials from temporary file"""
        try:
            if not cls.TEMP_CREDS_FILE.exists():
                return None
            with open(cls.TEMP_CREDS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    @classmethod
    def clear_temp_credentials(cls):
        """Clear temporary credentials file"""
        if cls.TEMP_CREDS_FILE.exists():
            cls.TEMP_CREDS_FILE.unlink()

    @classmethod
    def acquire_temp_creds_lock(cls, timeout=30, poll_interval=0.5):
        """
        Acquire a simple file-based lock for writing temp credentials.
        Returns True if lock acquired within timeout, False otherwise.
        """
        start = time.time()
        while True:
            try:
                # Use os.O_CREAT | os.O_EXCL to create the lock file atomically
                fd = os.open(str(cls.TEMP_CREDS_LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return True
            except FileExistsError:
                # Lock already exists
                if time.time() - start >= timeout:
                    return False
                time.sleep(poll_interval)

    @classmethod
    def release_temp_creds_lock(cls):
        """Release the simple file-based lock"""
        try:
            if cls.TEMP_CREDS_LOCK.exists():
                cls.TEMP_CREDS_LOCK.unlink()
        except Exception:
            pass