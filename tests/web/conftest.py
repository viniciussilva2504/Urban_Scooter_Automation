"""Shared browser fixtures. Each test starts from a clean browser session."""
import os
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from tests.web.data import TEST_WEB_URL
from tests.web.evidence import BrowserEvidence
from tests.web.pages.urban_scooter_page import LandingPage


@pytest.fixture
def driver(request):
    options = Options()
    options.add_argument("--window-size=1280,900")
    if os.getenv("URBAN_HEADLESS", "").lower() in {"1", "true", "yes"}:
        options.add_argument("--headless=new")
    driver_path = os.getenv("URBAN_CHROMEDRIVER", "").strip()
    if not driver_path:
        cache_dir = Path.home() / ".cache" / "selenium" / "chromedriver" / "win64"
        cached = list(cache_dir.glob("*/chromedriver.exe"))
        cached.sort(
            key=lambda path: tuple(int(part) for part in re.findall(r"\d+", path.parent.name)),
            reverse=True,
        )
        if cached:
            driver_path = str(cached[0])
    service = Service(driver_path) if driver_path else Service()
    browser = webdriver.Chrome(service=service, options=options)
    browser.set_page_load_timeout(30)
    browser.implicitly_wait(0)  # explicit waits only
    recorder = BrowserEvidence(request.node.nodeid, Path("reports/media"))
    browser._urban_evidence = recorder
    try:
        yield browser
    finally:
        try:
            recorder.capture(browser)
            media_paths = recorder.save()
            if media_paths:
                request.node.user_properties.extend(
                    [("gif", str(media_paths[0])), ("mp4", str(media_paths[1]))]
                )
        finally:
            browser.quit()


@pytest.fixture
def landing_page(driver):
    configured_url = os.getenv(
        "URBAN_WEB_URL",
        TEST_WEB_URL,
    ).strip()
    parts = urlsplit(configured_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["lng"] = "pt"
    url = urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urlencode(query), parts.fragment))
    driver.get(url)
    driver._urban_evidence.capture(driver)
    return LandingPage(driver)


@pytest.fixture
def order_details(landing_page):
    return landing_page.open_order()
