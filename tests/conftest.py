import os
import pytest
from playwright.sync_api import sync_playwright
import requests
# import data fixtures so they are available to all tests
from tests.fixtures.data_fixtures import sample_users, sample_cards
from tests.fixtures.auth_fixtures import existing_user, auth_api

def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default="http://localhost:3000", help="Base URL for the frontend")
    parser.addoption("--api-url", action="store", default="http://localhost:8000", help="Base URL for the backend API")
    parser.addoption("--headed", action="store_true", default=False, help="Run browser headed (visible)")
    parser.addoption("--slow-mo", action="store", default=0, type=int, help="Slow motion in ms for headed runs")


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture(scope="session")
def api_url(request):
    return request.config.getoption("--api-url")


@pytest.fixture(scope="session")
def api_client(api_url):
    s = requests.Session()
    s.headers.update({"Accept": "application/json"})
    s.base_url = api_url
    return s


@pytest.fixture(scope="session")
def playwright_instance(request):
    with sync_playwright() as p:
        # attach pytest config so downstream fixtures can access runtime options
        p._pytest_config = request.config
        yield p


@pytest.fixture()
def browser(playwright_instance):
    # read runtime options
    config = getattr(playwright_instance, "_pytest_config", None)
    # fallback defaults
    headed = False
    slow_mo = 0
    if config:
        headed = config.getoption("--headed")
        slow_mo = config.getoption("--slow-mo")

    # launch browser according to options
    browser = playwright_instance.chromium.launch(headless=not headed, slow_mo=slow_mo if headed else 0)
    yield browser
    browser.close()


@pytest.fixture()
def page(browser, base_url):
    page = browser.new_page()
    # increase default timeout for slow test environments
    page.set_default_timeout(20000)
    # helpful convenience to navigate
    page.base_url = base_url

    # collect console messages and page errors to help debugging
    console_messages = []

    def _on_console(msg):
        try:
            console_messages.append(f"CONSOLE {msg.type}: {msg.text}")
        except Exception:
            console_messages.append(f"CONSOLE {msg.type}: <unserializable>")

    def _on_page_error(err):
        console_messages.append(f"PAGE_ERROR: {err}")

    page.on("console", _on_console)
    page.on("pageerror", _on_page_error)

    # attach to page so the pytest hook can access them
    page._console_messages = console_messages

    yield page

    try:
        page.close()
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # only act on call phase (when the test body ran)
    if rep.when == "call" and rep.failed:
        # store test artifacts inside the register tests folder to keep workspace tidy
        screenshots_dir = os.path.join("tests", "logs")
        os.makedirs(screenshots_dir, exist_ok=True)
        # attempt to find a playwright page fixture on the test item
        page = item.funcargs.get("page")
        test_name = item.name
        if page:
            img_path = os.path.join(screenshots_dir, f"{test_name}.png")
            log_path = os.path.join(screenshots_dir, f"{test_name}.log")
            try:
                page.screenshot(path=img_path, full_page=True)
            except Exception:
                img_path = None
            # write console messages if any
            messages = getattr(page, "_console_messages", None)
            try:
                if messages:
                    with open(log_path, "w", encoding="utf-8") as fh:
                        fh.write("\n".join(messages))
                else:
                    # attempt to dump limited info
                    with open(log_path, "w", encoding="utf-8") as fh:
                        fh.write("(no console messages captured)\n")
            except Exception:
                log_path = None

            # print helpful info for the test runner output
            if img_path:
                print(f"Saved screenshot: {img_path}")
            if log_path:
                print(f"Saved console log: {log_path}")

@pytest.fixture
def registered_user(api_client):

    created_users = []

    yield created_users

    # teardown
    for user in created_users:

        try:
            api_client.delete(
                f"/auth/users/{user['id']}"
            )
        except Exception:
            pass