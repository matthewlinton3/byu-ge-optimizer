"""
BYU MyMap Browser-Based Login
==============================
Opens a real Chrome browser window so the user can log in to mymap.byu.edu
manually — including Duo 2FA — without ever passing credentials through this app.
Once the user completes login, this module extracts the authenticated session
cookies and uses them with requests to scrape the degree audit.

SECURITY:
  - Credentials never enter this application. The user types them directly
    into the browser window (same as using the site normally).
  - Only session cookies are extracted — standard browser behavior.
  - Cookies are held in memory only and discarded when the session ends.
  - No credentials appear in any log, debug output, or exception message.
"""

import time

import requests

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
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
LOGIN_POLL_INTERVAL = 2    # seconds between URL checks
PAGE_SETTLE_DELAY   = 4    # seconds to wait after login detected for page to load
DEFAULT_TIMEOUT     = 180  # seconds (3 minutes) for user to complete login


# ── Public entry point ────────────────────────────────────────────────────────

def browser_login_and_scrape(timeout_seconds: int = DEFAULT_TIMEOUT) -> dict:
    """
    Opens Chrome, navigates to mymap.byu.edu, and waits for the user to log in
    (including Duo 2FA). Once login is detected, extracts session cookies and
    scrapes the degree audit using the authenticated session.

    Returns the same dict format as mymap_scraper.login_and_scrape():
        {
            "success":             bool,
            "error":               str | None,
            "ge_completed":        set,
            "ge_remaining":        set,
            "ge_partial":          dict,
            "completed_courses":   set,
            "in_progress_courses": set,
            "raw_requirements":    dict,
            "debug":               dict,
        }
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
        result["error"] = (
            "Selenium is not installed. "
            "Run: pip install selenium webdriver-manager"
        )
        return result

    driver  = None
    session = None

    try:
        # ── 1. Launch Chrome ──────────────────────────────────────────────────
        debug["steps"].append("Step 1: Launching Chrome browser...")
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # NOT headless — the user must interact with the real browser window

        try:
            # Try modern Selenium Manager (built into Selenium 4.6+)
            driver = webdriver.Chrome(options=options)
        except Exception:
            # Fall back to webdriver-manager for older Selenium versions
            service = Service(ChromeDriverManager().install())
            driver  = webdriver.Chrome(service=service, options=options)

        debug["steps"].append("  → Chrome launched successfully")

        # ── 2. Navigate to MyMap ──────────────────────────────────────────────
        debug["steps"].append(f"Step 2: Opening {MYMAP_BASE} in browser")
        driver.get(MYMAP_BASE)
        debug["cas_redirect"] = driver.current_url
        debug["steps"].append(f"  → Browser at: {driver.current_url}")

        # ── 3. Wait for user to complete login ────────────────────────────────
        debug["steps"].append(
            f"Step 3: Waiting up to {timeout_seconds}s for user to log in..."
        )

        deadline  = time.time() + timeout_seconds
        logged_in = False

        while time.time() < deadline:
            try:
                current_url = driver.current_url
            except Exception:
                # Browser was closed by the user
                debug["warnings"].append("Browser window was closed before login completed.")
                break

            on_mymap  = MYMAP_HOST in current_url
            on_cas    = CAS_HOST   in current_url
            logged_in = on_mymap and not on_cas

            if logged_in:
                debug["steps"].append(f"  → Login detected — URL: {current_url}")
                debug["final_url"] = current_url
                break

            time.sleep(LOGIN_POLL_INTERVAL)

        if not logged_in:
            result["error"] = (
                f"Login timed out after {timeout_seconds} seconds, or the browser was closed. "
                "Please try again and complete login within 3 minutes."
            )
            debug["warnings"].append(result["error"])
            return result

        # Give the page a moment to finish loading after login
        debug["steps"].append(f"  → Waiting {PAGE_SETTLE_DELAY}s for page to settle...")
        time.sleep(PAGE_SETTLE_DELAY)

        # ── 4. Extract session cookies ────────────────────────────────────────
        debug["steps"].append("Step 4: Extracting session cookies from browser...")
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

        # ── 6. Scrape degree audit ─────────────────────────────────────────────
        debug["steps"].append("Step 6: Scraping degree audit with captured session...")
        pages = _scrape_mymap(session, debug)

        if not pages:
            result["error"] = (
                "Logged in successfully but could not find degree audit content on MyMap. "
                "The page may not have loaded, or MyMap's URL structure may have changed. "
                "Try the PDF upload tab instead."
            )
            return result

        # ── 7. Parse requirements ──────────────────────────────────────────────
        debug["steps"].append("Step 7: Parsing GE requirements from scraped pages...")
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
