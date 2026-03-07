"""
BYU MyMap Browser-Based Login
==============================
Two modes depending on environment:

LOCAL (default):
  Opens a visible Chrome window. User logs in manually — including Duo 2FA.
  Detects login completion by polling the URL, then extracts session cookies.
  Credentials never pass through this app.

RAILWAY (IS_RAILWAY=True, detected via RAILWAY_ENVIRONMENT env var):
  Launches headless Chrome (system Chromium installed via nixpacks.toml).
  Provides helper functions so app.py can drive a step-by-step visual login
  flow inside Streamlit: CAS page screenshot → fill credentials → Duo screenshot
  → user approves on phone → session captured → degree audit scraped.

SECURITY:
  - In local mode: credentials never enter this application.
  - In Railway mode: credentials are sent via send_keys() directly to the
    headless browser's CAS form field; they are never stored, logged, or
    returned by any function. The Python string goes out of scope immediately.
  - Only session cookies are extracted — standard browser behavior.
  - Cookies are held in memory only for the duration of the scrape.
"""

import os
import re
import shutil
import time

import requests

# ── Environment detection ─────────────────────────────────────────────────────
IS_RAILWAY = bool(os.environ.get("RAILWAY_ENVIRONMENT"))

# ── Optional Selenium import ──────────────────────────────────────────────────
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

from mymap_scraper import (
    MYMAP_BASE,
    HEADERS,
    _scrape_mymap,
    _parse_all_pages,
)

# ── Constants ─────────────────────────────────────────────────────────────────

MYMAP_HOST          = "mymap.byu.edu"
CAS_HOST            = "cas.byu.edu"
LOGIN_POLL_INTERVAL = 2    # seconds between URL checks (local mode)
PAGE_SETTLE_DELAY   = 4    # seconds to wait after login detected (local mode)
DEFAULT_TIMEOUT     = 180  # seconds (3 min) for user to complete login (local)

_DUO_RE = re.compile(r"duo[- ]?security|two.factor|2fa|mfa|duosecurity", re.IGNORECASE)


# ── Driver creation ───────────────────────────────────────────────────────────

def create_driver(headless: bool = False):
    """
    Create and return a Selenium Chrome WebDriver.

    headless=True  → Railway mode: headless Chromium via system nixpkg binaries.
    headless=False → Local mode: visible Chrome window the user can interact with.
    """
    if not HAS_SELENIUM:
        raise RuntimeError("Selenium is not installed. Run: pip install selenium webdriver-manager")

    options = Options()

    if headless:
        # Railway/server mode — system Chromium installed by nixpacks.toml
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")

        # Locate system Chromium binary (nixpkg)
        chromium = shutil.which("chromium") or shutil.which("chromium-browser")
        if chromium:
            options.binary_location = chromium

        # Locate system chromedriver (nixpkg)
        chromedriver = shutil.which("chromedriver")
        if chromedriver:
            return webdriver.Chrome(service=Service(chromedriver), options=options)
        else:
            return webdriver.Chrome(options=options)

    else:
        # Local interactive mode — user sees the browser window
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            # Modern Selenium Manager (built-in to Selenium 4.6+)
            return webdriver.Chrome(options=options)
        except Exception:
            # Fallback to webdriver-manager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)


# ── Railway headless helper functions ─────────────────────────────────────────

def navigate_to_login(driver) -> str:
    """
    Navigate to mymap.byu.edu (which redirects to the BYU CAS login page).
    Returns a base64-encoded PNG screenshot of the current page.
    """
    driver.get(MYMAP_BASE)
    time.sleep(2)  # Allow redirect to complete
    return driver.get_screenshot_as_base64()


