"""
BYU MyMap Degree Audit Scraper
===============================
Logs into mymap.byu.edu via BYU CAS SSO and scrapes the student's
personal degree audit including GE requirements, completed courses,
in-progress courses, and remaining requirements.

SECURITY POLICY:
  - Credentials are NEVER written to disk, logged, or stored in any database.
  - NetID and password are held only in local variables for the duration of
    the CAS POST request, then immediately discarded.
  - The requests.Session() object (which holds session cookies) is used only
    within this module and never serialized or persisted.
  - No credential appears in any debug output, log line, or exception message.
"""

import re
import time
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ── Constants ─────────────────────────────────────────────────────────────────

MYMAP_BASE       = "https://mymap.byu.edu"
CAS_BASE         = "https://cas.byu.edu"
CAS_LOGIN_URL    = f"{CAS_BASE}/cas/login"
REQUEST_TIMEOUT  = 20  # seconds

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# GE category keywords for text-based detection
GE_KEYWORDS = {
    "American Heritage":                                    ["american heritage"],
    "Religion":                                             ["religion"],
    "First-Year Writing":                                   ["first-year writing", "first year writing", "wrtg 150"],
    "Advanced Written and Oral Communication":              ["advanced written", "oral communication"],
    "Languages of Learning (Quantitative)":                 ["languages of learning", "quantitative reasoning"],
    "Arts":                                                 ["arts"],
    "Letters":                                              ["letters"],
    "Scientific Principles and Reasoning (Life Sciences)":  ["life sciences", "life science"],
    "Scientific Principles and Reasoning (Physical Sciences)": ["physical sciences", "physical science"],
    "Social and Behavioral Sciences":                       ["social and behavioral", "social & behavioral"],
    "American Civilization":                                ["american civilization"],
    "Global and Cultural Awareness":                        ["global and cultural", "global & cultural", "cultural awareness"],
    "Comparative Civilization":                             ["comparative civilization"],
}

COURSE_CODE_RE   = re.compile(r"\b([A-Z]{2,6}(?:\s+[A-Z])?\s+\d{3}[A-Z]?)\b")
COMPLETION_RE    = re.compile(
    r"satisfied|complete[d]?|fulfilled|\b(met)\b|✓|✔|passed|\b[ABCD][+-]?\b",
    re.IGNORECASE,
)
IN_PROGRESS_RE   = re.compile(
    r"in[- ]progress|enrolled|current semester|in progress",
    re.IGNORECASE,
)
NOT_DONE_RE      = re.compile(
    r"not satisfied|not complete|not fulfilled|remaining|still needed|incomplete",
    re.IGNORECASE,
)
DUO_RE           = re.compile(r"duo[- ]?security|two.factor|2fa|mfa", re.IGNORECASE)


# ── Public entry point ────────────────────────────────────────────────────────

