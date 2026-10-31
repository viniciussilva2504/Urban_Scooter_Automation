"""USBR1–USBR5: landing-page behavior and layout sequence."""
from selenium.webdriver.common.by import By

from tests.web.pages.urban_scooter_page import LandingPage


def test_main_scooter_model_is_present(landing_page):
    blueprint = landing_page.visible(LandingPage.BLUEPRINT_IMAGE)
    scooter = landing_page.visible(LandingPage.SCOOTER_IMAGE)
    assert blueprint.get_attribute("src").endswith("blueprint.png")
    assert scooter.get_attribute("src").endswith("scooter.png")
    initial_scooter_opacity = float(scooter.find_element(By.XPATH, "..").value_of_css_property("opacity"))
    landing_page.driver.execute_script("window.scrollBy(0, window.innerHeight * 0.65)")
    landing_page.wait.until(lambda d: float(d.find_element(*LandingPage.SCOOTER).value_of_css_property("opacity")) > initial_scooter_opacity)
    assert landing_page.visible(LandingPage.SPECS).is_displayed()


def test_cookie_consent_dismisses_banner(landing_page, driver):
    assert any(element.is_displayed() for element in driver.find_elements(*LandingPage.COOKIE_TEXT))
    landing_page.accept_cookies()
    assert not any(element.is_displayed() for element in driver.find_elements(*LandingPage.COOKIE_TEXT))


def test_order_button_is_visible_and_enabled(landing_page):
    button = landing_page.visible(LandingPage.ORDER_BUTTON)
    assert button.is_displayed() and button.is_enabled()


def test_faq_question_toggles_answer(landing_page):
    question = landing_page.visible((By.XPATH, "//button[contains(.,'Quanto custa isso?')]") )
    answer = question.find_element(By.XPATH, "following-sibling::*[1]")
    landing_page.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", question)
    question.click()
    landing_page.wait.until(lambda _: answer.is_displayed())
    question.click()
    landing_page.wait.until(lambda _: not answer.is_displayed())


def test_landing_page_sections_appear_in_expected_order(landing_page):
    driver = landing_page.driver
    specs = landing_page.visible((By.XPATH, "//*[normalize-space()='Modelo PRO']"))
    roadmap = landing_page.visible((By.XPATH, "//*[normalize-space()='Como funciona']"))
    faq = landing_page.visible(LandingPage.FAQ_HEADING)
    order_buttons = [button for button in driver.find_elements(*LandingPage.ORDER_BUTTON) if button.is_displayed()]
    assert order_buttons
    # The published Portuguese interface has no separate "usage rules" section;
    # check the actual product-specs, roadmap, order, and FAQ sequence.
    order_button = order_buttons[-1]
    positions = [
        driver.execute_script("return arguments[0].getBoundingClientRect().top + window.scrollY", element)
        for element in (specs, roadmap, order_button, faq)
    ]
    assert positions == sorted(positions)
