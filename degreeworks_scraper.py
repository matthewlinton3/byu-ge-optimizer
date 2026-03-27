"""
Scrape DegreeWorks using Playwright after CAS authentication.

Assumes a valid session has been established via the CAS ticket exchange.
The caller must provide a list of cookie dicts for the authenticated session.
"""
import asyncio
import re

from bs4 import BeautifulSoup

DEGREEWORKS_URL = "https://degreeworks.byu.edu"

# GE category names as they appear in DegreeWorks audit text
GE_CATEGORY_NAMES = [
    "American Heritage",
    "American Civilization",
    "Religion",
    "First-Year Writing",
    "Advanced Written",
    "Languages of Learning",
    "Arts",
    "Letters",
    "Life Sciences",
    "Physical Sciences",
    "Social",
    "Global",
    "Comparative Civilization",
]

_COURSE_RE = re.compile(r'\b([A-Z]{2,6})\s+(\d{3}[A-Z]?)\b')


async def _scrape_degreeworks_async(cas_cookies: list[dict]) -> dict:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-setuid-sandbox",
            ],
        )
        context = await browser.new_context()
        await context.add_cookies(cas_cookies)
        page = await context.new_page()

        try:
            await page.goto(DEGREEWORKS_URL, wait_until="networkidle", timeout=30_000)

            if "cas.byu.edu" in page.url:
                raise ValueError("CAS authentication failed — session cookies rejected")

            await page.wait_for_load_state("domcontentloaded", timeout=15_000)
            html = await page.content()
        finally:
            await browser.close()

    result = _parse_degreeworks_html(html)
    result["raw_html"] = html
    return result


def _parse_degreeworks_html(html: str) -> dict:
    """Parse a DegreeWorks audit page and return structured GE data."""
    soup = BeautifulSoup(html, "lxml")

    result: dict = {
        "net_id": "",
        "major": "",
        "completed_ge": [],
        "in_progress_ge": [],
        "courses_taken": [],
    }

    # Major — look in common header elements
    for selector in ["[class*='major']", "[class*='program']", "[class*='degree']", "h2", "h3"]:
        el = soup.select_one(selector)
        if el:
            text = el.get_text(strip=True)
            if len(text) > 3:
                result["major"] = text
                break

    # Completed GE — DegreeWorks marks satisfied blocks with RuleComplete / complete / satisfied
    complete_selectors = [
        "[class*='RuleComplete']",
        "[class*='Complete']",
        "[class*='complete']",
        "[class*='satisfied']",
        "[class*='met']",
    ]
    for sel in complete_selectors:
        for block in soup.select(sel):
            text = block.get_text(" ", strip=True).lower()
            for cat in GE_CATEGORY_NAMES:
                if cat.lower() in text and cat not in result["completed_ge"]:
                    result["completed_ge"].append(cat)

    # All course codes mentioned anywhere in the page
    for match in _COURSE_RE.finditer(html):
        code = f"{match.group(1)} {match.group(2)}"
        if code not in result["courses_taken"]:
            result["courses_taken"].append(code)

    return result


def scrape_degreeworks_sync(cas_cookies: list[dict]) -> dict:
    """Synchronous wrapper — safe to call from Streamlit."""
    return asyncio.run(_scrape_degreeworks_async(cas_cookies))
