"""
BYU GE Requirements Scraper
============================
Scrapes the official BYU GE requirement pages from catalog.byu.edu,
merges the results with the authoritative course pools from pathways.py,
and writes the combined mapping to ge_requirements.py.

Run once to generate ge_requirements.py:
    python scrape_ge_requirements.py

The result is a dict: {GE category name → sorted list of valid course codes}.

Data sources (merged):
  1. catalog.byu.edu subpages — courses shown with explicit codes (e.g. BIOL 130)
  2. pathways.py PATHWAYS — authoritative curated course pools for each category
     (covers the courses not rendered in catalog HTML due to Coursedog's JS rendering)
"""

import re
import sys
import time
import pprint

import requests
from bs4 import BeautifulSoup

# ── Import pathways data ──────────────────────────────────────────────────────
sys.path.insert(0, ".")
from pathways import PATHWAYS

# ── Category → Coursedog page ID mapping ─────────────────────────────────────
CATEGORY_PAGES = {
    "American Heritage": [
        "etcMcLPynkU39DOba7Nt",
    ],
    "Global and Cultural Awareness": [
        "sG7A2OCx1J5kVfFC0RrD",
    ],
    "First-Year Writing": [
        "pebH2QP1qDF5IRZWAJB5",
    ],
    "Advanced Written and Oral Communication": [
        "qQt373mrrWfQWrKO2xYx",
    ],
    "Languages of Learning (Quantitative)": [
        "zt4tySdIAsvXxrtnJyy2",  # Quantitative Reasoning
        "xIjTV0CGd9mWg2cwbmp8",  # Languages of Learning
    ],
    "American Civilization": [
        "poUbjdX27rnoApiy78mc",   # Civilization 1
    ],
    "Comparative Civilization": [
        "vlLAPgRgIRsEvkRQwFm7",   # Civilization 2
    ],
    "Arts": [
        "ykeRT2EfmSTHvuJUA51L",
    ],
    "Letters": [
        "tVQyxvEHzqVaivhb5rtF",
    ],
    "Scientific Principles and Reasoning (Life Sciences)": [
        "8VbKODHxb2FZXJaSheen",
    ],
    "Scientific Principles and Reasoning (Physical Sciences)": [
        "0A8ilAKiFyODGH1KEkJj",
    ],
    "Social and Behavioral Sciences": [
        "GtBcUol64p4fvFNbW4Io",
    ],
    "Religion": [
        "n4WXDGZw30lJhuUADcp3",   # BYU Religion Hours overview
        "hVM9zB9ygH2TLc5XmZ5P",   # Foundations of the Restoration
        "PKWE6qOHznWkgupGsKsR",   # Tchgs & Doctrine of Book of Mormon
        "LDghjNDnbQYfKxdzXqCc",   # Christ and the Everlasting Gospel
        "ehUngBGvXbjtl7k4d1eh",   # The Eternal Family
    ],
}

BASE_URL = "https://catalog.byu.edu/pages/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# E-prefix codes and admin codes to filter out (not real BYU Banner codes)
SKIP_PREFIXES = {"UT", "EBIOL", "ECHEM", "EPHSCS", "EMATH", "ESTAT", "ECS", "EENGL"}


def fetch_page(page_id: str) -> str:
    url = BASE_URL + page_id
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def extract_codes_from_html(html: str) -> list[str]:
    """
    Parse <p> tags and extract course codes in format 'DEPT NNN - Title'.
    Filters out non-standard E-prefix and admin codes.
    """
    soup = BeautifulSoup(html, "lxml")
    codes = set()

    for p in soup.find_all("p"):
        text = p.get_text(separator=" ", strip=True)
        # Match course code at the very start of the text (before " - ")
        m = re.match(r"^([A-Z]{1,6}(?:\s[A-Z])?\s+\d{3}[A-Z]?)\s*-", text)
        if m:
            code = re.sub(r"\s+", " ", m.group(1)).strip()
            dept = code.split()[0]
            if dept not in SKIP_PREFIXES:
                codes.add(code)

    return sorted(codes)


def scrape_catalog() -> dict[str, set[str]]:
    """Fetch catalog pages and return {category: set of course codes}."""
    catalog_codes: dict[str, set[str]] = {}

    for category, page_ids in CATEGORY_PAGES.items():
        codes = set()
        for page_id in page_ids:
            print(f"  Fetching /pages/{page_id} ({category})", end=" ... ", flush=True)
            try:
                html = fetch_page(page_id)
                found = extract_codes_from_html(html)
                codes.update(found)
                print(f"{len(found)} codes")
            except Exception as exc:
                print(f"ERROR: {exc}")
            time.sleep(0.4)
        catalog_codes[category] = codes

    return catalog_codes


def extract_pathway_codes() -> dict[str, set[str]]:
    """
    Pull all explicit course_pool entries from pathways.py PATHWAYS.
    These are the authoritative curated codes for each GE category.
    """
    pathway_codes: dict[str, set[str]] = {}

    for category, pathways_list in PATHWAYS.items():
        codes = set()
        for pathway in pathways_list:
            if pathway.course_pool:
                codes.update(pathway.course_pool)
        pathway_codes[category] = codes

    return pathway_codes


def merge(
    catalog: dict[str, set[str]],
    pathways: dict[str, set[str]],
) -> dict[str, list[str]]:
    """Merge catalog + pathways codes per category, return sorted lists."""
    all_categories = set(catalog.keys()) | set(pathways.keys())
    result = {}
    for cat in sorted(all_categories):
        combined = (catalog.get(cat) or set()) | (pathways.get(cat) or set())
        result[cat] = sorted(combined)
    return result


def write_output(ge_requirements: dict[str, list[str]], output_path: str = "ge_requirements.py"):
    """Write the merged data as an importable Python dict."""
    header = [
        '"""',
        "BYU GE Requirements — Official Course Lists",
        "",
        "Auto-generated by scrape_ge_requirements.py.",
        "Sources:",
        "  1. catalog.byu.edu GE subpages (explicit course codes rendered in SSR HTML)",
        "  2. pathways.py PATHWAYS (curated course pools, authoritative for most categories)",
        "",
        "Maps each GE category name to the list of valid course codes.",
        "Import: from ge_requirements import GE_REQUIREMENTS",
        '"""',
        "",
        "GE_REQUIREMENTS = " + pprint.pformat(ge_requirements, indent=4, width=100),
        "",
    ]
    with open(output_path, "w") as f:
        f.write("\n".join(header))
    print(f"\n✅ Wrote {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("BYU GE Requirements Scraper")
    print("=" * 60)

    print("\n[1/3] Scraping catalog.byu.edu ...")
    catalog = scrape_catalog()

    print("\n[2/3] Extracting pathways.py course pools ...")
    pathways = extract_pathway_codes()
    for cat, codes in pathways.items():
        print(f"  {cat}: {len(codes)} codes from pathways")

    print("\n[3/3] Merging and writing ge_requirements.py ...")
    merged = merge(catalog, pathways)
    total = sum(len(v) for v in merged.values())
    print(f"\nTotal: {total} course codes across {len(merged)} GE categories")
    for cat, codes in merged.items():
        print(f"  [{len(codes):3d}] {cat}")

    write_output(merged)
