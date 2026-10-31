import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_case_8_empty_list(driver):
    # Setup: Logged in, no orders
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "id_no_orders")))
    assert driver.find_element(AppiumBy.ID, "id_no_orders").is_displayed()
    driver.swipe(500, 1000, 500, 200, 1000)
    assert driver.find_element(AppiumBy.ID, "id_no_orders").is_displayed()

def test_case_9_tabs_filter(driver):
    all_tab = driver.find_element(AppiumBy.ID, "id_all_orders_tab")
    my_tab = driver.find_element(AppiumBy.ID, "id_my_orders_tab")
    all_tab.click()
    assert all_tab.is_selected()
    my_tab.click()
    assert my_tab.is_selected()

def test_case_10_update_list(driver):
    # Swipe down to update
    driver.swipe(500, 1000, 500, 200, 1000)
    # Check if list updated (logic depends on backend)
    assert driver.find_element(AppiumBy.ID, "id_order_list").is_displayed()

def test_case_11_sync_cache(driver):
    # Change tab and return
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    driver.find_element(AppiumBy.ID, "id_all_orders_tab").click()
    assert driver.find_element(AppiumBy.ID, "id_all_orders_tab").is_selected()

def test_case_12_auto_update(driver):
    # Accept order, check others don't update
    driver.find_element(AppiumBy.ID, "id_accept_btn_0").click()
    assert driver.find_element(AppiumBy.ID, "id_order_card_1").is_displayed()

def test_case_13_sorting_delay(driver):
    # Verify delayed orders are on top and red
    first_card = driver.find_element(AppiumBy.ID, "id_order_card_0")
    assert "red" in first_card.get_attribute("color") or first_card.find_element(AppiumBy.ID, "id_delay_highlight").is_displayed()

def test_case_14_station_filter_dup(driver):
    driver.find_element(AppiumBy.ID, "id_filter_btn").click()
    stations = driver.find_elements(AppiumBy.ID, "id_station_option")
    station_names = [s.text for s in stations]
    assert len(station_names) == len(set(station_names))

def test_case_15_filter_scroll(driver):
    driver.find_element(AppiumBy.ID, "id_filter_btn").click()
    # Verify scrolling if > 8 stations
    stations = driver.find_elements(AppiumBy.ID, "id_station_option")
    if len(stations) > 8:
        driver.swipe(500, 800, 500, 400, 1000)
        assert driver.find_element(AppiumBy.ID, "id_station_option_last").is_displayed()

def test_case_41_blue_dot_disappear(driver):
    driver.find_element(AppiumBy.ID, "id_my_orders_tab").click()
    # View order
    driver.find_element(AppiumBy.ID, "id_order_card_0").click()
    driver.find_element(AppiumBy.ID, "id_all_orders_tab").click()
    assert not driver.find_element(AppiumBy.ID, "id_blue_dot").is_displayed()
