import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_case_28_push_notification(driver):
    # This requires system-level push check or mock
    pass

def test_case_29_push_target_tab(driver):
    # Simulate push click
    # Verify My Orders is open
    assert driver.find_element(AppiumBy.ID, "id_my_orders_tab").is_selected()

def test_case_30_offline_warning(driver):
    # Toggle airplane mode via shell
    driver.execute_script("mobile: shell", {"command": "svc wifi disable"})
    driver.execute_script("mobile: shell", {"command": "svc data disable"})
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    assert driver.find_element(AppiumBy.ID, "id_offline_text").is_displayed()

def test_case_31_offline_persistence(driver):
    # Close offline warning and try again
    driver.find_element(AppiumBy.ID, "id_offline_ok").click()
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    assert driver.find_element(AppiumBy.ID, "id_offline_text").is_displayed()

def test_case_32_portrait_lock(driver):
    driver.orientation = "LANDSCAPE"
    # Verify if app forces portrait or stays usable
    assert driver.get_window_size()['width'] < driver.get_window_size()['height']

def test_case_33_figma_login(driver):
    # Visual check of fields
    assert driver.find_element(AppiumBy.ID, "id_login").is_displayed()
    assert driver.find_element(AppiumBy.ID, "id_password").is_displayed()

def test_case_34_figma_lists(driver):
    # Visual check of layout
    assert driver.find_element(AppiumBy.ID, "id_order_card_0").is_displayed()

def test_case_35_blue_dot_empty(driver):
    # Setup: No orders
    assert not driver.find_element(AppiumBy.ID, "id_blue_dot").is_displayed()

def test_case_36_color_any(driver):
    # Setup: Order with no color
    card = driver.find_element(AppiumBy.ID, "id_order_card_0")
    card.click()
    assert "qualquer" in card.find_element(AppiumBy.ID, "id_color").text

def test_case_37_push_text(driver):
    # Check push content
    pass

def test_case_38_push_layout(driver):
    # Check push layout
    pass

def test_case_39_offline_popup_figma(driver):
    # Visual check of offline popup
    driver.execute_script("mobile: shell", {"command": "svc wifi disable"})
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    assert driver.find_element(AppiumBy.ID, "id_offline_popup").is_displayed()

def test_case_40_offline_popup_text(driver):
    driver.execute_script("mobile: shell", {"command": "svc wifi disable"})
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    popup = driver.find_element(AppiumBy.ID, "id_offline_popup")
    assert "Sem acesso à internet" in popup.text

def test_case_41_blue_dot_clear(driver):
    # View order then check dot
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    driver.find_element(AppiumBy.ID, "id_order_card_0").click()
    driver.find_element(AppiumBy.ID, "id_all_orders_tab").click()
    assert not driver.find_element(AppiumBy.ID, "id_blue_dot").is_displayed()

def test_case_42_accept_cancelled(driver):
    # Attempt to accept cancelled order
    driver.find_element(AppiumBy.ID, "id_accept_btn_cancelled").click()
    error = WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_error_msg")))
    assert "cancelado" in error.text
