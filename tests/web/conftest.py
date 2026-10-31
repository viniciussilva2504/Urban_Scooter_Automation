"""Shared browser fixtures. Each test starts from a clean browser session."""
import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from tests.web.pages.urban_scooter_page import LandingPage


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--window-size=1280,900")
    if os.getenv("URBAN_HEADLESS", "").lower() in {"1", "true", "yes"}:
        options.add_argument("--headless=new")
    driver_path = os.getenv("URBAN_CHROMEDRIVER", "").strip()
    service = Service(driver_path) if driver_path else Service()
    browser = webdriver.Chrome(service=service, options=options)
    browser.set_page_load_timeout(30)
    browser.implicitly_wait(0)  # explicit waits only
    yield browser
    browser.quit()


@pytest.fixture
def landing_page(driver):
    configured_url = os.getenv("URBAN_WEB_URL", "").strip()
    if not configured_url:
        pytest.skip("Configure URBAN_WEB_URL with the Urban Scooter test application URL")
    parts = urlsplit(configured_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["lng"] = "pt"
    url = urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urlencode(query), parts.fragment))
    driver.get(url)
    return LandingPage(driver)


@pytest.fixture
def order_details(landing_page):
    return landing_page.open_order()
