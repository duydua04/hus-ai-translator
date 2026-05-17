from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


class TranslatorPage:
    URL = "http://localhost:3000/home/text"
    LOGIN_URL = "http://localhost:3000/login"

    # --- Auth locators ---
    EMAIL_INPUT    = (By.CSS_SELECTOR, "input[type='email'], input[name='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password'], input[name='password']")
    LOGIN_BUTTON   = (By.CSS_SELECTOR, "button[type='submit'], .btn--primary")

    # --- Translator locators ---
    SOURCE_SELECT  = (By.CSS_SELECTOR, ".translator__tabs .translator__select:first-of-type")
    TARGET_SELECT  = (By.CSS_SELECTOR, ".translator__tabs .translator__select:last-of-type")
    INPUT_TEXTAREA = (By.CSS_SELECTOR, ".translator__input")
    OUTPUT_TEXTAREA= (By.CSS_SELECTOR, ".translator__output")
    TRANSLATE_BTN  = (By.CSS_SELECTOR, ".translator__action .btn--primary")
    CLEAR_BTN      = (By.CSS_SELECTOR, ".action-btn[title='Xóa']")
    COPY_BTN       = (By.CSS_SELECTOR, ".action-btn[title='Sao chép']")
    CHAR_COUNTER   = (By.CSS_SELECTOR, ".translator__selector-left")
    SWAP_BTN       = (By.CSS_SELECTOR, ".translator__swap-btn")
    TRANSLATOR_BOX = (By.CSS_SELECTOR, ".translator__box")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # ------------------------------------------------------------------ #
    #  Auth helpers
    # ------------------------------------------------------------------ #
    def login(self, email: str, password: str):
        self.driver.get(self.LOGIN_URL)
        self.wait.until(EC.presence_of_element_located(self.EMAIL_INPUT)).send_keys(email)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()
        # Wait until redirected away from login page
        self.wait.until(EC.url_changes(self.LOGIN_URL))

    def open(self):
        self.driver.get(self.URL)
        self.wait.until(EC.presence_of_element_located(self.TRANSLATOR_BOX))

    def login_and_open(self, email: str = "user1@example.com", password: str = "Test1234!"):
        self.login(email, password)
        self.open()

    # ------------------------------------------------------------------ #
    #  Language selectors
    # ------------------------------------------------------------------ #
    def get_source_language(self) -> str:
        sel = Select(self.wait.until(EC.presence_of_element_located(self.SOURCE_SELECT)))
        return sel.first_selected_option.get_attribute("value")

    def get_target_language(self) -> str:
        sel = Select(self.wait.until(EC.presence_of_element_located(self.TARGET_SELECT)))
        return sel.first_selected_option.get_attribute("value")

    def select_source_language(self, value: str):
        sel = Select(self.wait.until(EC.presence_of_element_located(self.SOURCE_SELECT)))
        sel.select_by_value(value)

    def select_target_language(self, value: str):
        sel = Select(self.wait.until(EC.presence_of_element_located(self.TARGET_SELECT)))
        sel.select_by_value(value)

    def click_swap(self):
        self.wait.until(EC.element_to_be_clickable(self.SWAP_BTN)).click()

    # ------------------------------------------------------------------ #
    #  Input / output
    # ------------------------------------------------------------------ #
    def type_text(self, text: str):
        area = self.wait.until(EC.presence_of_element_located(self.INPUT_TEXTAREA))
        area.clear()
        area.send_keys(text)

    def get_input_text(self) -> str:
        return self.driver.find_element(*self.INPUT_TEXTAREA).get_attribute("value")

    def get_output_text(self) -> str:
        return self.driver.find_element(*self.OUTPUT_TEXTAREA).get_attribute("value")

    def get_char_counter_text(self) -> str:
        return self.wait.until(EC.presence_of_element_located(self.CHAR_COUNTER)).text

    # ------------------------------------------------------------------ #
    #  Actions
    # ------------------------------------------------------------------ #
    def click_translate(self):
        self.wait.until(EC.element_to_be_clickable(self.TRANSLATE_BTN)).click()

    def click_clear(self):
        self.wait.until(EC.element_to_be_clickable(self.CLEAR_BTN)).click()

    def click_copy(self):
        copy_btn = self.wait.until(EC.element_to_be_clickable(self.COPY_BTN))
        copy_btn.click()

    def is_copy_button_enabled(self) -> bool:
        btn = self.driver.find_element(*self.COPY_BTN)
        return btn.get_attribute("disabled") is None

    def wait_for_translation(self, timeout: int = 10):
        """Wait until output textarea is non-empty."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_element(*self.OUTPUT_TEXTAREA).get_attribute("value").strip() != ""
        )