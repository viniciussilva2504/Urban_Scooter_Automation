# Urban Scooter — QA test automation

Portfolio automation for the Urban Scooter rental app, based on the cases in `Vinicius Silva_QA32_SPT9.xlsx`. The web suite uses Python, pytest, Selenium WebDriver, and the Page Object Model. API and Android tests live in the same repository. Their current status is in [Suite status](#suite-status).

The long setup script, GIF walkthroughs, and Portuguese guide are in [docs/test-guide.md](docs/test-guide.md).

## What it tests

- **Web:** landing page, order-form validation, scooter order creation, and order-status lookup.
- **API:** courier create, login, and delete on `/api/v1/courier`.
- **Android:** courier-app login, order lists, order cards, and system behavior (offline mode, orientation, notifications), written with Appium.

## Scope

Counts below are from the workbook sheets and from `pytest --collect-only -q` in this repository.

| Area | Workbook | pytest collected |
| --- | --- | --- |
| Web | USBR1–USBR48 (48 cases) | 60 tests |
| API | API1–API31 (31 cases) | 29 tests |
| Android | cases 1–43 (43 cases) | 57 tests |

Web collection is higher than the workbook because several form cases are parameterized. API collection is lower because some workbook cases share a test: API26 and API27 are one test, and API28, API29, and API31 are one parametrized test with two values. Android collection is higher than the 43 workbook rows because `test_login.py`, `test_orders.py`, and `test_system.py` repeat flows that the numbered case files also cover, and case 41 is collected in both `test_lists.py` and `test_lifecycle.py`.

### Web modules

| Module | Workbook IDs in the module docstring | pytest tests |
| --- | --- | --- |
| `tests/web/scenarios/test_layout.py` | USBR1–USBR5 | 5 |
| `tests/web/scenarios/test_order_form.py` | USBR6–USBR30 and USBR48 | 38 |
| `tests/web/scenarios/test_order_flow.py` | USBR31–USBR38 | 8 |
| `tests/web/scenarios/test_order_status.py` | USBR39–USBR47 | 9 |

Recorded defects stay marked `XFAIL` while the app keeps that behavior: the FAQ answer that does not close on a second click, plus USBR13, USBR17, USBR21, USBR24, and USBR25. `XPASS` means the application may have changed and the marker should be reviewed.

## Test approach

- pytest collects and runs the cases. Web scenarios are under `tests/web/scenarios/`. Locators and UI actions are in the page objects at `tests/web/pages/urban_scooter_page.py`.
- The Chrome fixture sets `implicitly_wait(0)`. Page objects wait with `WebDriverWait` (10 seconds, polled every 0.2 seconds). Inputs tab out of the field so validation runs without a fixed sleep.
- Valid, invalid, and boundary values use `@pytest.mark.parametrize`.
- Each web test opens its own Chrome window. `URBAN_HEADLESS=true` starts Chrome with `--headless=new`. `URBAN_WEB_URL` overrides the stand URL, and the fixture forces `lng=pt`.
- API requests use the Python standard library (`urllib`). The API session skips when `URBAN_API_BASE_URL` is empty. A URL that cannot be reached fails the test.
- Android uses Appium with UiAutomator2. See [Suite status](#suite-status) before running it.

## Suite status

**Web.** The suite is implemented with page objects and runs in Chrome when a live stand URL is set. The default in `tests/web/data.py` is a TripleTen container. On 4 November 2026 that host returned HTTP 404 with `container with id=cnt-21e647cd-cf6f-4526-b07e-1d34f0ed0f44 is not found`. Set `URBAN_WEB_URL` to the current stand. If the stand is down, the tests fail on the connection.

**API.** `tests/api/test_couriers.py` implements workbook cases API1–API31, with unique data and cleanup in the tests that create a courier. Set `URBAN_API_BASE_URL` before running them. `postman/urban_scooter_env.json` points at the same TripleTen container, which is not found, so these tests cannot run against the URL stored in the repo.

**Android.** pytest collects 57 tests. They still need a device run: `tests/mobile/conftest.py` comments mark the package `com.urban.scooter` and activity `.MainActivity` as assumed, and the fixture expects Appium at `http://localhost:4723`. Resource IDs differ across files (for example `id_login` in `test_auth.py` and `login_field` in `test_login.py`). A run needs Appium, UiAutomator2, and a device or emulator with the real app. This repository does not include device results.

## How to run

Commands use Windows PowerShell from the repository root. Per-test logs, the full loop, and the Portuguese steps are in [docs/test-guide.md](docs/test-guide.md).

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pytest selenium pillow imageio-ffmpeg
$env:URBAN_WEB_URL = "https://<current-stand>/?lng=pt"
$env:URBAN_HEADLESS = "true"
New-Item -ItemType Directory -Force reports | Out-Null
python -m pytest tests/web -v --junitxml=reports/web-suite.xml
```

Install Google Chrome. Selenium Manager resolves ChromeDriver. If it cannot, set `URBAN_CHROMEDRIVER` to a driver that matches the installed Chrome. List every collected web test, including parameter IDs:

```powershell
python -m pytest --collect-only -q tests/web
```

API, after a live base URL is available:

```powershell
$env:URBAN_API_BASE_URL = "https://<current-stand>"
python -m pytest tests/api -v --junitxml=reports/api-suite.xml
```

Android is separate. Check the package, activity, and Appium URL in `tests/mobile/conftest.py` before `python -m pytest tests/mobile`.

## Reports

- JUnit XML from `--junitxml`, such as `reports/web-suite.xml`.
- One GIF and one MP4 per web test under `reports/media/`, built from browser checkpoints. `reports/` is gitignored.
- Four checkpoint GIFs stay in `docs/media/` so they render on GitHub: station autocomplete (`test_station_suggestion_can_be_selected`), rental period (`test_rental_period_has_supported_choices`), scooter color (`test_optional_scooter_color_can_be_selected`), and preserved details (`test_details_are_preserved_when_returning_to_previous_step`).

<p align="center">
  <img src="docs/media/station-autocomplete.gif" alt="Searching for and selecting a suggested station" width="480">
</p>

## Tech stack

Python, pytest, Selenium WebDriver, Google Chrome, Pillow, imageio-ffmpeg, Page Object Model, JUnit XML, Python `urllib`, Postman collection in `postman/`, Appium, and UiAutomator2.

## Project layout

```text
.
├── docs/test-guide.md   # Full setup, per-test commands, Portuguese guide
├── docs/media/          # GIFs shown above
├── postman/             # API collection and environment
├── tests/api/           # Courier API tests
├── tests/mobile/        # Android tests (Appium)
├── tests/web/pages/     # Page objects
├── tests/web/scenarios/ # Web scenarios
├── pytest.ini
└── Vinicius Silva_QA32_SPT9.xlsx
```
