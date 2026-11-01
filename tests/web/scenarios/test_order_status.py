"""USBR39–USBR47: order lookup, cancellation and delivery state lifecycle."""
import json
import os
import re
import secrets
import string
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.web.data import METRO_SEARCH, METRO_STATION, TEST_WEB_URL
from tests.web.pages.urban_scooter_page import ConfirmationPage, LandingPage, OrderDetailsPage, OrderStatusPage, RentalPage

@pytest.fixture
def status_page(landing_page, driver):
    return OrderStatusPage(driver)


@pytest.fixture
def order_api():
    base_url = os.getenv("URBAN_API_BASE_URL", "").strip()
    if not base_url:
        web_url = os.getenv("URBAN_WEB_URL", TEST_WEB_URL)
        web_parts = urlsplit(web_url)
        base_url = f"{web_parts.scheme}://{web_parts.netloc}"
    base_url = base_url.rstrip("/")

    def request(method, path, body=None):
        payload = None if body is None else json.dumps(body).encode("utf-8")
        request_object = Request(
            base_url + path,
            data=payload,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            response = urlopen(request_object, timeout=20)
        except HTTPError as error:
            response = error
        except URLError as error:
            pytest.fail(f"API test stand unavailable at {base_url}: {error}")
        raw = response.read().decode("utf-8")
        try:
            result = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            result = raw
        if response.status >= 400:
            pytest.fail(f"{method} {path} returned {response.status}: {result}")
        return result

    return request


@pytest.fixture
def pending_order(landing_page, driver):
    return _create_order(landing_page, "AnaMaria")


@pytest.fixture
def accepted_order(landing_page, driver, order_api):
    track = _create_order(landing_page, "JoaoPedro")
    order_data = order_api("GET", f"/api/v1/orders/track?{urlencode({'t': track})}")["order"]
    login = "qa" + "".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    courier_name = "QABot"
    order_api("POST", "/api/v1/courier", {"login": login, "password": "1234", "firstName": courier_name})
    courier = order_api("POST", "/api/v1/courier/login", {"login": login, "password": "1234"})
    courier_id = courier["id"]
    try:
        order_api("PUT", f"/api/v1/orders/accept/{order_data['id']}?courierId={courier_id}")
        yield track, courier_name, order_data["id"], courier_id
    finally:
        order_api("DELETE", f"/api/v1/courier/{courier_id}")


@pytest.fixture
def arrived_order(accepted_order, order_api):
    track, _, order_id, _ = accepted_order
    order_api("PUT", f"/api/v1/orders/finish/{order_id}")
    return track


def _lookup(status_page, order_id):
    status_page.click(LandingPage.STATUS_BUTTON)
    status_page.visible(OrderStatusPage.ORDER_NUMBER_INPUT).send_keys(order_id)
    status_page.click(OrderStatusPage.GO)


def test_lookup_existing_order_shows_status(status_page, pending_order):
    order_id = pending_order
    _lookup(status_page, order_id)
    assert status_page.wait.until(lambda d: d.find_elements(By.XPATH, "//*[contains(.,'Статус') or contains(.,'Status') or contains(.,'scooter')]") )


def test_lookup_nonexistent_order_shows_not_found(status_page):
    _lookup(status_page, "999999999")
    error = status_page.visible((By.XPATH, "//*[contains(.,'Este pedido não existe') or contains(.,\"There's no such order\")]") )
    assert error.is_displayed()


def test_cancel_confirmation_can_return_to_order_status(status_page, pending_order):
    order_id = pending_order
    _lookup(status_page, order_id)
    status_page.click(OrderStatusPage.CANCEL)
    back = (By.XPATH, "//button[normalize-space()='Voltar' or normalize-space()='Back']")
    status_page.click(back)
    assert status_page.visible(OrderStatusPage.ORDER_NUMBER_INPUT).is_displayed()


def test_cancelled_order_cannot_be_looked_up_again(status_page, pending_order):
    order_id = pending_order
    _lookup(status_page, order_id)
    status_page.click(OrderStatusPage.CANCEL)
    status_page.click((By.XPATH, "//button[normalize-space()='Cancelar' or normalize-space()='Cancel']"))
    status_page.click((By.XPATH, "//button[normalize-space()='Ok' or normalize-space()='Okay']"))
    _lookup(status_page, order_id)
    assert status_page.visible((By.XPATH, "//*[contains(.,'Este pedido não existe') or contains(.,\"There's no such order\")]")).is_displayed()


def test_cancellation_is_unavailable_after_courier_acceptance(status_page, accepted_order):
    order_id = accepted_order[0]
    _lookup(status_page, order_id)
    assert not status_page.driver.find_elements(*OrderStatusPage.CANCEL)


def test_consecutive_orders_receive_independent_numbers(landing_page):
    first_track = _create_order(landing_page, "AnaMaria")
    second_track = _create_order(landing_page, "JoaoPedro")
    assert first_track != second_track


def test_initial_status_shows_scooter_in_warehouse(status_page, pending_order):
    _lookup(status_page, pending_order)
    status = status_page.visible((By.XPATH, "//*[contains(.,'A scooter está no depósito')]"))
    assert status.is_displayed()


def test_courier_en_route_status_shows_courier_name(status_page, accepted_order):
    track, courier_name, _, _ = accepted_order
    _lookup(status_page, track)
    status = status_page.visible((By.XPATH, f"//*[contains(.,'O entregador {courier_name} está a caminho')]"))
    assert status.is_displayed()


def test_arrived_status_is_shown(status_page, arrived_order):
    _lookup(status_page, arrived_order)
    status = status_page.visible((By.XPATH, "//*[contains(.,'O entregador chegou')]"))
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
    date_field.send_keys(Keys.ESCAPE)
    rental.capture()
    rental.choose_two_day_period()
    confirmation = rental.submit_order()
    confirmation.click(ConfirmationPage.CONFIRM)
    modal = confirmation.visible((By.XPATH, "//*[contains(.,'O pedido foi feito')]"))
    match = re.search(r"número do pedido:\s*(\d+)", modal.text, re.IGNORECASE)
    if not match:
        match = re.search(r"número do pedido:\s*(\d+)", confirmation.driver.find_element(By.TAG_NAME, "body").text, re.IGNORECASE)
    assert match, "Order created confirmation did not show a tracking number"
    track = match.group(1)
    url_parts = urlsplit(os.getenv("URBAN_WEB_URL", TEST_WEB_URL))
    home_url = urlunsplit((url_parts.scheme, url_parts.netloc, url_parts.path, "lng=pt", ""))
    landing_page.driver.get(home_url)
    return track
