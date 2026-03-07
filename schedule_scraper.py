"""
BYU Class Schedule Scraper
===========================
Fetches current-semester sections for a course from the BYU public class
schedule at commtech.byu.edu/noauth/classSchedule.

Endpoint discovered by inspecting js/search.js on the page:
  POST ajax/getClasses.php  — returns all sections for a dept/number
  POST ajax/getSections.php — returns detailed section data (requires curriculum ID)

Usage:
    from schedule_scraper import get_instructors_for_course, get_section_count
"""

import re
import time
import requests

BASE_URL = "https://commtech.byu.edu/noauth/classSchedule"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Referer": BASE_URL + "/index.php",
    "Origin": BASE_URL,
}

_yearterm_cache: str | None = None
_session_id_cache: str | None = None


def _fetch_init_data() -> tuple[str, str]:
    """Fetch the current yearterm and a fresh session ID from the index page."""
    global _yearterm_cache, _session_id_cache
    if _yearterm_cache and _session_id_cache:
        return _yearterm_cache, _session_id_cache

    try:
        resp = requests.get(BASE_URL + "/index.php", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        yt_match = re.search(r'_init_yearterm\s*=\s*"(\d+)"', html)
        sid_match = re.search(r'_session_id\s*=\s*"([A-Z0-9]+)"', html)

        yearterm  = yt_match.group(1)  if yt_match  else "20263"
        session_id = sid_match.group(1) if sid_match else ""

        _yearterm_cache  = yearterm
        _session_id_cache = session_id
        return yearterm, session_id
    except Exception:
        return "20263", ""


def get_course_sections(dept: str, catalog_number: str) -> tuple[list[dict], str]:
    """
    Fetch all current sections for a course.

    Parameters
    ----------
    dept           : BYU department code, e.g. "PSYCH", "ECON", "REL A"
    catalog_number : 3-digit catalog number, e.g. "111", "110"

    Returns (sections, course_title) where sections is a list of dicts with keys:
        section_number, instructor_name, section_type, credit_hours, mode
    and course_title is the authoritative title from the BYU schedule (may be "").
    """
    yearterm, session_id = _fetch_init_data()

    # Build form-encoded data matching jQuery's nested object serialization
    post_data = {
        "sessionId": session_id,
        "searchObject[yearterm]":  yearterm,
        "searchObject[dept_name_or_keyword][dept]":    dept.upper(),
        "searchObject[dept_name_or_keyword][keyword]": dept.upper(),
        "searchObject[catalog_number]": catalog_number,
    }

    try:
        resp = requests.post(
            BASE_URL + "/ajax/getClasses.php",
            data=post_data,
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return [], ""

    # data is a dict keyed by "curriculumId-titleCode"
    sections: list[dict] = []
    course_title: str = ""
    if isinstance(data, dict):
        for _key, course in data.items():
            # Capture course title from the top-level course object
            if not course_title:
                course_title = (
                    course.get("title_long")
                    or course.get("title")
                    or course.get("full_title")
                    or ""
                ).strip()
            for sec in course.get("sections", []):
                name = (sec.get("instructor_name") or "").strip()
                if name:
                    sections.append({
                        "section_number": sec.get("section_number", ""),
                        "instructor_name": name,
                        "section_type":   sec.get("section_type", ""),
                        "credit_hours":   sec.get("credit_hours", ""),
                        "mode":           sec.get("mode", ""),
                    })

    return sections, course_title


def get_instructors_for_course(dept: str, catalog_number: str) -> tuple[list[str], int, str]:
    """
    Return (unique_instructor_names, total_section_count, course_title) for a course.

    Names are in the form returned by BYU, e.g. "Sandra Sephton".
    section_count includes ALL sections (even TBA / no instructor listed).
    course_title is the authoritative title from the BYU class schedule.
    """
    sections, course_title = get_course_sections(dept, catalog_number)
    total_sections = len(sections)
    seen: dict[str, bool] = {}
    for sec in sections:
        name = sec["instructor_name"]
        if name and name.upper() not in ("TBA", "STAFF", ""):
            seen[name] = True
    return list(seen.keys()), total_sections, course_title


def parse_course_code(course_code: str) -> tuple[str, str]:
    """
    Split a BYU course code like "PSYCH 111" or "REL A 121" into (dept, number).
    Returns ("", "") if it can't be parsed.
    """
    m = re.match(r"^([A-Z]+(?:\s+[A-Z])?)\s+(\d{3}[A-Z]?)$", course_code.strip())
    if m:
        return m.group(1), m.group(2)
    return "", ""
