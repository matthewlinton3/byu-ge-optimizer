"""
RateMyProfessors Integration
Uses the RMP GraphQL API to fetch professor ratings for BYU courses.

Search strategy
---------------
RMP's GraphQL `teachers` query filters by professor **name**, not department.
Searching "PSYCH" or "Psychology" returns nothing useful. Instead we do a
paginated empty-string search for BYU to retrieve all rated professors, then
filter client-side by matching the department name to the course's code prefix.
"""

import requests
import sqlite3
import time
import re

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
# BYU course code prefixes mapped to the department strings RMP uses.
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


def search_professor(course_code: str, course_name: str) -> list[dict]:
    """
    Find top-rated professors at BYU for the department matching course_code.

    Strategy:
      1. Extract the dept code from course_code (e.g. "PSYCH" from "PSYCH 111")
      2. Look up matching RMP department name(s) from DEPT_CODE_TO_RMP
      3. Paginate through all BYU professors and filter by department
      4. Return sorted by rating descending
    """
    dept_match = re.match(r"([A-Z]+)", course_code)
    dept_code = dept_match.group(1) if dept_match else ""

    # Determine which RMP dept names to match against
    target_depts: list[str] = DEPT_CODE_TO_RMP.get(dept_code, [])
    if not target_depts:
        # Fallback: try matching the dept code as a substring of RMP dept name
        # e.g. "ANTHR" → "Anthropology" won't match above but "ANTHR" is listed
        target_depts = []  # no data available for unknown depts

    try:
        all_profs = _fetch_all_byu_professors(max_pages=20)
    except Exception:
        return []

    # Filter by matching department
    if target_depts:
        target_lower = [d.lower() for d in target_depts]
        matching = [
            p for p in all_profs
            if any(t in p["department"].lower() for t in target_lower)
        ]
    else:
        matching = []

    # Sort by rating descending
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

    Adds keys: professors (list), rmp_rating, rmp_difficulty, rmp_would_take_again.
    Missing data is represented as 0 / -1 (numeric sentinels) so the optimizer
    can still sort without type errors.  Use fmt_* helpers for display.
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
                course["professors"] = cached
                course["rmp_rating"] = cached[0]["rating"] or 0
                course["rmp_difficulty"] = cached[0]["difficulty"] or 0
                course["rmp_would_take_again"] = (
                    cached[0]["would_take_again"]
                    if (cached[0]["would_take_again"] or -1) >= 0
                    else -1
                )
                continue

        # ── 2. Live lookup — fetch all BYU profs once, reuse ─────
        print(f"  → [{i+1}/{len(courses)}] {code}...")
        if _prof_cache is None:
            print("      (fetching BYU professor list from RMP...)")
            _prof_cache = _fetch_all_byu_professors(max_pages=20)

        # Filter pool to this course's department
        dept_match = re.match(r"([A-Z]+)", code)
        dept_code = dept_match.group(1) if dept_match else ""
        target_depts = DEPT_CODE_TO_RMP.get(dept_code, [])
        target_lower = [d.lower() for d in target_depts]

        if target_lower:
            professors = [
                p for p in _prof_cache
                if any(t in p["department"].lower() for t in target_lower)
            ]
            professors.sort(key=lambda p: -(p.get("rating") or 0))
        else:
            professors = []

        # ── 3. Persist & attach ───────────────────────────────────
        if professors:
            for prof in professors:
                save_professor(code, prof)
            course["professors"] = professors
            course["rmp_rating"] = professors[0]["rating"] or 0
            course["rmp_difficulty"] = professors[0]["difficulty"] or 0
            course["rmp_would_take_again"] = professors[0]["would_take_again"]
        else:
            course["professors"] = []
            course["rmp_rating"] = 0
            course["rmp_difficulty"] = 0
            course["rmp_would_take_again"] = -1

        time.sleep(0.1)  # gentle rate limiting between per-course saves

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
