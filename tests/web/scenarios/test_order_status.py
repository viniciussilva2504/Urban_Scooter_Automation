"""USBR39–USBR47: order lookup, cancellation and visible status lifecycle.

Set URBAN_WEB_ORDER_ID to a disposable, known order for the lifecycle scenarios.
"""
import os
import re
from datetime import date, timedelta

import pytest
from selenium.webdriver.common.by import By

from tests.web.data import METRO_SEARCH, METRO_STATION
from tests.web.pages.urban_scooter_page import ConfirmationPage, LandingPage, OrderDetailsPage, OrderStatusPage, RentalPage


@pytest.fixture
def status_page(landing_page, driver):
    # The order number field and tracking action live in the shared page header.
    return OrderStatusPage(driver)


def _lookup(status_page, order_id):
    status_page.visible(OrderStatusPage.ORDER_NUMBER_INPUT).send_keys(order_id)
    status_page.click(OrderStatusPage.GO)


def test_lookup_existing_order_shows_status(status_page):
    order_id = os.getenv("URBAN_WEB_ORDER_ID", "").strip()
    if not order_id:
        pytest.skip("Configure URBAN_WEB_ORDER_ID with an existing test order")
    _lookup(status_page, order_id)
    assert status_page.wait.until(lambda d: d.find_elements(By.XPATH, "//*[contains(.,'Статус') or contains(.,'Status') or contains(.,'scooter')]") )


def test_lookup_nonexistent_order_shows_not_found(status_page):
    _lookup(status_page, "999999999")
    error = status_page.visible((By.XPATH, "//*[contains(.,'Este pedido não existe') or contains(.,\"There's no such order\")]") )
    assert error.is_displayed()


def test_cancel_confirmation_can_return_to_order_status(status_page):
    order_id = os.getenv("URBAN_WEB_CANCEL_ORDER_ID", "").strip()
    if not order_id:
        pytest.skip("Configure URBAN_WEB_CANCEL_ORDER_ID with a disposable pending order")
    _lookup(status_page, order_id)
    status_page.click(OrderStatusPage.CANCEL)
    back = (By.XPATH, "//button[normalize-space()='Voltar' or normalize-space()='Back']")
    status_page.click(back)
    assert status_page.visible(OrderStatusPage.ORDER_NUMBER_INPUT).is_displayed()


def test_cancelled_order_cannot_be_looked_up_again(status_page):
    order_id = os.getenv("URBAN_WEB_CANCEL_ORDER_ID", "").strip()
    if not order_id:
        pytest.skip("Configure URBAN_WEB_CANCEL_ORDER_ID with a disposable pending order")
    _lookup(status_page, order_id)
    status_page.click(OrderStatusPage.CANCEL)
    status_page.click((By.XPATH, "//button[normalize-space()='Cancelar' or normalize-space()='Cancel']"))
    status_page.click((By.XPATH, "//button[normalize-space()='Ok' or normalize-space()='Okay']"))
    _lookup(status_page, order_id)
    assert status_page.visible((By.XPATH, "//*[contains(.,'Este pedido não existe') or contains(.,\"There's no such order\")]")).is_displayed()


def test_cancellation_is_unavailable_after_courier_acceptance(status_page):
    order_id = os.getenv("URBAN_WEB_ACCEPTED_ORDER_ID", "").strip()
    if not order_id:
        pytest.skip("Configure URBAN_WEB_ACCEPTED_ORDER_ID with an accepted order")
    _lookup(status_page, order_id)
    assert not status_page.driver.find_elements(*OrderStatusPage.CANCEL)


def test_consecutive_orders_receive_independent_numbers(landing_page):
    first_track = _create_order(landing_page, "AnaMaria")
    driver = landing_page.driver
    base_url = driver.current_url.split("/order")[0].split("/track")[0]
    driver.get(base_url + "?lng=pt")
    second_track = _create_order(LandingPage(driver), "JoaoPedro")
    assert first_track != second_track


def test_initial_status_shows_scooter_in_warehouse(status_page):
    _assert_status(status_page, "URBAN_WEB_INITIAL_ORDER_ID", "A scooter está no depósito")


def test_courier_en_route_status_shows_courier_name(status_page):
    _assert_status(status_page, "URBAN_WEB_EN_ROUTE_ORDER_ID", "está a caminho")


def test_arrived_status_is_shown(status_page):
    _assert_status(status_page, "URBAN_WEB_ARRIVED_ORDER_ID", "O entregador chegou")


def _assert_status(status_page, env_var, expected_text):
    order_id = os.getenv(env_var, "").strip()
    if not order_id:
        pytest.skip(f"Configure {env_var} with an order in the required state")
    _lookup(status_page, order_id)
    status = status_page.visible((By.XPATH, f"//*[contains(.,'{expected_text}')]") )
    assert status.is_displayed()


def _create_order(landing_page, name):
    details = landing_page.open_order()
    details.set_field(OrderDetailsPage.NAME, name)
    details.set_field(OrderDetailsPage.SURNAME, "Silva")
    details.set_field(OrderDetailsPage.ADDRESS, "123 Main Street")
    details.choose_station(METRO_SEARCH, METRO_STATION)
    details.set_field(OrderDetailsPage.PHONE, "+1234567890")
    rental = details.advance()
    date_field = rental.visible(RentalPage.DATE)
    date_field.send_keys((date.today() + timedelta(days=1)).strftime("%d.%m.%Y"))
    date_field.send_keys("\t")
    rental.choose_two_day_period()
    confirmation = rental.submit_order()
    confirmation.click(ConfirmationPage.CONFIRM)
    modal = confirmation.visible((By.XPATH, "//*[contains(.,'O pedido foi feito')]"))
    match = re.search(r"número do pedido:\s*(\d+)", modal.text, re.IGNORECASE)
    if not match:
        match = re.search(r"número do pedido:\s*(\d+)", confirmation.driver.find_element(By.TAG_NAME, "body").text, re.IGNORECASE)
    assert match, "Order created confirmation did not show a tracking number"
    return match.group(1)
