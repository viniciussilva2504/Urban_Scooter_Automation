"""Page objects for the Urban Scooter web ordering flow.

Locators use the accessible labels and visible copy from the test cases. If the
application's copy changes, update locators here rather than in test scenarios.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout, poll_frequency=0.2)

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator):
        self.clickable(locator).click()
        self.capture()

    def fill(self, locator, value):
        element = self.visible(locator)
        element.clear()
        element.send_keys(value)
        element.send_keys("\t")  # trigger blur validation without fixed sleeps
        self.capture()
        return element

    def capture(self):
        recorder = getattr(self.driver, "_urban_evidence", None)
        if recorder:
            recorder.capture(self.driver)

    def error_for(self, locator):
        field = self.visible(locator)
        # Validation text is associated with the input in the application's form.
        described_by = field.get_attribute("aria-describedby")
        if described_by:
            for element_id in described_by.split():
                matches = self.driver.find_elements(By.ID, element_id)
                if matches and matches[0].is_displayed():
                    return matches[0].text
        parent = field.find_element(By.XPATH, "..")
        errors = parent.find_elements(
            By.XPATH,
            ".//*[@role='alert' or @aria-live or contains(@class,'error') or contains(@class,'Error')]",
        )
        return " ".join(e.text for e in errors if e.is_displayed() and e.text.strip())


class LandingPage(BasePage):
    ORDER_BUTTON = (By.XPATH, "//button[contains(.,'Fazer pedido') or contains(.,'Make order')]")
    COOKIE_BUTTON = (By.XPATH, "//button[contains(.,'Concordar') or contains(.,'Agree') or contains(.,'Accept')]")
    COOKIE_TEXT = (By.XPATH, "//*[contains(translate(., 'COOKIES', 'cookies'),'cookies')]")
    FAQ_HEADING = (By.XPATH, "//*[normalize-space()='Perguntas frequentes' or normalize-space()='Frequently asked questions']")
    BLUEPRINT_IMAGE = (By.CSS_SELECTOR, "[class*='BluePrint'] img")
    SCOOTER_IMAGE = (By.CSS_SELECTOR, "[class*='Scooter'] img")
    SCOOTER = (By.CSS_SELECTOR, "[class*='Scooter']")
    SPECS = (By.XPATH, "//*[normalize-space()='Modelo PRO']")

    def open_order(self):
        self.click(self.ORDER_BUTTON)
        return OrderDetailsPage(self.driver)

    def accept_cookies(self):
        buttons = self.driver.find_elements(*self.COOKIE_BUTTON)
        if buttons and buttons[0].is_displayed():
            buttons[0].click()
            self.capture()


class OrderDetailsPage(BasePage):
    # Name/phone are required to create an order. Selectors are centralized here.
    NAME = (By.XPATH, "//input[contains(@placeholder,'Nome') or contains(@placeholder,'First name')]")
    SURNAME = (By.XPATH, "//input[contains(@placeholder,'Sobrenome') or contains(@placeholder,'Last name')]")
    ADDRESS = (By.XPATH, "//input[contains(@placeholder,'Endereço:') or contains(@placeholder,'Address')]")
    METRO = (By.XPATH, "//div[normalize-space()='* Estação de metrô' or contains(@class,'Metro')]")
    PHONE = (By.XPATH, "//input[contains(@placeholder,'Telefone') or contains(@placeholder,'Phone')]")
    NEXT = (By.XPATH, "//button[contains(.,'Avançar') or contains(.,'Next')]")
    ERROR = (By.XPATH, "//*[contains(.,'válido') or contains(.,'valid') or contains(.,'número válido')]")

    def set_field(self, locator, value):
        return self.fill(locator, value)

    def advance(self):
        self.click(self.NEXT)
        return RentalPage(self.driver)

    def choose_station(self, query, option):
        station_control = self.visible(self.METRO)
        station_control.click()
        self.capture()
        search_fields = self.driver.find_elements(By.XPATH, "//input[@type='text']")
        if search_fields:
            search_fields[-1].send_keys(query)
        suggestion = (By.XPATH, f"//*[self::li or self::button or @role='option'][contains(normalize-space(),{self._xpath_literal(option)})]")
        self.click(suggestion)
        return option

    @staticmethod
    def _xpath_literal(value):
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        return "concat(" + ", \"'\", ".join(f"'{part}'" for part in value.split("'")) + ")"


class RentalPage(BasePage):
    DATE = (By.XPATH, "//input[contains(@placeholder,'Quando entregar') or contains(@placeholder,'Delivery date') or @type='date']")
    PERIOD = (By.XPATH, "//*[self::div or self::input][normalize-space()='* Período de locação' or normalize-space()='* Rental period']")
    RENT_OPTIONS = (By.XPATH, "//*[self::div or self::button or @role='option'][normalize-space()='um dia' or normalize-space()='dois dias' or normalize-space()='três dias' or normalize-space()='quatro dias' or normalize-space()='cinco dias' or normalize-space()='seis dias' or normalize-space()='sete dias']")
    COLOR_CHECKBOXES = (By.XPATH, "//input[@type='checkbox']")
    COMMENT = (By.XPATH, "//*[self::input or self::textarea][contains(@placeholder,'Comentário') or contains(@placeholder,'comment')]")
    ORDER = (By.XPATH, "//button[contains(.,'Заказать') or contains(.,'Fazer pedido') or contains(.,'Order')]")
    BACK = (By.XPATH, "//button[normalize-space()='Voltar' or normalize-space()='Back']")

    def submit_order(self):
        self.click(self.ORDER)
        return ConfirmationPage(self.driver)

    def choose_two_day_period(self):
        self.click(self.PERIOD)
        self.click((By.XPATH, "//*[self::div or self::button or @role='option'][normalize-space()='dois dias' or normalize-space()='two days']"))

    def available_rent_options(self):
        self.click(self.PERIOD)
        return [option.text.strip() for option in self.driver.find_elements(*self.RENT_OPTIONS) if option.is_displayed()]

    def select_rent_option(self, visible_text):
        self.click(self.PERIOD)
        option = (By.XPATH, f"//*[self::div or self::button or @role='option'][normalize-space()={OrderDetailsPage._xpath_literal(visible_text)}]")
        self.click(option)

    def choose_color(self, color_id):
        checkbox = self.visible((By.ID, color_id))
        if not checkbox.is_selected():
            self.driver.find_element(By.XPATH, f"//label[@for='{color_id}']").click()
            self.capture()
        return checkbox.is_selected()


class ConfirmationPage(BasePage):
    CONFIRM = (By.XPATH, "//button[normalize-space()='Sim' or normalize-space()='Yes' or normalize-space()='Confirm']")
    ORDER_NUMBER = (By.XPATH, "//*[contains(.,'número do pedido') or contains(.,'order number')]")
    ORDER_SUCCESS = (By.XPATH, "//*[contains(.,'pedido foi criado') or contains(.,'order has been created')]")


class OrderStatusPage(BasePage):
    ORDER_NUMBER_INPUT = (By.XPATH, "//input[contains(@placeholder,'número do pedido') or contains(@placeholder,'order number')]")
    GO = (By.XPATH, "//button[normalize-space()='Ir!' or normalize-space()='Go!']")
    CANCEL = (By.XPATH, "//button[contains(.,'Cancelar pedido') or contains(.,'Cancel the order')]")
