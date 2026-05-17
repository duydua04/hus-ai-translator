"""
conftest.py  –  fixture tập trung cho toàn bộ test suite
─────────────────────────────────────────────────────────
Sử dụng pytest-playwright: 'page' được inject tự động,
KHÔNG tạo browser / context thủ công.

Cấu hình browser (headless, viewport, …) đặt trong pytest.ini
hoặc truyền qua CLI:  pytest --headed --browser firefox
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page

# ── load biến môi trường từ .env ─────────────────────────────────────────────
load_dotenv()

BASE_URL     = os.getenv("BASE_URL",   "http://localhost:3000")
ADMIN_URL    = os.getenv("ADMIN_URL",  "http://localhost:3001")  # admin chạy cổng riêng
FIXTURES_DIR = Path(__file__).parent / "data" / "fixtures"


# ══════════════════════════════════════════════════════════════════════════════
# 1.  CẤU HÌNH PLAYWRIGHT  (hook chính thức của pytest-playwright)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """
    Ghi đè browser context mặc định của pytest-playwright.
    Thêm base_url và viewport để tất cả fixture dùng chung.
    """
    return {
        **browser_context_args,
        "base_url": BASE_URL,
        "viewport": {"width": 1280, "height": 800},
        "locale": "vi-VN",
    }


# ══════════════════════════════════════════════════════════════════════════════
# 2.  PAGE OBJECTS  (pytest-playwright inject 'page' tự động)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def register_page(page: Page):
    """Page Object trang Đăng ký."""
    from pages.user.register_page import RegisterPage
    rp = RegisterPage(page, BASE_URL)
    rp.navigate()
    return rp


@pytest.fixture(scope="function")
def user_login_page(page: Page):
    """Page Object trang Đăng nhập – User."""
    from pages.user.user_login_page import UserLoginPage
    lp = UserLoginPage(page, BASE_URL)
    lp.navigate()
    return lp


@pytest.fixture(scope="function")
def admin_login_page(page: Page):
    """Page Object trang Đăng nhập – Admin (cổng 3001)."""
    from pages.admin.admin_login_page import AdminLoginPage
    alp = AdminLoginPage(page, ADMIN_URL)
    alp.navigate()
    return alp


@pytest.fixture(scope="function")
def home_page(page: Page):
    """Page Object trang chủ dịch thuật."""
    from pages.home_page import HomePage
    hp = HomePage(page, BASE_URL)
    hp.navigate()
    return hp


@pytest.fixture(scope="function")
def admin_user_page(page: Page):
    """Page Object trang quản lý User – Admin (cổng 3001)."""
    from pages.admin.admin_user_page import AdminUserPage
    return AdminUserPage(page, ADMIN_URL)


@pytest.fixture(scope="function")
def dashboard_page(page: Page):
    """Page Object trang Dashboard – Admin (cổng 3001)."""
    from pages.admin.dashboard_page import DashboardPage
    return DashboardPage(page, ADMIN_URL)


@pytest.fixture(scope="function")
def feedback_page(page: Page):
    """Page Object trang Feedback – Admin (cổng 3001)."""
    from pages.admin.feedback_page import FeedbackPage
    return FeedbackPage(page, ADMIN_URL)


# ══════════════════════════════════════════════════════════════════════════════
# 3.  TEST DATA  (đọc từ JSON fixture – scope=session, parse 1 lần)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def users_fixture() -> dict:
    """
    Đọc data/fixtures/users.json, trả về dict index theo 'id'.
    Dùng: users_fixture["valid_user"]["email"]
    """
    raw = json.loads((FIXTURES_DIR / "users.json").read_text(encoding="utf-8"))
    return {u["id"]: u for u in raw["users"]}


@pytest.fixture(scope="session")
def valid_user(users_fixture: dict) -> dict:
    return users_fixture["valid_user"]


@pytest.fixture(scope="session")
def admin_user(users_fixture: dict) -> dict:
    return users_fixture["admin_user"]


@pytest.fixture(scope="session")
def locked_user(users_fixture: dict) -> dict:
    return users_fixture["locked_user"]


@pytest.fixture(scope="session")
def unverified_user(users_fixture: dict) -> dict:
    return users_fixture["unverified_user"]


# ══════════════════════════════════════════════════════════════════════════════
# 4.  AUTHENTICATED PAGES  (đã đăng nhập sẵn – tránh lặp bước login)
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def authenticated_user_page(page: Page, valid_user: dict) -> Page:
    """
    Trả về Page đã đăng nhập với tài khoản user thông thường.
    Dùng cho test cần trạng thái đã đăng nhập mà không muốn
    lặp lại bước login (ví dụ: test lịch sử, feedback, dịch thuật).
    """
    from pages.user.user_login_page import UserLoginPage
    lp = UserLoginPage(page, BASE_URL)
    lp.navigate()
    lp.login(valid_user["email"], valid_user["password"])
    page.wait_for_load_state("networkidle")
    return page


@pytest.fixture(scope="function")
def authenticated_admin_page(page: Page, admin_user: dict) -> Page:
    """
    Trả về Page đã đăng nhập với tài khoản admin (cổng 3001).
    Dùng cho test Dashboard, quản lý user, feedback admin.
    """
    from pages.admin.admin_login_page import AdminLoginPage
    alp = AdminLoginPage(page, ADMIN_URL)
    alp.navigate()
    alp.login(admin_user["email"], admin_user["password"])
    page.wait_for_load_state("networkidle")
    return page