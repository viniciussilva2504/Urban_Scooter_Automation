"""API1–API31 from the workbook, with unique data and cleanup per test."""
import pytest


def create_body(login, **overrides):
    body = {"login": login, "password": "1234", "firstName": "Ana"}
    body.update(overrides)
    return body


def assert_rejected(response, allowed=(400,)):
    status, payload = response
    assert status in allowed, f"Expected HTTP {allowed}, received {status}: {payload}"


def test_api1_create_courier_and_login(api, unique_login):
    status, payload = api("POST", "/api/v1/courier", create_body(unique_login))
    assert status == 201, payload
    assert payload == {"ok": True}
    status, payload = api("POST", "/api/v1/courier/login", {"login": unique_login, "password": "1234"})
    assert status == 200, payload
    courier_id = payload["id"]
    try:
        assert isinstance(courier_id, int)
    finally:
        api("DELETE", f"/api/v1/courier/{courier_id}")


@pytest.mark.parametrize("login", ["ab", "abcdefghij"])
def test_api2_api3_login_length_boundaries(api, unique_login, login):
    candidate = unique_login[:len(login)]
    status, payload = api("POST", "/api/v1/courier", create_body(candidate))
    assert status == 201, payload
    status, logged = api("POST", "/api/v1/courier/login", {"login": candidate, "password": "1234"})
    assert status == 200, logged
    api("DELETE", f"/api/v1/courier/{logged['id']}")


@pytest.mark.parametrize("login", ["a", "abcdefghijk", "login123", "qa@test", "тест", "two words", ""])
def test_api4_to_api10_invalid_login(api, unique_login, login):
    assert_rejected(api("POST", "/api/v1/courier", create_body(login or unique_login, login=login)))


def test_api11_missing_login(api):
    assert_rejected(api("POST", "/api/v1/courier", {"password": "1234", "firstName": "Ana"}))


def test_api12_duplicate_login(api, unique_login):
    status, payload = api("POST", "/api/v1/courier", create_body(unique_login))
    assert status == 201, payload
    status, result = api("POST", "/api/v1/courier", create_body(unique_login))
    assert_rejected((status, result), allowed=(409,))
    _, logged = api("POST", "/api/v1/courier/login", {"login": unique_login, "password": "1234"})
    api("DELETE", f"/api/v1/courier/{logged['id']}")


@pytest.mark.parametrize("password", ["123", "12345", "abcd", ""])
def test_api13_to_api16_invalid_password(api, unique_login, password):
    assert_rejected(api("POST", "/api/v1/courier", create_body(unique_login, password=password)))


def test_api17_missing_password(api, unique_login):
    assert_rejected(api("POST", "/api/v1/courier", {"login": unique_login, "firstName": "Ana"}))


@pytest.mark.parametrize("first_name", ["Al", "Valentinaa"])
def test_api18_api19_first_name_length_boundaries(api, unique_login, first_name):
    status, payload = api("POST", "/api/v1/courier", create_body(unique_login, firstName=first_name))
    assert status == 201, payload
    _, logged = api("POST", "/api/v1/courier/login", {"login": unique_login, "password": "1234"})
    api("DELETE", f"/api/v1/courier/{logged['id']}")


@pytest.mark.parametrize("first_name", ["A", "Valentinaaa", "Ana12", "An@!", ""])
def test_api20_to_api24_invalid_first_name(api, unique_login, first_name):
    assert_rejected(api("POST", "/api/v1/courier", create_body(unique_login, firstName=first_name)))


def test_api25_missing_first_name(api, unique_login):
    assert_rejected(api("POST", "/api/v1/courier", {"login": unique_login, "password": "1234"}))


def test_api26_api27_delete_and_login_after_delete(api, unique_login):
    status, payload = api("POST", "/api/v1/courier", create_body(unique_login))
    assert status == 201, payload
    _, logged = api("POST", "/api/v1/courier/login", {"login": unique_login, "password": "1234"})
    courier_id = logged["id"]
    status, result = api("DELETE", f"/api/v1/courier/{courier_id}")
    assert status == 200 and result == {"ok": True}
    assert_rejected(api("POST", "/api/v1/courier/login", {"login": unique_login, "password": "1234"}), allowed=(404,))


@pytest.mark.parametrize("courier_id", ["999999999", "abc"])
def test_api28_api29_api31_delete_nonexistent_or_invalid_id(api, courier_id):
    assert_rejected(api("DELETE", f"/api/v1/courier/{courier_id}"), allowed=(400, 404))


def test_api30_delete_without_id_is_not_server_error(api):
    status, _ = api("DELETE", "/api/v1/courier/")
    assert status < 500
