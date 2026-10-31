import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

@pytest.fixture(scope="session")
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Android Emulator"
    options.app_package = "com.urban.scooter" # Assumed package name
    options.app_activity = ".MainActivity"     # Assumed activity name
    options.automation_name = "UiAutomator2"
    
    # The Appium server is assumed to be running on localhost:4723
    driver = webdriver.Remote("http://localhost:4723", options=options)
    yield driver
    driver.quit()
