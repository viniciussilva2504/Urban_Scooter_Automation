"""USBR6–USBR30 and USBR48: order details form validation and station choice."""
import pytest

from tests.web.data import VALID_ADDRESS, VALID_NAME, VALID_PHONE, VALID_SURNAME
from tests.web.pages.urban_scooter_page import OrderDetailsPage


@pytest.mark.parametrize("value", ["V", "Vinicius Jesusss", "Vinicius 2", "Vin7ciu5", "Ana@Silva"], ids=["short", "over-15", "space-number", "embedded-digits", "symbol"])
def test_name_rejects_invalid_values(order_details, value):
    order_details.set_field(OrderDetailsPage.NAME, value)
    assert "valid" in order_details.error_for(OrderDetailsPage.NAME).lower() or "válido" in order_details.error_for(OrderDetailsPage.NAME).lower()


@pytest.mark.parametrize("value", ["Al", "Vinicius Jesus", "Ana Maria Silva"])
def test_name_accepts_boundary_and_supported_values(order_details, value):
    field = order_details.set_field(OrderDetailsPage.NAME, value)
    assert field.get_attribute("value") == value
    assert not order_details.error_for(OrderDetailsPage.NAME)


@pytest.mark.parametrize("value", ["A", "Jesus da Silvaaaaaa", "Ana@Silva"])
def test_surname_validation(order_details, value):
    order_details.set_field(OrderDetailsPage.SURNAME, value)
    message = order_details.error_for(OrderDetailsPage.SURNAME)
    assert "valid" in message.lower() or "válido" in message.lower()


@pytest.mark.parametrize("value", ["Al", "Ana Maria Silva", "Ana-Silva"])
def test_surname_accepts_supported_values(order_details, value):
    field = order_details.set_field(OrderDetailsPage.SURNAME, value)
    assert field.get_attribute("value") == value
    assert not order_details.error_for(OrderDetailsPage.SURNAME)


@pytest.mark.parametrize("value", ["123 A", "123 Main Street, Los Angeles, CA 90001", " 123 Main Street "])
def test_address_accepts_valid_value_and_trims_whitespace(order_details, value):
    field = order_details.set_field(OrderDetailsPage.ADDRESS, value)
    assert field.get_attribute("value") == value.strip()
    assert not order_details.error_for(OrderDetailsPage.ADDRESS)


@pytest.mark.parametrize("value", ["123 Main St, Apt 4, Los Angeles, CA 90001, Unit 5", "1234", "A" * 51, "123 Main Street@"])
def test_address_validation_cases(order_details, value):
    order_details.set_field(OrderDetailsPage.ADDRESS, value)
    message = order_details.error_for(OrderDetailsPage.ADDRESS)
    if len(value) == 50:
        assert not message
    else:
        assert "valid" in message.lower() or "válido" in message.lower()


@pytest.mark.parametrize("value", ["+123456789", "+1234567890", "+12345678901"])
def test_phone_accepted_range(order_details, value):
    field = order_details.set_field(OrderDetailsPage.PHONE, value)
    assert field.get_attribute("value") == value
    assert not order_details.error_for(OrderDetailsPage.PHONE)


@pytest.mark.parametrize("value", ["1234567890", "+12345678", "+123456789012", "1234567890123", "+123456abc", "+12345-789", "+12345@789"])
def test_phone_rejects_invalid_values(order_details, value):
    order_details.set_field(OrderDetailsPage.PHONE, value)
    message = order_details.error_for(OrderDetailsPage.PHONE)
    assert "valid" in message.lower() or "válido" in message.lower()


def test_station_suggestion_can_be_selected(order_details):
    selected = order_details.choose_station("Hollywood", "Hollywood/Highland")
    assert selected == "Hollywood/Highland"


@pytest.mark.parametrize("locator", [OrderDetailsPage.NAME, OrderDetailsPage.PHONE])
def test_required_name_and_phone_block_advance(order_details, locator):
    for field, value in [(OrderDetailsPage.NAME, VALID_NAME), (OrderDetailsPage.SURNAME, VALID_SURNAME), (OrderDetailsPage.ADDRESS, VALID_ADDRESS), (OrderDetailsPage.PHONE, VALID_PHONE)]:
        order_details.set_field(field, "" if field == locator else value)
    order_details.click(OrderDetailsPage.NEXT)
    assert order_details.visible(("xpath", "//*[normalize-space()='Para quem é a scooter']")).is_displayed()


@pytest.mark.parametrize("locator", [OrderDetailsPage.SURNAME, OrderDetailsPage.ADDRESS, OrderDetailsPage.METRO])
def test_required_surname_address_and_station_block_advance(order_details, locator):
    for field, value in [(OrderDetailsPage.NAME, VALID_NAME), (OrderDetailsPage.SURNAME, VALID_SURNAME), (OrderDetailsPage.ADDRESS, VALID_ADDRESS), (OrderDetailsPage.PHONE, VALID_PHONE)]:
        order_details.set_field(field, "" if field == locator else value)
    order_details.click(OrderDetailsPage.NEXT)
    assert order_details.visible(("xpath", "//*[normalize-space()='Para quem é a scooter']")).is_displayed()


def test_name_accepts_hyphen(order_details):
    field = order_details.set_field(OrderDetailsPage.NAME, "Ana-Maria")
    assert field.get_attribute("value") == "Ana-Maria"
    assert not order_details.error_for(OrderDetailsPage.NAME)
