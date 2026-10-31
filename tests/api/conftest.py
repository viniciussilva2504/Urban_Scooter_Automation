"""Fixtures for the spreadsheet's courier API cases.

Set URBAN_API_BASE_URL to the test server URL before running this suite.
"""
import json
import os
import secrets
import string
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest


@pytest.fixture(scope="session")
def api_base_url():
    value = os.getenv("URBAN_API_BASE_URL", "").strip().rstrip("/")
    if not value:
        pytest.skip("Configure URBAN_API_BASE_URL with the Urban Scooter test server URL")
    return value


@pytest.fixture
def api(api_base_url):
    def request(method, path, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = Request(
            api_base_url + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            response = urlopen(req, timeout=20)
        except HTTPError as error:
            response = error
        except URLError as error:
            pytest.fail(f"API server unavailable at {api_base_url}: {error}")
        raw = response.read().decode("utf-8")
        try:
            payload = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            payload = raw
        return response.status, payload

    return request


@pytest.fixture
def unique_login():
    return "".join(secrets.choice(string.ascii_lowercase) for _ in range(10))