def login_and_scrape(netid: str, password: str) -> dict:
    """
    Full pipeline: CAS login → degree audit scrape → structured parse.

    Args:
        netid:    BYU Net ID (e.g. "jsmith123")
        password: BYU password — used only for the CAS POST, never stored.

    Returns a dict:
        {
            "success":           bool,
            "error":             str | None,
            "ge_completed":      set of category names,
            "ge_remaining":      set of category names,
            "ge_partial":        dict {cat: {"taken": [...], "needed": int}},
            "completed_courses": set of course codes,
            "in_progress_courses": set of course codes,
            "raw_requirements":  dict {cat: {"status", "raw_text", ...}},
            "debug": {
                "steps":         list of str,
                "warnings":      list of str,
                "page_texts":    dict {url: text},
                "all_courses_found": list,
                "cas_redirect":  str,
                "final_url":     str,
                "pages_scraped": int,
                "duo_detected":  bool,
            }
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

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        session, login_ok = _cas_login(session, netid, password, debug)
        if not login_ok:
            result["error"] = debug["warnings"][-1] if debug["warnings"] else "Login failed."
            return result

        pages = _scrape_mymap(session, debug)
        if not pages:
            result["error"] = "Logged in but could not find any degree audit content on MyMap."
            return result

        _parse_all_pages(pages, result, debug)
        result["success"] = True

    except Exception as exc:
        # Never include credential data in exception messages
        safe_msg = str(exc).replace(netid, "***")
        result["error"] = f"Unexpected error: {safe_msg}"
        debug["warnings"].append(result["error"])
    finally:
        session.close()
        # netid and password go out of scope here; GC will collect them

    return result


# ── CAS Authentication ────────────────────────────────────────────────────────

def _cas_login(
    session: requests.Session,
    netid: str,
    password: str,
    debug: dict,
) -> tuple:
    """
    Performs BYU CAS SSO login.
    Returns (session, success_bool).
    Credentials are used only in the POST body and never appear in logs.
    """
    # Step 1: GET MyMap → follow redirect to CAS login page
    debug["steps"].append("Step 1: GET mymap.byu.edu (follow redirect to CAS)")
    try:
        r1 = session.get(MYMAP_BASE, allow_redirects=True, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        debug["warnings"].append(f"Cannot reach mymap.byu.edu: {e}")
        return session, False

    debug["cas_redirect"] = r1.url
    debug["steps"].append(f"  → Landed on: {r1.url} [{r1.status_code}]")

    # Check for Duo 2FA on the redirect page
    if DUO_RE.search(r1.text):
        debug["duo_detected"] = True
        debug["warnings"].append(
            "Duo 2FA detected on the login page. "
            "Automated login cannot complete MFA. Use the PDF upload instead."
        )
        return session, False

    # Step 2: Parse the CAS login form
    soup = BeautifulSoup(r1.text, "lxml")
    form = soup.find("form", id="fm1") or soup.find("form")
    if not form:
        debug["warnings"].append(
            "Could not find a login form on the CAS page. "
            "BYU may have changed their login page structure."
        )
        debug["steps"].append(f"  CAS page HTML snippet:\n{r1.text[:1500]}")
        return session, False

    # Extract all hidden fields (lt, execution, _eventId, etc.)
    form_data = {}
    for inp in form.find_all("input"):
        name  = inp.get("name")
        value = inp.get("value", "")
        if name and name not in ("username", "password"):
            form_data[name] = value

    # Inject credentials — these are the ONLY two lines that touch the password
    form_data["username"] = netid
    form_data["password"] = password

    post_action = form.get("action") or r1.url
    if not post_action.startswith("http"):
        post_action = urljoin(r1.url, post_action)

    debug["steps"].append(f"Step 2: POST credentials to CAS ({post_action})")

    try:
        r2 = session.post(
            post_action,
            data=form_data,
            allow_redirects=True,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as e:
        debug["warnings"].append(f"CAS POST request failed: {e}")
        return session, False
    finally:
        # Overwrite credential fields in the dict before it can be GC'd
        form_data["username"] = ""
        form_data["password"] = ""

    debug["steps"].append(f"  → After CAS POST: {r2.url} [{r2.status_code}]")
    debug["final_url"] = r2.url

    # Check for Duo 2FA in the response
    if DUO_RE.search(r2.text):
        debug["duo_detected"] = True
        debug["warnings"].append(
            "Duo 2FA prompt detected. Automated login cannot complete MFA. "
            "Use the PDF/manual option instead."
        )
        return session, False

    # Check if still on CAS (login failed)
    parsed = urlparse(r2.url)
    if "cas.byu.edu" in parsed.netloc and "login" in parsed.path:
        soup2 = BeautifulSoup(r2.text, "lxml")
        err_el = (
            soup2.find(id="msg")
            or soup2.find(class_=re.compile(r"errors?|alert|invalid|warning", re.I))
        )
        err_text = err_el.get_text(strip=True) if err_el else "Unknown login error."
        debug["warnings"].append(f"CAS login rejected: {err_text}")
        return session, False

    debug["steps"].append("  → CAS login successful — session cookies established")
    return session, True


# ── MyMap Scraping ─────────────────────────────────────────────────────────────

def _scrape_mymap(session: requests.Session, debug: dict) -> dict:
    """
    Try common MyMap URLs to find degree audit content.
    Returns dict of {url: page_text} for every page that returned useful content.
    """
    candidate_paths = [
        "/",
        "/audit",
        "/degree-audit",
        "/plan",
        "/academicplan",
        "/student/ge",
        "/requirements",
    ]

    pages = {}
    for path in candidate_paths:
        url = MYMAP_BASE + path
        try:
            r = session.get(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            debug["steps"].append(f"GET {url} → {r.url} [{r.status_code}]")

            if r.status_code != 200 or len(r.text) < 500:
                continue

            soup = BeautifulSoup(r.text, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            pages[r.url] = {"html": r.text, "text": text}
            debug["page_texts"][r.url] = text
            debug["pages_scraped"] += 1
            debug["steps"].append(f"  → Captured {len(text)} chars of text")

            # Small delay to be polite
            time.sleep(0.3)

        except requests.RequestException as e:
            debug["steps"].append(f"  GET {url} failed: {e}")

    return pages


# ── Parsing ───────────────────────────────────────────────────────────────────

def _parse_all_pages(pages: dict, result: dict, debug: dict):
    """
    Aggregate text from all scraped pages and extract structured GE data.
    """
    all_text_parts = []
    all_html_parts = []

    for url, page in pages.items():
        all_text_parts.append(f"\n\n{'='*60}\nPAGE: {url}\n{'='*60}\n")
        all_text_parts.append(page["text"])
        all_html_parts.append(page["html"])

    combined_text = "\n".join(all_text_parts)
    combined_html = "\n".join(all_html_parts)

    # Extract all course codes across all pages
    all_courses = list(set(COURSE_CODE_RE.findall(combined_text)))
    debug["all_courses_found"] = sorted(all_courses)
    debug["steps"].append(f"Found {len(all_courses)} unique course codes across all pages")

    # Try structured HTML parse first (more accurate)
    _parse_html_structure(combined_html, result, debug)

    # Then fill gaps with line-by-line text scan
    _parse_text_lines(combined_text, result, debug)

    debug["steps"].append(
        f"GE parse complete: {len(result['ge_completed'])} completed, "
        f"{len(result['ge_remaining'])} remaining, "
        f"{len(result['raw_requirements'])} categories found total"
    )


def _parse_html_structure(html: str, result: dict, debug: dict):
    """
    Try to extract GE requirement blocks from the HTML DOM structure.
    BYU MyMap / Ellucian Degree Works uses various class names — we try several.
    """
    soup = BeautifulSoup(html, "lxml")

    # Common Degree Works / BYU MyMap selectors (try all)
    selectors = [
        ".req-block",
        ".audit-block",
        ".requirement-block",
        ".ge-block",
        "[class*='requirement']",
        "[class*='audit']",
        "[data-type='requirement']",
        "section",
        "article",
        ".card",
        ".panel",
    ]

    found_blocks = []
    for sel in selectors:
        blocks = soup.select(sel)
        if blocks:
            debug["steps"].append(f"  HTML selector '{sel}' found {len(blocks)} blocks")
            found_blocks.extend(blocks)
            if len(found_blocks) > 5:
                break  # Stop when we have enough structure

    for block in found_blocks:
        block_text = block.get_text(separator=" ", strip=True)
        block_lower = block_text.lower()

        for cat, keywords in GE_KEYWORDS.items():
            if cat in result["raw_requirements"]:
                continue  # Already found this category

            for kw in keywords:
                if kw in block_lower:
                    status = _detect_status(block_text)
                    result["raw_requirements"][cat] = {
                        "status":         status,
                        "raw_text":       block_text[:500],
                        "matched_keyword": kw,
                        "source":         "html_structure",
                    }
                    _apply_status(cat, status, result)
                    debug["steps"].append(f"  [HTML] Found '{cat}' → {status}")
                    break


def _parse_text_lines(text: str, result: dict, debug: dict):
    """
    Line-by-line scan of all page text to detect GE categories and status.
    Used as a fallback / gap-filler after HTML structural parsing.
    Also extracts completed and in-progress course codes.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for i, line in enumerate(lines):
        line_lower = line.lower()

        # ── Course extraction ────────────────────────────────────────────────
        if COMPLETION_RE.search(line):
            for m in COURSE_CODE_RE.findall(line):
                result["completed_courses"].add(re.sub(r"\s+", " ", m).strip())

        if IN_PROGRESS_RE.search(line):
            for m in COURSE_CODE_RE.findall(line):
                result["in_progress_courses"].add(re.sub(r"\s+", " ", m).strip())

        # ── GE category detection ────────────────────────────────────────────
        for cat, keywords in GE_KEYWORDS.items():
            if cat in result["raw_requirements"]:
                continue  # Already captured via HTML structure

            for kw in keywords:
                if kw not in line_lower:
                    continue

                # Window of surrounding lines for context
                window_lines = lines[max(0, i - 3): min(len(lines), i + 8)]
                window       = "\n".join(window_lines)

                status = _detect_status(window)
                result["raw_requirements"][cat] = {
                    "status":          status,
                    "raw_text":        window[:600],
                    "matched_keyword": kw,
                    "source":          "text_scan",
                }
                _apply_status(cat, status, result)
                debug["steps"].append(f"  [text] Found '{cat}' → {status} (keyword: '{kw}')")
                break