def fill_cas_credentials(driver, netid: str, password: str) -> None:
    """
    Find the BYU CAS login form, fill in the NetID and password, and submit.
    Clears the password field (best-effort) before navigating away.
    Credentials are passed directly to the browser via send_keys() and are
    not stored or returned by this function.
    """
    wait = WebDriverWait(driver, 15)

    try:
        username_el = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    except Exception as exc:
        raise RuntimeError(f"Could not find username field on CAS page: {exc}") from exc

    username_el.clear()
    username_el.send_keys(netid)

    try:
        password_el = driver.find_element(By.NAME, "password")
    except Exception as exc:
        raise RuntimeError(f"Could not find password field on CAS page: {exc}") from exc

    password_el.clear()
    password_el.send_keys(password)

    # Submit the form
    try:
        submit_el = driver.find_element(
            By.CSS_SELECTOR,
            "input[type='submit'], button[type='submit'], .btn-submit, #submitBtn",
        )
        submit_el.click()
    except Exception:
        password_el.submit()  # fallback: submit the enclosing form

    # Best-effort: clear password from browser DOM before navigation completes
    try:
        password_el.clear()
    except Exception:
        pass  # StaleElementReferenceException after redirect — expected and fine

    time.sleep(3)  # Wait for redirect/response


def detect_login_state(driver) -> str:
    """
    Inspect the browser's current URL and page source to determine login status.

    Returns one of:
        "logged_in"  — successfully on mymap.byu.edu
        "duo"        — Duo 2FA challenge page
        "cas_login"  — still on CAS login (wrong credentials?)
        "unknown"    — other/intermediate page
        "error"      — driver unresponsive (browser closed, etc.)
    """
    try:
        current = driver.current_url
        source  = driver.page_source
    except Exception:
        return "error"

    if MYMAP_HOST in current and CAS_HOST not in current:
        return "logged_in"
    if _DUO_RE.search(source) or "duosecurity" in current.lower():
        return "duo"
    if CAS_HOST in current:
        return "cas_login"
    return "unknown"


def take_screenshot_base64(driver) -> str:
    """Return a base64-encoded PNG screenshot of the current browser view."""
    try:
        return driver.get_screenshot_as_base64()
    except Exception:
        return ""


def scrape_from_driver(driver) -> dict:
    """
    Extract authenticated session cookies from the driver, scrape mymap.byu.edu,
    parse GE requirements, and return the same result dict as login_and_scrape().
    The driver is NOT closed here — the caller is responsible for cleanup.
    """
    debug = {
        "steps":             ["[Browser Login] Extracting session cookies from browser..."],
        "warnings":          [],
        "page_texts":        {},
        "all_courses_found": [],
        "cas_redirect":      "",
        "final_url":         "",
        "pages_scraped":     0,
        "duo_detected":      False,
        "browser_login":     True,
    }
    result = {
        "success":             False,
        "error":               None,
        "ge_completed":        set(),
        "ge_remaining":        set(),
        "ge_partial":          {},
        "completed_courses":   set(),
        "in_progress_courses": set(),
        "raw_requirements":    {},
        "debug":               debug,
    }

    session = None
    try:
        selenium_cookies = driver.get_cookies()
        debug["steps"].append(f"  → {len(selenium_cookies)} cookies extracted")
        debug["final_url"] = driver.current_url

        session = requests.Session()
        session.headers.update(HEADERS)
        for c in selenium_cookies:
            domain = c.get("domain", "").lstrip(".")
            session.cookies.set(c["name"], c["value"], domain=domain, path=c.get("path", "/"))

        pages = _scrape_mymap(session, debug)
        if not pages:
            result["error"] = (
                "Logged in but could not find degree audit content on MyMap. "
                "Try uploading the PDF instead."
            )
            return result

        _parse_all_pages(pages, result, debug)
        result["success"] = True

    except Exception as exc:
        result["error"] = f"Scrape error: {exc}"
        debug["warnings"].append(result["error"])
    finally:
        if session is not None:
            try:
                session.close()
            except Exception:
                pass

    return result


# ── Local (non-headless) full pipeline ───────────────────────────────────────

