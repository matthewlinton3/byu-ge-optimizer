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


def _parse_time_to_decimal(t: str) -> float | None:
    """
    Parse a time string (e.g. '8:00 AM', '2:30 PM', '14:30') to decimal hours 0-24.
    Returns None if unparseable.
    """
    if not t or not isinstance(t, str):
        return None
    t = t.strip().upper()
    # 24h format e.g. "14:30" or "14:30:00"
    m = re.match(r"^(\d{1,2}):(\d{2})(?::\d{2})?$", t)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return h + mi / 60.0
    # 12h format e.g. "8:00 AM", "2:30 PM"
    m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)?$", t)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        ampm = (m.group(3) or "").strip()
        if ampm == "PM" and h != 12:
            h += 12
        elif ampm == "AM" and h == 12:
            h = 0
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return h + mi / 60.0
    return None


def _parse_days_to_set(days: str) -> set[int]:
    """
    Parse day string (e.g. 'MWF', 'TTh', 'M W F') to set of weekday indices 0=Mon .. 4=Fri.
    """
    if not days or not isinstance(days, str):
        return set()
    s = days.strip().upper().replace(" ", "")
    # Map single letters and Th
    mapping = {"M": 0, "T": 1, "W": 2, "TH": 3, "F": 4}
    result = set()
    i = 0
    while i < len(s):
        if i + 1 < len(s) and s[i : i + 2] == "TH":
            result.add(3)
            i += 2
        elif s[i] in mapping:
            result.add(mapping[s[i]])
            i += 1
        else:
            i += 1
    return result


def get_course_sections(dept: str, catalog_number: str) -> tuple[list[dict], str]:
    """
    Fetch all current sections for a course.

    Parameters
    ----------
    dept           : BYU department code, e.g. "PSYCH", "ECON", "REL A"
    catalog_number : 3-digit catalog number, e.g. "111", "110"

    Returns (sections, course_title) where sections is a list of dicts with keys:
        section_number, instructor_name, section_type, credit_hours, mode,
        days (e.g. MWF, TTh), start_time, end_time (decimal hours 0-24),
        start_time_display, end_time_display (original strings), room
    and course_title is the authoritative title from the BYU schedule (may be "").
    Sections without meeting times (TBA) have days=set(), start/end=None; all sections included.
    """
    yearterm, session_id = _fetch_init_data()

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

    sections: list[dict] = []
    course_title: str = ""
    if isinstance(data, dict):
        for _key, course in data.items():
            if not course_title:
                course_title = (
                    course.get("title_long")
                    or course.get("title")
                    or course.get("full_title")
                    or ""
                ).strip()
            for sec in course.get("sections", []):
                name = (sec.get("instructor_name") or sec.get("instructor") or "").strip() or "TBA"
                days_raw = (
                    sec.get("days")
                    or sec.get("meeting_days")
                    or sec.get("day")
                    or sec.get("days_taught")
                    or ""
                )
                start_raw = (
                    sec.get("start_time")
                    or sec.get("start")
                    or sec.get("begin_time")
                    or sec.get("begin")
                    or ""
                )
                end_raw = (
                    sec.get("end_time")
                    or sec.get("end")
                    or sec.get("stop_time")
                    or sec.get("stop")
                    or ""
                )
                room = (
                    sec.get("room")
                    or sec.get("location")
                    or sec.get("building_room")
                    or sec.get("building")
                    or ""
                )
                if isinstance(room, dict):
                    room = (room.get("room") or room.get("building") or "").strip()
                if not isinstance(room, str):
                    room = str(room) if room else ""

                start_decimal = _parse_time_to_decimal(str(start_raw)) if start_raw else None
                end_decimal = _parse_time_to_decimal(str(end_raw)) if end_raw else None
                days_set = _parse_days_to_set(str(days_raw)) if days_raw else set()

                sections.append({
                    "section_number": sec.get("section_number", ""),
                    "instructor_name": name,
                    "section_type":   sec.get("section_type", ""),
                    "credit_hours":   sec.get("credit_hours", ""),
                    "mode":           sec.get("mode", ""),
                    "days":           days_raw if isinstance(days_raw, str) else str(days_raw or ""),
                    "days_set":       days_set,
                    "start_time":    start_decimal,
                    "end_time":       end_decimal,
                    "start_time_display": str(start_raw).strip() if start_raw else "",
                    "end_time_display": str(end_raw).strip() if end_raw else "",
                    "room":           room.strip() if isinstance(room, str) else room,
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
        name = sec.get("instructor_name", "")
        if name and str(name).upper() not in ("TBA", "STAFF", ""):
            seen[name] = True
    return list(seen.keys()), total_sections, course_title


def attach_sections_to_courses(courses: list[dict]) -> list[dict]:
    """
    For each course dict (with course_code), fetch section details including
    days, start_time, end_time, room and set course['sections'].
    Modifies each course in place and returns the same list.
    """
    for course in courses:
        code = course.get("course_code", "")
        dept, num = parse_course_code(code)
        if not dept or not num:
            course["sections"] = []
            continue
        sections, title = get_course_sections(dept, num)
        course["sections"] = sections
        if title:
            course["course_name"] = title
        time.sleep(0.15)
    return courses


def parse_course_code(course_code: str) -> tuple[str, str]:
    """
    Split a BYU course code like "PSYCH 111" or "REL A 121" into (dept, number).
    Returns ("", "") if it can't be parsed.
    """
    m = re.match(r"^([A-Z]+(?:\s+[A-Z])?)\s+(\d{3}[A-Z]?)$", course_code.strip())
    if m:
        return m.group(1), m.group(2)
    return "", ""
