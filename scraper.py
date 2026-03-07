"""
BYU GE Course Scraper
Scrapes BYU catalog for GE courses and caches results in SQLite.
"""

import requests
import sqlite3
import json
import time
import re
from bs4 import BeautifulSoup

DB_PATH = "ge_courses.db"

GE_CATEGORIES = {
    "American Heritage": {"credits_needed": 3, "courses_needed": 1},
    "Religion": {"credits_needed": 14, "courses_needed": 1},
    "First-Year Writing": {"credits_needed": 3, "courses_needed": 1},
    "Advanced Written and Oral Communication": {"credits_needed": 3, "courses_needed": 1},
    "Languages of Learning (Quantitative)": {"credits_needed": 3, "courses_needed": 1},
    "Arts": {"credits_needed": 3, "courses_needed": 1},
    "Letters": {"credits_needed": 3, "courses_needed": 1},
    "Scientific Principles and Reasoning (Life Sciences)": {"credits_needed": 3, "courses_needed": 1},
    "Scientific Principles and Reasoning (Physical Sciences)": {"credits_needed": 3, "courses_needed": 1},
    "Social and Behavioral Sciences": {"credits_needed": 3, "courses_needed": 1},
    "American Civilization": {"credits_needed": 3, "courses_needed": 1},
    "Global and Cultural Awareness": {"credits_needed": 3, "courses_needed": 1},
    "Comparative Civilization": {"credits_needed": 3, "courses_needed": 1},
}

GE_CATEGORY_SLUGS = {
    "American Heritage": "american-heritage",
    "Arts": "arts",
    "Letters": "letters",
    "Scientific Principles and Reasoning (Life Sciences)": "life-sciences",
    "Scientific Principles and Reasoning (Physical Sciences)": "physical-sciences",
    "Social and Behavioral Sciences": "social-behavioral-sciences",
    "American Civilization": "american-civilization",
    "Global and Cultural Awareness": "global-cultural-awareness",
    "Comparative Civilization": "comparative-civilization",
    "First-Year Writing": "first-year-writing",
    "Advanced Written and Oral Communication": "advanced-written-oral-communication",
    "Languages of Learning (Quantitative)": "languages-of-learning",
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE,
            course_name TEXT,
            credit_hours INTEGER,
            ge_categories TEXT,
            description TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS professors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT,
            professor_name TEXT,
            rmp_rating REAL,
            rmp_difficulty REAL,
            rmp_would_take_again REAL,
            rmp_id TEXT
        )
    """)
    conn.commit()
    conn.close()

def db_has_courses():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM courses")
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def save_course(course_code, course_name, credit_hours, ge_categories, description=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO courses (course_code, course_name, credit_hours, ge_categories, description)
        VALUES (?, ?, ?, ?, ?)
    """, (course_code, course_name, credit_hours, json.dumps(ge_categories), description))
    conn.commit()
    conn.close()

def get_all_courses():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT course_code, course_name, credit_hours, ge_categories FROM courses")
    rows = c.fetchall()
    conn.close()
    courses = []
    for row in rows:
        courses.append({
            "course_code": row[0],
            "course_name": row[1],
            "credit_hours": row[2],
            "ge_categories": json.loads(row[3]),
        })
    return courses

def scrape_catalog_for_ge(refresh=False):
    """Scrape BYU catalog for GE courses by category."""
    init_db()

    if db_has_courses() and not refresh:
        print("[cache] Using cached course data. Pass --refresh to re-scrape.")
        return get_all_courses()

    print("[scraper] Scraping BYU catalog for GE courses...")
    all_courses = {}

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    session = requests.Session()
    session.headers.update(headers)

    for category, slug in GE_CATEGORY_SLUGS.items():
        url = f"https://catalog.byu.edu/search?attribute={slug}&type=ge"
        fallback_url = f"https://catalog.byu.edu/courses?ge={slug}"

        print(f"  → Fetching: {category}")
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                resp = session.get(fallback_url, timeout=15)

            soup = BeautifulSoup(resp.text, "lxml")

            # Try multiple selectors for course blocks
            course_blocks = (
                soup.select(".course-block") or
                soup.select(".views-row") or
                soup.select("article.course") or
                soup.select("[class*='course']")
            )

            found = 0
            for block in course_blocks:
                code_el = (
                    block.select_one(".course-code") or
                    block.select_one(".field--name-field-course-id") or
                    block.select_one("h3") or
                    block.select_one(".title")
                )
                name_el = (
                    block.select_one(".course-name") or
                    block.select_one(".field--name-title") or
                    block.select_one("h4")
                )
                credit_el = (
                    block.select_one(".credit-hours") or
                    block.select_one(".field--name-field-credit-hours")
                )

                if not code_el:
                    continue

                raw_code = code_el.get_text(strip=True)
                course_match = re.search(r"([A-Z]+\s*\d+[A-Z]?)", raw_code)
                if not course_match:
                    continue

                course_code = course_match.group(1).replace(" ", " ").strip()
                course_name = name_el.get_text(strip=True) if name_el else "Unknown"

                credits_text = credit_el.get_text(strip=True) if credit_el else "3"
                credits_match = re.search(r"(\d+)", credits_text)
                credit_hours = int(credits_match.group(1)) if credits_match else 3

                if course_code not in all_courses:
                    all_courses[course_code] = {
                        "course_code": course_code,
                        "course_name": course_name,
                        "credit_hours": credit_hours,
                        "ge_categories": [],
                    }

                if category not in all_courses[course_code]["ge_categories"]:
                    all_courses[course_code]["ge_categories"].append(category)

                found += 1

            print(f"     Found {found} courses for {category}")
            time.sleep(0.5)

        except Exception as e:
            print(f"     [warn] Failed to scrape {category}: {e}")
            continue

    # If scraping returned very little, use fallback seed data
    if len(all_courses) < 10:
        print("\n[warn] Live scrape returned limited results. Using BYU seed data as fallback...")
        all_courses = get_seed_courses()

    # Save to DB
    for code, course in all_courses.items():
        save_course(
            course["course_code"],
            course["course_name"],
            course["credit_hours"],
            course["ge_categories"],
        )

    print(f"\n[scraper] Saved {len(all_courses)} courses to database.")
    return list(all_courses.values())


