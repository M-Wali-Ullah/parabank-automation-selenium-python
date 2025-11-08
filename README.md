# ParaBank Test Automation Framework

## Overview

This test automation framework provides end-to-end testing for ParaBank, a demo banking application. It addresses several key challenges in banking application testing:

- **User Management**: Automates account registration and login flows with credential management
- **Banking Operations**: Tests critical banking functions like funds transfer and bill payments
- **Transaction Verification**: Validates financial transactions across accounts
- **Data Validation**: Ensures accurate processing of monetary transactions and account balances
- **Session Management**: Handles user sessions efficiently across test scenarios
- **Test Data Management**: Provides dynamic test data generation and persistence
- **Cross-browser Testing**: Supports Chrome, Firefox, and Edge browsers
- **Reporting**: Generates detailed Allure reports with screenshots for failed tests
- **Logging**: Comprehensive logging for better debugging and audit trails
- **Reusability**: Modular design with page objects and shared utilities

## Project Structure

```
parabank-automation/
├── config/                     # Configuration management
│   ├── config.py              # Central configuration
│   └── test_data.json         # Test data
├── logs/                      # Test execution logs
├── pages/                     # Page Object Models
│   ├── accounts_overview_page.py
│   ├── base_page.py          # Base page with common actions
│   ├── bill_pay_page.py
│   ├── find_transactions_page.py
│   ├── login_page.py
│   ├── open_account_page.py
│   ├── register_page.py
│   └── transfer_funds_page.py
├── reports/                   # Test execution reports
│   └── screenshots/          # Failure screenshots
├── tests/                    # Test suites
│   ├── conftest.py          # Pytest fixtures and config
│   ├── test_01_user_registration.py
│   ├── test_02_fund_transfer.py
│   ├── test_03_bill_payment.py
│   └── test_04_open_account.py
├── utils/                    # Shared utilities
│   ├── driver_factory.py    # WebDriver management
│   ├── logger.py           # Logging configuration 
│   └── credentials_manager.py # Test user management
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Test Demonstrations
**Plz wait for GIF file to load**

### User Registration Test
<iframe width="560" height="315" src="https://youtu.be/ZxYMBCN5dzY" 
frameborder="0" allowfullscreen></iframe>

### Fund Transfer Test  
![Fund Transfer Test](reports/screenshots/transfer_demo.gif)

## Features

1. **User Registration & Login**
   - Automated new user registration
   - Credential persistence for test reuse
   - Session management across tests

2. **Fund Transfers**
   - Inter-account transfers
   - Balance verification
   - Transaction history validation

3. **Bill Payments**
   - Payee management
   - Payment processing
   - Transaction verification

4. **Account Management**
   - New account creation
   - Account overview
   - Transaction search

## Additional Information

- **Browser Support**: Chrome (default), Firefox, Edge
- **Python Version**: 3.14+
- **Key Dependencies**: 
  - Selenium WebDriver
  - Pytest
  - Allure Reporting
  - Faker (test data generation)

## Logging

Logs are stored in `logs/` directory with the following information:
- Test execution steps
- WebDriver initialization
- Page navigation
- Test data generation
- Assertions and verifications

## Reports

The framework generates:
- Allure HTML reports with test execution details
- Screenshots for failed tests
- Execution logs for debugging
- Transaction verification data

## Setup and Execution

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run specific test:
```bash
pytest tests/test_01_user_registration.py -v
```

3. Run all tests:
```bash
pytest -v
```

4. Generate Allure report:
```bash
pytest --alluredir=./reports
allure serve ./reports
```
