import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_case_1_login_ui(driver):
    # UI check in portrait
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_login")))
    assert driver.find_element(AppiumBy.ID, "id_login").is_displayed()
    assert driver.find_element(AppiumBy.ID, "id_password").is_displayed()
    assert driver.find_element(AppiumBy.ID, "id_login_btn").is_displayed()

def test_case_2_valid_login(driver):
    driver.find_element(AppiumBy.ID, "id_login").send_keys("QANotify")
    driver.find_element(AppiumBy.ID, "id_password").send_keys("1234")
    driver.find_element(AppiumBy.ID, "id_login_btn").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_all_orders_tab")))

def test_case_3_invalid_login(driver):
    driver.find_element(AppiumBy.ID, "id_login").send_keys("QANotExist")
    driver.find_element(AppiumBy.ID, "id_password").send_keys("1234")
    driver.find_element(AppiumBy.ID, "id_login_btn").click()
    error = WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_error_msg")))
    assert "Nome de usuário ou senha inválidos" in error.text

def test_case_4_login_length(driver):
    # Test 1 char (should fail)
    driver.find_element(AppiumBy.ID, "id_login").send_keys("A")
    driver.find_element(AppiumBy.ID, "id_login_btn").click()
    assert driver.find_element(AppiumBy.ID, "id_error_msg").is_displayed()

def test_case_5_password_format(driver):
    driver.find_element(AppiumBy.ID, "id_login").send_keys("QANotify")
    driver.find_element(AppiumBy.ID, "id_password").send_keys("123") # 3 digits
    driver.find_element(AppiumBy.ID, "id_login_btn").click()
    assert driver.find_element(AppiumBy.ID, "id_error_msg").is_displayed()

def test_case_6_password_recovery(driver):
    driver.find_element(AppiumBy.ID, "id_forgot_password").click()
    popup = WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_recovery_text")))
    assert "Contate o gerente: 0101" in popup.text
    driver.find_element(AppiumBy.ID, "id_recovery_ok").click()

def test_case_7_logout(driver):
    # Assume logged in
    driver.find_element(AppiumBy.ID, "id_logout").click()
    driver.find_element(AppiumBy.ID, "id_confirm_logout").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_login")))

def test_case_43_incorrect_password(driver):
    driver.find_element(AppiumBy.ID, "id_login").send_keys("QANotify")
    driver.find_element(AppiumBy.ID, "id_password").send_keys("9999")
    driver.find_element(AppiumBy.ID, "id_login_btn").click()
    assert driver.find_element(AppiumBy.ID, "id_error_msg").is_displayed()
