"""
RateMyProfessors Integration
Uses the RMP GraphQL API to fetch professor ratings for BYU courses.

Search strategy
---------------
1. Query the BYU class schedule (schedule_scraper) for the actual professors
   currently teaching the course this semester.
2. For each professor name, search the RMP BYU professor list by name.
   - Exact match first (case-insensitive full name)
   - Fuzzy match via rapidfuzz WRatio if no exact hit (threshold: 82)
     This bridges "Joe Smith" (BYU schedule) ↔ "Joseph Smith" (RMP).
3. If the schedule scraper returns no names (course not offered this term),
   fall back to the department-based search used previously.

Fuzzy matching is always active: rapidfuzz is a required dependency.
"""

import requests
import sqlite3
import time
import re

try:
    from rapidfuzz import fuzz, process as rfprocess
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

from schedule_scraper import get_instructors_for_course, parse_course_code

DB_PATH = "ge_courses.db"
BYU_SCHOOL_ID = "U2Nob29sLTEzNQ=="  # BYU's RMP school ID (base64 encoded)

RMP_GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"

RMP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Basic dGVzdDp0ZXN0",  # RMP's public auth token
    "Origin": "https://www.ratemyprofessors.com",
    "Referer": "https://www.ratemyprofessors.com/",
}

# Paginated teacher search — empty text returns all BYU professors in rating order
_PAGED_QUERY = """
query TeacherSearchQuery($text: String!, $schoolID: ID!, $cursor: String) {
  newSearch {
    teachers(query: { text: $text, schoolID: $schoolID }, first: 20, after: $cursor) {
      edges {
        cursor
        node {
          id
          firstName
          lastName
          avgRating
          avgDifficulty
          wouldTakeAgainPercent
          numRatings
          department
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""

# ── Dept-code → RMP department name mapping ───────────────────────────────────
DEPT_CODE_TO_RMP: dict[str, list[str]] = {
    "PSYCH":   ["Psychology"],
    "ECON":    ["Economics"],
    "HIST":    ["History"],
    "BIO":     ["Biology", "Life Sciences", "Molecular Biosciences"],
    "BIOL":    ["Biology", "Life Sciences"],
    "CHEM":    ["Chemistry"],
    "PHSCS":   ["Physics", "Physical Sciences"],
    "MATH":    ["Mathematics", "Mathematics Education"],
    "STAT":    ["Statistics"],
    "CS":      ["Computer Science"],
    "REL":     ["Religion", "Ancient Scripture", "Religious Studies"],
    "PHIL":    ["Philosophy", "Humanities"],
    "SOC":     ["Sociology", "Social Science"],
    "ANTHR":   ["Anthropology"],
    "POLI":    ["Political Science"],
    "COMM":    ["Communication"],
    "ENG":     ["English"],
    "ENGL":    ["English"],
    "AMER":    ["History", "Social Science"],
    "AMST":    ["Humanities"],
    "GEOG":    ["Geography"],
    "GEO":     ["Geology"],
    "GEOL":    ["Geology"],
    "ART":     ["Art", "Fine Arts"],
    "MUSIC":   ["Music"],
    "DANCE":   ["Dance"],
    "THEATRE": ["Theatre & Media Arts"],
    "HUMA":    ["Humanities"],
    "FHSS":    ["Social Science"],
    "MFHD":    ["Family Life", "Family Studies"],
    "NDFS":    ["Nutrition & Food Science"],
    "PH":      ["Health Science"],
    "EXSC":    ["Exercise & Sport Science", "Physical Education"],
    "NURS":    ["Health Science"],
    "WRTG":    ["Writing"],
    "ESL":     ["Writing"],
    "SPAN":    ["Spanish", "Spanish & Portuguese"],
    "LING":    ["Linguistics"],
    "INTL":    ["International Studies"],
    "MKT":     ["Business"],
    "MGMT":    ["Management", "Business"],
    "FIN":     ["Finance"],
    "ACC":     ["Accounting"],
    "IS":      ["Information Systems"],
    "STDEV":   ["Student Life", "Student Services"],
    "ME":      ["Mechanical Engineering"],
    "CE":      ["Civil Engineering"],
    "ITM":     ["Construction", "Construction Management"],
}

# Fuzzy match threshold (0–100). 82 catches "Joe"↔"Joseph", "Mike"↔"Michael"
# while avoiding false positives between different people.
FUZZY_THRESHOLD = 82


def _fetch_all_byu_professors(max_pages: int = 20) -> list[dict]:
    """
    Paginate through BYU professors on RMP (empty-text search).
    Returns up to max_pages * 20 professor dicts, each with:
      name, rating, difficulty, would_take_again, num_ratings, department, rmp_id
    """
    professors = []
    cursor = None

    for _ in range(max_pages):
        try:
            payload = {
                "query": _PAGED_QUERY,
                "variables": {
                    "text": "",
                    "schoolID": BYU_SCHOOL_ID,
                    "cursor": cursor,
                },
            }
            resp = requests.post(
                RMP_GRAPHQL_URL, headers=RMP_HEADERS, json=payload, timeout=10
            )
            if resp.status_code != 200:
                break

            data = resp.json()
            teachers = (
                data.get("data", {})
                .get("newSearch", {})
                .get("teachers", {})
            )
            edges = teachers.get("edges", [])
            page_info = teachers.get("pageInfo", {})

            for edge in edges:
                node = edge.get("node", {})
                if node.get("numRatings", 0) == 0:
                    continue
                professors.append({
                    "name": f"{node.get('firstName','')} {node.get('lastName','')}".strip(),
                    "rating": node.get("avgRating", 0) or 0,
                    "difficulty": node.get("avgDifficulty", 0) or 0,
                    "would_take_again": node.get("wouldTakeAgainPercent", -1)
                    if node.get("wouldTakeAgainPercent") is not None
                    else -1,
                    "num_ratings": node.get("numRatings", 0),
                    "department": node.get("department", ""),
                    "rmp_id": node.get("id", ""),
                })

            if not page_info.get("hasNextPage") or not edges:
                break
            cursor = page_info.get("endCursor")
            time.sleep(0.2)

        except Exception:
            break

    return professors


def _match_by_name(schedule_name: str, all_profs: list[dict]) -> dict | None:
    """
    Find the best RMP professor record matching a schedule name.

    Strategy:
      1. Exact full-name match (case-insensitive)
      2. Fuzzy match via rapidfuzz WRatio (threshold FUZZY_THRESHOLD)
         — handles "Joe Smith" ↔ "Joseph Smith", nicknames, middle initials
      3. Return None if no match meets the threshold
    """
    name_lower = schedule_name.lower().strip()

    # ── 1. Exact match ────────────────────────────────────────────
    for prof in all_profs:
        if prof["name"].lower() == name_lower:
            return prof

    # ── 2. Fuzzy match ────────────────────────────────────────────
    if not HAS_RAPIDFUZZ or not all_profs:
        return None

    rmp_names = [p["name"] for p in all_profs]
    result = rfprocess.extractOne(
        schedule_name,
        rmp_names,
        scorer=fuzz.WRatio,
        score_cutoff=FUZZY_THRESHOLD,
    )
    if result is not None:
        matched_name = result[0]
        for prof in all_profs:
            if prof["name"] == matched_name:
                return prof

    return None


def _dept_fallback(course_code: str, all_profs: list[dict]) -> list[dict]:
    """
    Fall back to department-based filtering when the schedule scraper has no
    data for this course (not offered this term, or lookup failed).
    """
    dept_match = re.match(r"([A-Z]+)", course_code)
    dept_code = dept_match.group(1) if dept_match else ""
    target_depts = DEPT_CODE_TO_RMP.get(dept_code, [])
    if not target_depts:
        return []

    target_lower = [d.lower() for d in target_depts]
    matching = [
        p for p in all_profs
        if any(t in p["department"].lower() for t in target_lower)
    ]
    matching.sort(key=lambda p: -(p.get("rating") or 0))
    return matching


def save_professor(course_code: str, prof: dict) -> None:
    """Cache professor data in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        INSERT OR REPLACE INTO professors
        (course_code, professor_name, rmp_rating, rmp_difficulty, rmp_would_take_again, rmp_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            course_code,
            prof["name"],
            prof["rating"],
            prof["difficulty"],
            prof["would_take_again"],
            prof.get("rmp_id", ""),
        ),
    )
    conn.commit()
    conn.close()


