import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_case_16_summary_card(driver):
    card = driver.find_element(AppiumBy.ID, "id_order_card_0")
    assert card.find_element(AppiumBy.ID, "id_address").is_displayed()
    assert card.find_element(AppiumBy.ID, "id_date").is_displayed()

def test_case_17_expanded_card(driver):
    card = driver.find_element(AppiumBy.ID, "id_order_card_0")
    card.click()
    assert card.find_element(AppiumBy.ID, "id_customer_name").is_displayed()
    assert card.find_element(AppiumBy.ID, "id_customer_phone").is_displayed()

def test_case_18_card_displacement(driver):
    card0 = driver.find_element(AppiumBy.ID, "id_order_card_0")
    card1 = driver.find_element(AppiumBy.ID, "id_order_card_1")
    y_before = card1.location['y']
    card0.click()
    y_after = card1.location['y']
    assert y_after > y_before

def test_case_19_accept_summary(driver):
    driver.find_element(AppiumBy.ID, "id_accept_btn_0").click()
    popup = WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_confirm_popup")))
    assert "Você gostaria de aceitar o pedido?" in popup.text

def test_case_20_accept_expanded(driver):
    card = driver.find_element(AppiumBy.ID, "id_order_card_0")
    card.click()
    driver.find_element(AppiumBy.ID, "id_accept_btn_0").click()
    popup = WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_confirm_popup")))
    assert "Você gostaria de aceitar o pedido?" in popup.text

def test_case_21_decline_accept(driver):
    driver.find_element(AppiumBy.ID, "id_accept_btn_0").click()
    driver.find_element(AppiumBy.ID, "id_confirm_no").click()
    assert driver.find_element(AppiumBy.ID, "id_accept_btn_0").is_displayed()

def test_case_22_move_to_my_orders(driver):
    driver.find_element(AppiumBy.ID, "id_accept_btn_0").click()
    driver.find_element(AppiumBy.ID, "id_confirm_yes").click()
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    assert driver.find_element(AppiumBy.ID, "id_order_card_0").is_displayed()

def test_case_23_duplicate_accept(driver):
    # Order already accepted by another
    driver.find_element(AppiumBy.ID, "id_accept_btn_0").click()
    driver.find_element(AppiumBy.ID, "id_confirm_yes").click()
    error = WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_error_msg")))
    assert "já foi aceito por outro entregador" in error.text

def test_case_24_complete_btn_visibility(driver):
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    assert driver.find_element(AppiumBy.ID, "id_complete_btn").is_displayed()

def test_case_25_decline_completion(driver):
    driver.find_element(AppiumBy.ID, "id_complete_btn").click()
    driver.find_element(AppiumBy.ID, "id_confirm_no").click()
    assert driver.find_element(AppiumBy.ID, "id_complete_btn").is_displayed()

def test_case_26_complete_order_move(driver):
    driver.find_element(AppiumBy.ID, "id_complete_btn").click()
    driver.find_element(AppiumBy.ID, "id_confirm_yes").click()
    # Verify moved to end (compare Y coordinates)
    # ... logic to check position in list

def test_case_27_completion_sorting(driver):
    # Create two completed orders and verify order
    pass
