"""
RateMyProfessors Integration
Uses the RMP GraphQL API to fetch professor ratings for BYU courses.
"""

import requests
import sqlite3
import json
import time
import re

DB_PATH = "ge_courses.db"
BYU_SCHOOL_ID = "U2Nob29sLTEzNQ=="  # BYU's RMP school ID (base64 encoded)

RMP_GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"

RMP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Basic dGVzdDp0ZXN0",  # RMP's public auth token
    "Origin": "https://www.ratemyprofessors.com",
    "Referer": "https://www.ratemyprofessors.com/",
}

SEARCH_QUERY = """
query TeacherSearchQuery($text: String!, $schoolID: ID!) {
  newSearch {
    teachers(query: { text: $text, schoolID: $schoolID }) {
      edges {
        node {
          id
          firstName
          lastName
          avgRating
          avgDifficulty
          wouldTakeAgainPercent
          numRatings
          department
          teacherRatingTags {
            tagName
            tagCount
          }
        }
      }
    }
  }
}
"""

def search_professor(course_code, course_name):
    """Search RMP for professors teaching this course at BYU."""

    # Extract department from course code (e.g., "PSYCH 111" -> "PSYCH")
    dept_match = re.match(r"([A-Z]+)", course_code)
    search_term = dept_match.group(1) if dept_match else course_name.split()[0]

    try:
        payload = {
            "query": SEARCH_QUERY,
            "variables": {
                "text": search_term,
                "schoolID": BYU_SCHOOL_ID,
            }
        }

        resp = requests.post(RMP_GRAPHQL_URL, headers=RMP_HEADERS, json=payload, timeout=10)

        if resp.status_code != 200:
            return []

        data = resp.json()
        edges = data.get("data", {}).get("newSearch", {}).get("teachers", {}).get("edges", [])

        professors = []
        for edge in edges:
            node = edge.get("node", {})
            if node.get("numRatings", 0) == 0:
                continue

            professors.append({
                "name": f"{node.get('firstName', '')} {node.get('lastName', '')}".strip(),
                "rating": node.get("avgRating", 0),
                "difficulty": node.get("avgDifficulty", 0),
                "would_take_again": node.get("wouldTakeAgainPercent", -1),
                "num_ratings": node.get("numRatings", 0),
                "department": node.get("department", ""),
                "rmp_id": node.get("id", ""),
            })

        # Sort by rating descending
        professors.sort(key=lambda p: p["rating"], reverse=True)
        return professors

    except Exception as e:
        return []


def save_professor(course_code, prof):
    """Cache professor data in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO professors
        (course_code, professor_name, rmp_rating, rmp_difficulty, rmp_would_take_again, rmp_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        course_code,
        prof["name"],
        prof["rating"],
        prof["difficulty"],
        prof["would_take_again"],
        prof["rmp_id"],
    ))
    conn.commit()
    conn.close()


def get_cached_professors(course_code):
    """Get cached professor data from SQLite."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT professor_name, rmp_rating, rmp_difficulty, rmp_would_take_again
        FROM professors WHERE course_code = ?
        ORDER BY rmp_rating DESC
    """, (course_code,))
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


def enrich_with_rmp(courses, refresh=False):
    """Add RMP data to each course in the list."""
    print("\n[rmp] Looking up professor ratings...")

    for i, course in enumerate(courses):
        code = course["course_code"]

        # Check cache first
        if not refresh:
            cached = get_cached_professors(code)
            if cached:
                course["professors"] = cached
                course["rmp_rating"] = cached[0]["rating"] if cached else 0
                course["rmp_difficulty"] = cached[0]["difficulty"] if cached else 0
                course["rmp_would_take_again"] = cached[0]["would_take_again"] if cached else -1
                continue

        # Live lookup
        print(f"  → [{i+1}/{len(courses)}] {code}...")
        professors = search_professor(code, course["course_name"])

        if professors:
            for prof in professors:
                save_professor(code, prof)
            course["professors"] = professors
            course["rmp_rating"] = professors[0]["rating"]
            course["rmp_difficulty"] = professors[0]["difficulty"]
            course["rmp_would_take_again"] = professors[0]["would_take_again"]
        else:
            course["professors"] = []
            course["rmp_rating"] = 0
            course["rmp_difficulty"] = 0
            course["rmp_would_take_again"] = -1

        time.sleep(0.3)  # Be polite with rate limiting

    return courses
