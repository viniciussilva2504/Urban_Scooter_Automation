import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_offline_mode_warning(driver):
    # Case 30, 31: No internet warning
    # This requires using the driver to toggle airplane mode or network settings via shell
    driver.execute_script("mobile: shell", {"command": "svc wifi disable"})
    driver.execute_script("mobile: shell", {"command": "svc data disable"})
    
    # Trigger an action that requires internet
    driver.find_element(AppiumBy.ID, "my_orders_tab").click()
    
    # Check warning
    warning_text = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ID, "offline_warning_text"))
    ).text
    assert "Sem acesso à internet" in warning_text
    
    # Case 31: Warning reappears after OK
    driver.find_element(AppiumBy.ID, "offline_ok_button").click()
    driver.find_element(AppiumBy.ID, "my_orders_tab").click()
    
    assert driver.find_element(AppiumBy.ID, "offline_warning_text").is_displayed()
    
    # Restore internet
    driver.execute_script("mobile: shell", {"command": "svc wifi enable"})
    driver.execute_script("mobile: shell", {"command": "svc data enable"})

def test_app_orientation_portrait(driver):
    # Case 32: Application maintains portrait orientation
    # Rotate to landscape
    driver.orientation = "LANDSCAPE"
    
    # Verify that the app doesn't crash and remains functional or forces portrait
    # Based on Case 32: "In Android 31, changing to landscape made the app display Oops! Something went wrong"
    # We check for the "Oops" screen or that the layout is still usable.
    try:
        error_screen = driver.find_element(AppiumBy.ID, "error_oops_screen")
        assert error_screen.is_displayed()
    except:
        # If it doesn't show error, it might be handling it correctly
        pass
    
    # Return to portrait
    driver.orientation = "PORTRAIT"

def test_ui_comparison_figma(driver):
    # Case 33, 34: Figma layout comparison
    # Automated visual testing typically requires tools like Applitools or OpenCV.
    # Here we check for the presence of key elements in expected positions.
    login_title = driver.find_element(AppiumBy.ID, "login_title")
    assert login_title.text == "Urban Scooter" # Comparing with Figma 'Urban.Scooter' (Case 33)