def get_seed_courses():
    """
    Fallback seed data of well-known BYU GE courses.
    This is used when the live scraper can't access the catalog.
    """
    seed = [
        ("AMER H 100", "American Heritage", 3, ["American Heritage", "American Civilization"]),
        ("AMER H 200", "Development of Western Civilization", 3, ["American Heritage"]),
        ("REL A 121", "The Book of Mormon", 2, ["Religion"]),
        ("REL A 122", "The Book of Mormon", 2, ["Religion"]),
        ("REL A 211", "Doctrine and Covenants", 2, ["Religion"]),
        ("REL A 212", "Church History and Doctrine", 2, ["Religion"]),
        ("REL C 225", "Eternal Family", 2, ["Religion"]),
        ("REL A 250", "Jesus Christ and the Everlasting Gospel", 2, ["Religion"]),
        ("WRTG 150", "Writing and Rhetoric", 3, ["First-Year Writing"]),
        ("WRTG 316", "Technical Writing", 3, ["Advanced Written and Oral Communication"]),
        ("WRTG 320", "Business Writing", 3, ["Advanced Written and Oral Communication"]),
        ("COMM 101", "Principles of Public Speaking", 3, ["Advanced Written and Oral Communication"]),
        ("MATH 110", "College Algebra", 3, ["Languages of Learning (Quantitative)"]),
        ("MATH 112", "Calculus 1", 4, ["Languages of Learning (Quantitative)"]),
        ("STAT 121", "Principles of Statistics", 3, ["Languages of Learning (Quantitative)"]),
        ("ART 100", "Foundations of Visual Arts", 3, ["Arts"]),
        ("MUSIC 101", "Introduction to Music", 3, ["Arts"]),
        ("THEATRE 101", "Introduction to Theatre", 3, ["Arts"]),
        ("ART 201", "Art History Survey 1", 3, ["Arts", "Comparative Civilization"]),
        ("ENGL 251", "Introduction to Literature", 3, ["Letters"]),
        ("ENGL 292", "Introduction to Literary Theory", 3, ["Letters"]),
        ("PHIL 201", "Introduction to Philosophy", 3, ["Letters"]),
        ("HIST 201", "World History to 1500", 3, ["Letters", "Global and Cultural Awareness"]),
        ("BIO 100", "Principles of Biology", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("BIO 130", "Human Biology", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("PDBIO 120", "Human Biology", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("CHEM 101", "Fundamentals of Chemistry", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("PHSCS 100", "Descriptive Astronomy", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("GEOL 101", "Principles of Geology", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("PSYCH 111", "Introduction to Psychology", 3, ["Social and Behavioral Sciences"]),
        ("SOC 111", "Introduction to Sociology", 3, ["Social and Behavioral Sciences"]),
        ("ECON 110", "Economic Principles and Problems", 3, ["Social and Behavioral Sciences", "American Heritage"]),
        ("POLI 110", "Introduction to American Government", 3, ["Social and Behavioral Sciences", "American Civilization"]),
        ("HIST 220", "US History to 1877", 3, ["American Civilization"]),
        ("HIST 221", "US History from 1877", 3, ["American Civilization"]),
        ("GEOG 101", "World Regional Geography", 3, ["Global and Cultural Awareness"]),
        ("ANTHR 101", "Introduction to Anthropology", 3, ["Global and Cultural Awareness", "Social and Behavioral Sciences"]),
        ("MFHD 210", "Foundations of Family Life", 3, ["Social and Behavioral Sciences"]),
        ("HIST 202", "World History 1500-Present", 3, ["Comparative Civilization", "Global and Cultural Awareness"]),
        ("PHIL 202", "World Religions", 3, ["Comparative Civilization", "Global and Cultural Awareness"]),
        ("ASIAN 101", "Introduction to Asian Civilizations", 3, ["Comparative Civilization", "Global and Cultural Awareness"]),
        ("LATIN 101", "Latin American Civilizations", 3, ["Comparative Civilization", "Global and Cultural Awareness"]),
        ("ENGL 340", "Survey of World Literature", 3, ["Letters", "Global and Cultural Awareness"]),
    ]

    result = {}
    for code, name, credits, categories in seed:
        result[code] = {
            "course_code": code,
            "course_name": name,
            "credit_hours": credits,
            "ge_categories": categories,
        }
    return result