def _detect_status(text: str) -> str:
    """
    Given a block of text about a requirement, return its completion status.
    """
    if COMPLETION_RE.search(text):
        return "completed"
    if IN_PROGRESS_RE.search(text):
        return "in_progress"
    if NOT_DONE_RE.search(text):
        return "remaining"
    return "unknown"


def _apply_status(cat: str, status: str, result: dict):
    """Update the ge_completed / ge_remaining sets based on detected status."""
    if status == "completed":
        result["ge_completed"].add(cat)
        result["ge_remaining"].discard(cat)
    elif status in ("in_progress", "remaining", "unknown"):
        if cat not in result["ge_completed"]:
            result["ge_remaining"].add(cat)


# ── Debug Formatter ──────────────────────────────────────────────────────────

def format_debug_report(result: dict) -> str:
    """
    Produces a full human-readable debug report from the scrape result.
    This is what gets shown in the Streamlit expander so the user can
    verify accuracy before running the optimizer.
    """
    d = result["debug"]
    lines = []

    lines.append("=" * 70)
    lines.append("MYMAP SCRAPE DEBUG REPORT")
    lines.append("=" * 70)

    lines.append("\n── Login & Navigation Steps ──────────────────────────────────────")
    for step in d["steps"]:
        lines.append(f"  {step}")

    if d["warnings"]:
        lines.append("\n── Warnings ──────────────────────────────────────────────────────")
        for w in d["warnings"]:
            lines.append(f"  ⚠️  {w}")

    lines.append(f"\n── Pages Scraped: {d['pages_scraped']} ───────────────────────────────────")

    lines.append("\n── GE Categories Detected ────────────────────────────────────────")
    for cat, info in result["raw_requirements"].items():
        status_icon = {"completed": "✅", "in_progress": "🔄", "remaining": "❌", "unknown": "❓"}.get(
            info["status"], "❓"
        )
        lines.append(f"  {status_icon} {cat}")
        lines.append(f"     Status:  {info['status']}")
        lines.append(f"     Keyword: '{info['matched_keyword']}'  Source: {info['source']}")
        lines.append(f"     Context:")
        for ctx_line in info["raw_text"].split("\n")[:6]:
            lines.append(f"       | {ctx_line}")
        lines.append("")

    lines.append("\n── All Course Codes Found on Pages ───────────────────────────────")
    courses = d["all_courses_found"]
    if courses:
        # Print 6 per row
        for i in range(0, len(courses), 6):
            lines.append("  " + "  ".join(f"{c:<12}" for c in courses[i : i + 6]))
    else:
        lines.append("  (none found)")

    lines.append("\n── Completed Courses (near completion signal) ─────────────────────")
    done = sorted(result["completed_courses"])
    if done:
        for i in range(0, len(done), 6):
            lines.append("  " + "  ".join(f"{c:<12}" for c in done[i : i + 6]))
    else:
        lines.append("  (none detected)")

    lines.append("\n── In-Progress Courses ───────────────────────────────────────────")
    prog = sorted(result["in_progress_courses"])
    if prog:
        for i in range(0, len(prog), 6):
            lines.append("  " + "  ".join(f"{c:<12}" for c in prog[i : i + 6]))
    else:
        lines.append("  (none detected)")

    lines.append("\n── Raw Page Text (for manual verification) ──────────────────────")
    for url, text in d["page_texts"].items():
        lines.append(f"\n  [ {url} ]")
        lines.append("-" * 60)
        lines.append(text[:4000])
        if len(text) > 4000:
            lines.append(f"  ... ({len(text) - 4000} more characters truncated)")

    lines.append("\n" + "=" * 70)
    lines.append("END OF DEBUG REPORT")
    lines.append("=" * 70)

    return "\n".join(lines)
