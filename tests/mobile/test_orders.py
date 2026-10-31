import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_empty_order_list(driver):
    # Case 8: Empty list displays "No orders" and allows swipe-to-refresh
    # Setup: Ensure user is logged in and has no orders
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "no_orders_text")))
    assert driver.find_element(AppiumBy.ID, "no_orders_text").is_displayed()
    
    # Swipe down to refresh
    driver.swipe(500, 1000, 500, 200, 1000)
    # Verify it remains empty but reloads
    assert driver.find_element(AppiumBy.ID, "no_orders_text").is_displayed()

def test_order_tabs_filtering(driver):
    # Case 9: All orders and My orders tabs display correctly
    all_tab = driver.find_element(AppiumBy.ID, "all_orders_tab")
    my_tab = driver.find_element(AppiumBy.ID, "my_orders_tab")
    
    all_tab.click()
    assert all_tab.is_selected()
    
    my_tab.click()
    assert my_tab.is_selected()

def test_order_card_expansion(driver):
    # Case 16, 17: Summary vs expanded cards
    card = driver.find_element(AppiumBy.ID, "order_card_0")
    
    # Summary check
    assert card.find_element(AppiumBy.ID, "address").is_displayed()
    assert card.find_element(AppiumBy.ID, "delivery_date").is_displayed()
    
    # Expand card
    card.click()
    
    # Detailed check
    assert card.find_element(AppiumBy.ID, "customer_name").is_displayed()
    assert card.find_element(AppiumBy.ID, "customer_phone").is_displayed()
    assert card.find_element(AppiumBy.ID, "customer_comment").is_displayed()

def test_accept_order_confirmation(driver):
    # Case 19, 20, 21: Accept order confirmation
    card = driver.find_element(AppiumBy.ID, "order_card_0")
    accept_btn = card.find_element(AppiumBy.ID, "accept_button")
    accept_btn.click()
    
    # Confirm dialog
    dialog_text = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ID, "confirm_accept_text"))
    ).text
    assert "Você gostaria de aceitar o pedido?" in dialog_text
    
    # Test "No" (Case 21)
    driver.find_element(AppiumBy.ID, "confirm_no_button").click()
    assert accept_btn.is_displayed()
    
    # Test "Yes" (Case 22)
    accept_btn.click()
    driver.find_element(AppiumBy.ID, "confirm_yes_button").click()
    
    # Verify it moves to "My Orders"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((AppiumBy.ID, "my_orders_tab")))
    driver.find_element(AppiumBy.ID, "my_orders_tab").click()
    assert driver.find_element(AppiumBy.ID, "order_card_0").is_displayed()

def test_complete_order(driver):
    # Case 24, 25, 26: Complete order flow
    driver.find_element(AppiumBy.ID, "my_orders_tab").click()
    complete_btn = driver.find_element(AppiumBy.ID, "complete_button")
    complete_btn.click()
    
    # Confirm completion
    driver.find_element(AppiumBy.ID, "confirm_yes_button").click()
    
    # Verify completion (Case 26: moves to end and removes delay highlight)
    # This check depends on the specific UI implementation of "end of list"
    assert not complete_btn.is_displayed()