def browser_login_and_scrape(timeout_seconds: int = DEFAULT_TIMEOUT) -> dict:
    """
    LOCAL MODE ONLY: Opens a visible Chrome window, waits for the user to log
    in (including Duo 2FA), then extracts session cookies and scrapes the
    degree audit.

    Returns the same dict format as mymap_scraper.login_and_scrape().
    """
    debug = {
        "steps":             [],
        "warnings":          [],
        "page_texts":        {},
        "all_courses_found": [],
        "cas_redirect":      "",
        "final_url":         "",
        "pages_scraped":     0,
        "duo_detected":      False,
        "browser_login":     True,
    }
    result = {
        "success":             False,
        "error":               None,
        "ge_completed":        set(),
        "ge_remaining":        set(),
        "ge_partial":          {},
        "completed_courses":   set(),
        "in_progress_courses": set(),
        "raw_requirements":    {},
        "debug":               debug,
    }

    if not HAS_SELENIUM:
        result["error"] = "Selenium is not installed. Run: pip install selenium webdriver-manager"
        return result

    driver = None
    session = None
    try:
        # ── 1. Launch visible Chrome ──────────────────────────────────────────
        debug["steps"].append("Step 1: Launching Chrome browser...")
        driver = create_driver(headless=False)
        debug["steps"].append("  → Chrome launched")

        # ── 2. Navigate to MyMap ──────────────────────────────────────────────
        debug["steps"].append(f"Step 2: Opening {MYMAP_BASE}")
        driver.get(MYMAP_BASE)
        debug["cas_redirect"] = driver.current_url
        debug["steps"].append(f"  → Browser at: {driver.current_url}")

        # ── 3. Wait for user to log in ────────────────────────────────────────
        debug["steps"].append(
            f"Step 3: Waiting up to {timeout_seconds}s for user to complete login..."
        )
        deadline  = time.time() + timeout_seconds
        logged_in = False

        while time.time() < deadline:
            try:
                current_url = driver.current_url
            except Exception:
                debug["warnings"].append("Browser window was closed before login completed.")
                break

            if MYMAP_HOST in current_url and CAS_HOST not in current_url:
                debug["steps"].append(f"  → Login detected — URL: {current_url}")
                debug["final_url"] = current_url
                logged_in = True
                break

            time.sleep(LOGIN_POLL_INTERVAL)

        if not logged_in:
            result["error"] = (
                f"Login timed out after {timeout_seconds}s, or the browser was closed. "
                "Please try again and complete login within 3 minutes."
            )
            debug["warnings"].append(result["error"])
            return result

        # Give the page time to fully settle after login redirect
        debug["steps"].append(f"  → Waiting {PAGE_SETTLE_DELAY}s for page to settle...")
        time.sleep(PAGE_SETTLE_DELAY)

        # ── 4. Extract cookies ────────────────────────────────────────────────
        debug["steps"].append("Step 4: Extracting session cookies...")
        selenium_cookies = driver.get_cookies()
        debug["steps"].append(f"  → {len(selenium_cookies)} cookies extracted")

        session = requests.Session()
        session.headers.update(HEADERS)
        for c in selenium_cookies:
            domain = c.get("domain", "").lstrip(".")
            session.cookies.set(c["name"], c["value"], domain=domain, path=c.get("path", "/"))

        # ── 5. Close browser ──────────────────────────────────────────────────
        debug["steps"].append("Step 5: Session captured — closing browser")
        driver.quit()
        driver = None

        # ── 6. Scrape degree audit ────────────────────────────────────────────
        debug["steps"].append("Step 6: Scraping degree audit...")
        pages = _scrape_mymap(session, debug)
        if not pages:
            result["error"] = (
                "Logged in but could not find degree audit content on MyMap. "
                "Try the PDF upload tab instead."
            )
            return result

        # ── 7. Parse ──────────────────────────────────────────────────────────
        debug["steps"].append("Step 7: Parsing GE requirements...")
        _parse_all_pages(pages, result, debug)
        result["success"] = True

    except Exception as exc:
        result["error"] = f"Browser login error: {exc}"
        debug["warnings"].append(result["error"])
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
        if session is not None:
            try:
                session.close()
            except Exception:
                pass

    return result
