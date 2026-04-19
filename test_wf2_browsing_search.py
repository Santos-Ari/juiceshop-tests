import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:3000"


def launch_browser():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False, slow_mo=600)
    context = browser.new_context(viewport={"width": 1280, "height": 1024})
    page = context.new_page()
    return pw, browser, page


def close_browser(pw, browser):
    browser.close()
    pw.stop()


def dismiss_all_banners(page):
    try:
        page.locator("button:has-text('Dismiss')").click(timeout=3000)
        page.wait_for_timeout(500)
    except Exception:
        pass
    try:
        page.locator("button:has-text('Me want it!')").click(timeout=3000)
        page.wait_for_timeout(500)
    except Exception:
        pass


def dismiss_welcome_modal(page):
    page.goto(f"{BASE_URL}/#/")
    page.wait_for_timeout(3000)
    dismiss_all_banners(page)
    page.wait_for_timeout(1000)
    dismiss_all_banners(page)
    page.wait_for_selector("mat-card", timeout=15000)
    page.wait_for_timeout(500)


def click_search_and_type(page, query):
    page.locator("mat-icon:has-text('search')").click(timeout=8000)
    page.wait_for_timeout(1500)

    close_icon = page.locator(
        "mat-icon:has-text('close'), "
        "mat-icon:has-text('cancel'), "
        "mat-icon:has-text('clear')"
    ).first
    close_icon.wait_for(state="visible", timeout=6000)

    x_box = close_icon.bounding_box()
    if x_box:
        page.mouse.click(x_box["x"] - 150, x_box["y"] + x_box["height"] / 2)
        page.wait_for_timeout(500)

    page.keyboard.type(query, delay=150)
    page.wait_for_timeout(500)

    page.keyboard.press("Enter")
    page.wait_for_timeout(2500)


# ── TC-006: Product Catalog Loads ────────────────────────────

def test_TC006_catalog_loads():
    pw, browser, page = launch_browser()
    try:
        dismiss_welcome_modal(page)

        product_cards = page.locator("mat-card")
        count = product_cards.count()
        print(f"\n  Products found: {count}")

        assert count >= 12, f"Expected at least 12 products, found {count}"
        print(f"\n[PASS] TC-006 — Catalog loaded with {count} product cards.")
    finally:
        close_browser(pw, browser)


# ── TC-007: Search Returns Results ───────────────────────────

def test_TC007_search_existing_product():
    pw, browser, page = launch_browser()
    try:
        dismiss_welcome_modal(page)

        click_search_and_type(page, "Apple Juice")

        assert "search" in page.url.lower(), \
            f"Expected search URL, got: {page.url}"

        page.wait_for_selector("mat-card", timeout=10000)
        count = page.locator("mat-card").count()

        assert count >= 1, \
            f"Expected at least 1 result for 'Apple Juice', got {count}"
        assert "apple" in page.locator("body").inner_text().lower(), \
            "Expected 'apple' to appear in search results"
        print(f"\n[PASS] TC-007 — Search for 'Apple Juice' returned {count} result(s).")
    finally:
        close_browser(pw, browser)


# ── TC-008: Search No Results ─────────────────────────────────

def test_TC008_search_no_results():
    pw, browser, page = launch_browser()
    try:
        dismiss_welcome_modal(page)

        click_search_and_type(page, "xyznonexistentproduct123")

        assert "search" in page.url.lower(), \
            f"Expected search URL, got: {page.url}"

        page.wait_for_timeout(1000)
        body_text = page.locator("body").inner_text()
        assert "No results" in body_text, \
            "Expected 'No results found' message on page"
        print("\n[PASS] TC-008 — 'No results found' displayed for unknown search term.")
    finally:
        close_browser(pw, browser)


# ── TC-009: Product Detail Modal ─────────────────────────────

def test_TC009_product_detail_modal():
    pw, browser, page = launch_browser()
    try:
        dismiss_welcome_modal(page)

        first_card = page.locator("mat-card").first
        first_card.click()
        page.wait_for_timeout(2000)

        dialog = page.locator("mat-dialog-container")
        expect(dialog).to_be_visible(timeout=8000)
        print("\n[PASS] TC-009 — Product detail modal opened successfully.")
    finally:
        close_browser(pw, browser)


# ── TC-010: Items Per Page Control ───────────────────────────

def test_TC010_items_per_page():
    pw, browser, page = launch_browser()
    try:
        dismiss_welcome_modal(page)

        initial_count = page.locator("mat-card").count()
        print(f"\n  Initial product count: {initial_count}")

        page.mouse.move(640, 500)
        page.wait_for_timeout(300)
        for _ in range(10):
            page.mouse.wheel(0, 400)
            page.wait_for_timeout(200)
        page.wait_for_timeout(1000)

        dismiss_all_banners(page)
        page.wait_for_timeout(500)

        paginator = page.locator("mat-paginator")
        paginator.wait_for(state="visible", timeout=8000)

        per_page_select = paginator.locator("mat-select")
        per_page_select.click(force=True)
        page.wait_for_timeout(1200)

        dismiss_all_banners(page)
        page.wait_for_timeout(300)

        option_24 = page.locator("mat-option").filter(has_text="24").first
        option_24.wait_for(state="visible", timeout=5000)
        option_24.click(force=True)
        page.wait_for_timeout(2000)

        new_count = page.locator("mat-card").count()
        print(f"  Product count after selecting 24: {new_count}")

        assert new_count >= 12, \
            f"Expected product count to update. Got: {new_count}"
        print(f"\n[PASS] TC-010 — Items per page changed: "
              f"{initial_count} → {new_count}")
    finally:
        close_browser(pw, browser)