import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_login_screen_ui(driver):
    # Case 1: Login screen exhibits fields and controls in portrait orientation
    # Note: Device orientation is typically handled by emulator settings or driver.orientation
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "login_field")))
    assert driver.find_element(AppiumBy.ID, "login_field").is_displayed()
    assert driver.find_element(AppiumBy.ID, "password_field").is_displayed()
    assert driver.find_element(AppiumBy.ID, "login_button").is_displayed()
    assert driver.find_element(AppiumBy.ID, "forgot_password_link").is_displayed()

def test_login_valid_credentials(driver):
    # Case 2: Login with valid credentials opens the order list
    driver.find_element(AppiumBy.ID, "login_field").send_keys("QANotify")
    driver.find_element(AppiumBy.ID, "password_field").send_keys("1234")
    driver.find_element(AppiumBy.ID, "login_button").click()
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "all_orders_tab")))
    assert driver.find_element(AppiumBy.ID, "all_orders_tab").is_displayed()

def test_login_invalid_credentials(driver):
    # Case 3: Non-existent login displays invalid credentials message
    driver.find_element(AppiumBy.ID, "login_field").clear()
    driver.find_element(AppiumBy.ID, "login_field").send_keys("QANotExist")
    driver.find_element(AppiumBy.ID, "password_field").clear()
    driver.find_element(AppiumBy.ID, "password_field").send_keys("1234")
    driver.find_element(AppiumBy.ID, "login_button").click()
    
    error_msg = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ID, "error_message"))
    ).text
    assert "Nome de usuário ou senha inválidos" in error_msg

def test_password_recovery_popup(driver):
    # Case 6: Password recovery informs management contact and closes with OK
    driver.find_element(AppiumBy.ID, "forgot_password_link").click()
    
    popup_text = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ID, "recovery_popup_text"))
    ).text
    assert "Contate o gerente: 0101" in popup_text
    
    driver.find_element(AppiumBy.ID, "recovery_ok_button").click()
    assert not driver.find_element(AppiumBy.ID, "recovery_popup_text").is_displayed()

def test_logout_session(driver):
    # Case 7: Exiting the app from main screens ends the session
    # Assuming we are already logged in from test_login_valid_credentials
    driver.find_element(AppiumBy.ID, "logout_button").click()
    driver.find_element(AppiumBy.ID, "confirm_logout_button").click()
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "login_field")))
    assert driver.find_element(AppiumBy.ID, "login_field").is_displayed()
