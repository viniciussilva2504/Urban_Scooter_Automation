"""USBR1?USBR5: landing-page behavior and layout sequence."""
from selenium.webdriver.common.by import By

from tests.web.pages.urban_scooter_page import LandingPage


def test_main_scooter_model_is_present(landing_page):
    blueprint = landing_page.visible(LandingPage.BLUEPRINT_IMAGE)
    assert blueprint.get_attribute("src").endswith("blueprint.png")

    landing_page.driver.execute_script("window.scrollBy(0, window.innerHeight * 0.65)")
    landing_page.capture()
    scooter = landing_page.visible(LandingPage.SCOOTER_IMAGE)
    landing_page.wait.until(
        lambda d: float(d.find_element(*LandingPage.SCOOTER).value_of_css_property("opacity")) > 0.5
    )
    assert scooter.get_attribute("src").endswith("scooter.png")
    assert landing_page.visible(LandingPage.SPECS).is_displayed()


def test_cookie_consent_dismisses_banner(landing_page, driver):
    landing_page.visible(LandingPage.COOKIE_TEXT)
    landing_page.accept_cookies()
    assert not any(element.is_displayed() for element in driver.find_elements(*LandingPage.COOKIE_TEXT))


def test_order_button_is_visible_and_enabled(landing_page):
    button = landing_page.visible(LandingPage.ORDER_BUTTON)
    assert button.is_displayed() and button.is_enabled()


def test_faq_question_toggles_answer(landing_page):
    question = landing_page.visible((By.XPATH, "//*[@role='button' and contains(.,'Quanto custa isso?')]"))
    answer = landing_page.driver.find_element(By.ID, question.get_attribute("aria-controls"))
    landing_page.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", question)
    question.click()
    landing_page.capture()
    landing_page.wait.until(lambda _: answer.is_displayed())
    question.click()
    landing_page.capture()
    landing_page.wait.until(lambda _: question.get_attribute("aria-expanded") == "false")


def test_landing_page_sections_appear_in_expected_order(landing_page):
    driver = landing_page.driver
    hero = landing_page.visible(LandingPage.SPECS)
    roadmap = landing_page.visible((By.XPATH, "//*[normalize-space()='Como funciona']"))
    faq = landing_page.visible(LandingPage.FAQ_HEADING)
    order_buttons = [button for button in driver.find_elements(*LandingPage.ORDER_BUTTON) if button.is_displayed()]
    assert order_buttons
    order_button = order_buttons[-1]
    positions = [
        driver.execute_script("return arguments[0].getBoundingClientRect().top + window.scrollY", element)
        for element in (hero, roadmap, order_button, faq)
    ]
    assert positions == sorted(positions)