def get_cached_professors(course_code: str) -> list[dict]:
    """Get cached professor data from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT professor_name, rmp_rating, rmp_difficulty, rmp_would_take_again
        FROM professors WHERE course_code = ?
        ORDER BY rmp_rating DESC
        """,
        (course_code,),
    )
    rows = c.fetchall()
    conn.close()

    return [
        {
            "name": r[0],
            "rating": r[1],
            "difficulty": r[2],
            "would_take_again": r[3],
        }
        for r in rows
    ]


def enrich_with_rmp(courses: list[dict], refresh: bool = False) -> list[dict]:
    """
    Add RMP data to each course dict in-place.

    For each course:
      1. Query BYU class schedule for current instructors (this semester).
      2. Match each instructor to an RMP record using exact → fuzzy name match.
      3. Store all matched professors sorted by rating descending.
      4. Fall back to department-based search if no schedule data available.

    Adds keys:
      professors         — list of matched RMP records, sorted by rating desc
      rmp_rating         — top professor's rating (0 if none)
      rmp_difficulty     — top professor's difficulty (0 if none)
      rmp_would_take_again — top professor's WTA % (-1 if none)
      section_count      — total sections offered this term (0 if unknown)

    Missing data uses numeric sentinels (0 / -1) so the optimizer can sort
    without type errors. Use fmt_* helpers for display.
    """
    print("\n[rmp] Looking up professor ratings...")

    # One paginated fetch covers all departments — reuse for the whole batch
    _prof_cache: list[dict] | None = None

    for i, course in enumerate(courses):
        code = course["course_code"]

        # ── 1. Check SQLite cache first ───────────────────────────
        if not refresh:
            cached = get_cached_professors(code)
            if cached:
                course["professors"]          = cached
                course["section_count"]       = course.get("section_count", 0)
                course["rmp_rating"]          = cached[0]["rating"] or 0
                course["rmp_difficulty"]      = cached[0]["difficulty"] or 0
                course["rmp_would_take_again"] = (
                    cached[0]["would_take_again"]
                    if (cached[0]["would_take_again"] or -1) >= 0
                    else -1
                )
                continue

        # ── 2. Fetch RMP professor list once, reuse ───────────────
        print(f"  → [{i+1}/{len(courses)}] {code}...")
        if _prof_cache is None:
            print("      (fetching BYU professor list from RMP...)")
            _prof_cache = _fetch_all_byu_professors(max_pages=20)

        # ── 3. Get current instructors from BYU schedule ──────────
        dept, num = parse_course_code(code)
        schedule_names: list[str] = []
        section_count: int = 0

        if dept and num:
            try:
                schedule_names, section_count, schedule_title = get_instructors_for_course(dept, num)
                if schedule_title:
                    course["course_name"] = schedule_title
                print(f"      schedule: {section_count} sections, "
                      f"instructors: {schedule_names or ['(none)']}, "
                      f"title: {schedule_title or '(none)'}")
            except Exception as exc:
                print(f"      schedule lookup failed: {exc}")

        course["section_count"] = section_count

        # ── 4. Name-based RMP lookup with fuzzy fallback ──────────
        professors: list[dict] = []

        if schedule_names:
            for sched_name in schedule_names:
                matched = _match_by_name(sched_name, _prof_cache)
                if matched:
                    # Attach the schedule name so display can show both
                    entry = dict(matched)
                    entry["schedule_name"] = sched_name
                    professors.append(entry)
                else:
                    # No RMP profile found — include with zeroed ratings
                    professors.append({
                        "name":           sched_name,
                        "schedule_name":  sched_name,
                        "rating":         0,
                        "difficulty":     0,
                        "would_take_again": -1,
                        "num_ratings":    0,
                        "department":     "",
                        "rmp_id":         "",
                    })
            professors.sort(key=lambda p: -(p.get("rating") or 0))
        else:
            # ── 5. Fallback: department-based search ───────────────
            professors = _dept_fallback(code, _prof_cache)

        # ── 6. Persist & attach ───────────────────────────────────
        for prof in professors:
            if prof.get("rating", 0) > 0:
                save_professor(code, prof)

        course["professors"]           = professors
        if professors and professors[0].get("rating", 0) > 0:
            course["rmp_rating"]           = professors[0]["rating"]
            course["rmp_difficulty"]       = professors[0]["difficulty"] or 0
            course["rmp_would_take_again"] = professors[0]["would_take_again"]
        else:
            course["rmp_rating"]           = 0
            course["rmp_difficulty"]       = 0
            course["rmp_would_take_again"] = -1

        time.sleep(0.1)

    return courses


# ── Display helpers ───────────────────────────────────────────────────────────

def fmt_rating(v) -> str:
    """Format RMP overall rating for display. Returns 'No ratings yet' for missing."""
    if v is None or v == 0:
        return "No ratings yet"
    return f"{v:.1f} / 5"


def fmt_difficulty(v) -> str:
    """Format RMP difficulty for display. Returns '—' for missing data."""
    if v is None or v == 0:
        return "—"
    return f"{v:.1f} / 5"


def fmt_wta(v) -> str:
    """Format 'would take again' percentage for display."""
    if v is None or v < 0:
        return "—"
    return f"{v:.0f}%"
