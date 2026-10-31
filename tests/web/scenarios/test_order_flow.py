"""USBR31–USBR38: complete order flow and rental-step behavior."""
from datetime import date, timedelta

import pytest
from selenium.webdriver.common.by import By
from tests.web.data import METRO_SEARCH, METRO_STATION, VALID_ADDRESS, VALID_NAME, VALID_PHONE, VALID_SURNAME
from tests.web.pages.urban_scooter_page import ConfirmationPage, OrderDetailsPage, RentalPage


def _valid_rental_page(landing_page):
    details = landing_page.open_order()
    details.set_field(OrderDetailsPage.NAME, VALID_NAME)
    details.set_field(OrderDetailsPage.SURNAME, VALID_SURNAME)
    details.set_field(OrderDetailsPage.ADDRESS, VALID_ADDRESS)
    details.choose_station(METRO_SEARCH, METRO_STATION)
    details.set_field(OrderDetailsPage.PHONE, VALID_PHONE)
    return details.advance()


@pytest.mark.parametrize("case_id", ["USBR31", "USBR35"])
def test_complete_order(landing_page, case_id):
    rental = _valid_rental_page(landing_page)
    date_field = rental.visible(RentalPage.DATE)
    date_field.send_keys((date.today() + timedelta(days=1)).strftime("%d.%m.%Y"))
    date_field.send_keys("\t")
    rental.choose_two_day_period()
    if case_id == "USBR31":
        rental.choose_color("black")
        rental.visible(RentalPage.COMMENT).send_keys("Entregar na portaria")
    confirmation = rental.submit_order()
    confirmation.click(ConfirmationPage.CONFIRM)
    assert confirmation.visible((By.XPATH, "//*[contains(.,'O pedido foi feito')]")).is_displayed(), case_id


def test_delivery_date_cannot_be_before_tomorrow(landing_page):
    rental = _valid_rental_page(landing_page)
    rental.click(RentalPage.DATE)
    today = rental.driver.find_element(By.CSS_SELECTOR, ".react-datepicker__day--today")
    assert "disabled" in today.get_attribute("class")


def test_rental_period_has_supported_choices(landing_page):
    rental = _valid_rental_page(landing_page)
    options = rental.available_rent_options()
    assert len(options) == 7
    rental.select_rent_option("sete dias")
    assert rental.visible(RentalPage.PERIOD).is_displayed()


def test_rental_date_and_period_are_required(landing_page):
    rental = _valid_rental_page(landing_page)
    rental.click(RentalPage.ORDER)
    assert "Locação" in rental.driver.find_element(By.TAG_NAME, "body").text


def test_optional_scooter_color_can_be_selected(landing_page):
    rental = _valid_rental_page(landing_page)
    assert rental.choose_color("black")


def test_optional_courier_comment_accepts_text(landing_page):
    rental = _valid_rental_page(landing_page)
    comment = rental.visible(RentalPage.COMMENT)
    comment.send_keys("Entregar na portaria")
    assert comment.get_attribute("value") == "Entregar na portaria"


def test_details_are_preserved_when_returning_to_previous_step(landing_page):
    rental = _valid_rental_page(landing_page)
    rental.click(RentalPage.BACK)
    field = landing_page.driver.find_element(*OrderDetailsPage.NAME)
    assert field.get_attribute("value") == VALID_NAME
