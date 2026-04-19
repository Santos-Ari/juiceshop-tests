import time
import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:3000"

ENABLED_INPUT = "input:not([disabled]):not([type='hidden'])"


def launch_browser():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False, slow_mo=600)
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    return pw, browser, page


def close_browser(pw, browser):
    browser.close()
    pw.stop()


def dismiss_welcome_modal(page):
    page.goto(f"{BASE_URL}/#/")
    page.wait_for_timeout(3000)
    try:
        page.locator("button:has-text('Dismiss')").click(timeout=5000)
        page.wait_for_timeout(500)
    except Exception:
        pass
    try:
        page.locator("button:has-text('Me want it!')").click(timeout=3000)
        page.wait_for_timeout(500)
    except Exception:
        pass


def unique_email():
    ts = int(time.time())
    return f"testuser_{ts}@juicetest.com"


def fill_registration_form(page, email, password="Test@1234"):
    page.wait_for_selector(ENABLED_INPUT, timeout=10000)
    page.wait_for_timeout(1000)

    page.locator(ENABLED_INPUT).nth(0).click()
    page.locator(ENABLED_INPUT).nth(0).fill(email)
    page.wait_for_timeout(400)

    page.locator(ENABLED_INPUT).nth(1).click()
    page.locator(ENABLED_INPUT).nth(1).fill(password)
    page.wait_for_timeout(400)

    page.locator(ENABLED_INPUT).nth(2).click()
    page.locator(ENABLED_INPUT).nth(2).fill(password)
    page.wait_for_timeout(400)

    page.locator("mat-select").click()
    page.wait_for_timeout(1000)
    page.locator("mat-option").first.click()
    page.wait_for_timeout(800)

    page.wait_for_selector(ENABLED_INPUT, timeout=5000)
    page.locator(ENABLED_INPUT).nth(3).click()
    page.locator(ENABLED_INPUT).nth(3).fill("TestAnswer")
    page.wait_for_timeout(400)


def register_user(page, email, password="Test@1234"):
    dismiss_welcome_modal(page)
    page.goto(f"{BASE_URL}/#/register")
    page.wait_for_timeout(2000)
    fill_registration_form(page, email, password)
    page.locator("button[type='submit']").click()
    page.wait_for_url(f"{BASE_URL}/#/login", timeout=15000)


def is_error_shown(page):
    selectors = [
        "simple-snack-bar",
        "mat-snack-bar-container",
        ".mat-mdc-snack-bar-container",
        ".cdk-overlay-container .mat-mdc-snackbar-surface",
        "[class*='snack-bar']",
    ]
    for sel in selectors:
        try:
            if page.locator(sel).is_visible():
                return True
        except Exception:
            pass
    return False


# ── TC-001: Valid User Registration ──────────────────────────

def test_TC001_valid_registration():
    pw, browser, page = launch_browser()
    try:
        email = unique_email()
        dismiss_welcome_modal(page)
        page.goto(f"{BASE_URL}/#/register")
        page.wait_for_timeout(2000)
        fill_registration_form(page, email)
        page.locator("button[type='submit']").click()

        expect(page).to_have_url(f"{BASE_URL}/#/login", timeout=15000)
        print(f"\n[PASS] TC-001 — User registered: {email}")
    finally:
        close_browser(pw, browser)


# ── TC-002: Duplicate Email Registration ─────────────────────

def test_TC002_duplicate_email():
    pw, browser, page = launch_browser()
    try:
        email = unique_email()

        register_user(page, email)

        page.goto(f"{BASE_URL}/#/register")
        page.wait_for_timeout(2000)
        fill_registration_form(page, email)
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(3000)

        assert "register" in page.url or is_error_shown(page), \
            "Expected an error for duplicate email"
        print(f"\n[PASS] TC-002 — Duplicate email error shown for: {email}")
    finally:
        close_browser(pw, browser)


# ── TC-003: Weak Password Blocked ────────────────────────────

def test_TC003_weak_password():
    pw, browser, page = launch_browser()
    try:
        dismiss_welcome_modal(page)
        page.goto(f"{BASE_URL}/#/register")
        page.wait_for_timeout(2000)

        page.wait_for_selector(ENABLED_INPUT, timeout=10000)
        page.wait_for_timeout(500)

        page.locator(ENABLED_INPUT).nth(0).click()
        page.locator(ENABLED_INPUT).nth(0).fill("weaktest@juicetest.com")
        page.wait_for_timeout(400)

        page.locator(ENABLED_INPUT).nth(1).click()
        page.locator(ENABLED_INPUT).nth(1).fill("ab")
        page.wait_for_timeout(1000)

        register_btn = page.locator("button[type='submit']")
        assert register_btn.is_disabled(), \
            "Expected Register button to be disabled for short password"
        print("\n[PASS] TC-003 — Short password correctly blocked registration.")
    finally:
        close_browser(pw, browser)


# ── TC-004: Valid Login ───────────────────────────────────────

def test_TC004_valid_login():
    pw, browser, page = launch_browser()
    try:
        dismiss_welcome_modal(page)
        page.goto(f"{BASE_URL}/#/login")
        page.wait_for_timeout(1000)

        page.wait_for_selector(ENABLED_INPUT, timeout=10000)
        page.wait_for_timeout(500)

        page.locator(ENABLED_INPUT).nth(0).click()
        page.locator(ENABLED_INPUT).nth(0).fill("admin@juice-sh.op")
        page.wait_for_timeout(400)

        page.locator(ENABLED_INPUT).nth(1).click()
        page.locator(ENABLED_INPUT).nth(1).fill("admin123")
        page.wait_for_timeout(400)

        page.locator("button[type='submit']").click()
        page.wait_for_timeout(3000)

        assert "login" not in page.url.lower(), \
            f"Still on login page after login. URL: {page.url}"
        expect(page.locator(
            "button[aria-label='Show/hide account menu']"
        )).to_be_visible(timeout=10000)
        print(f"\n[PASS] TC-004 — Login successful for: admin@juice-sh.op")
    finally:
        close_browser(pw, browser)


# ── TC-005: Login with Invalid Password ──────────────────────

def test_TC005_invalid_login():
    pw, browser, page = launch_browser()
    try:
        dismiss_welcome_modal(page)
        page.goto(f"{BASE_URL}/#/login")
        page.wait_for_timeout(1000)

        page.wait_for_selector(ENABLED_INPUT, timeout=10000)
        page.wait_for_timeout(500)

        page.locator(ENABLED_INPUT).nth(0).click()
        page.locator(ENABLED_INPUT).nth(0).fill("admin@juice-sh.op")
        page.wait_for_timeout(400)

        page.locator(ENABLED_INPUT).nth(1).click()
        page.locator(ENABLED_INPUT).nth(1).fill("WrongPass!99")
        page.wait_for_timeout(400)

        page.locator("button[type='submit']").click()
        page.wait_for_timeout(3000)

        body_text = page.locator("body").inner_text()
        assert "Invalid" in body_text, \
            f"Expected 'Invalid email or password.' on page, got: {body_text[:200]}"
        assert "login" in page.url.lower(), \
            f"Expected to remain on login page. URL: {page.url}"
        print("\n[PASS] TC-005 — Invalid login error shown correctly.")
    finally:
        close_browser(pw, browser)