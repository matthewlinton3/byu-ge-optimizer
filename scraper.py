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

def _try_scrape_url(session, url: str) -> str | None:
    """GET url and return response text if status 200 and body > 500 chars, else None."""
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200 and len(resp.text) > 500:
            return resp.text
    except Exception:
        pass
    return None


def _parse_courses_from_html(html: str, category: str, all_courses: dict) -> int:
    """
    Parse course blocks from HTML and merge into all_courses dict.
    Returns count of new courses found.
    """
    soup = BeautifulSoup(html, "lxml")

    # BYU catalog (catalog.byu.edu) uses various HTML structures depending on
    # whether the page is SSR or CSR. Try all known selectors.
    course_blocks = (
        soup.select(".course-block")
        or soup.select(".views-row")
        or soup.select("article.course")
        or soup.select("li.course")
        or soup.select("[class*='course-item']")
        or soup.select("[class*='course-row']")
        # Next.js / React catalog uses data-testid attributes
        or soup.select("[data-testid*='course']")
        # Generic fallback: any element containing a course-code pattern
        or [
            el for el in soup.select("div, li, tr")
            if re.search(r"\b[A-Z]{2,6}\s+\d{3}[A-Z]?\b", el.get_text())
            and len(el.get_text()) < 500  # skip huge containers
        ]
    )

    found = 0
    for block in course_blocks:
        block_text = block.get_text(separator=" ", strip=True)

        # Extract course code
        course_match = re.search(r"\b([A-Z]{2,6}(?:\s+[A-Z])?\s+\d{3}[A-Z]?)\b", block_text)
        if not course_match:
            continue
        course_code = re.sub(r"\s+", " ", course_match.group(1)).strip()

        # Extract name — look for heading elements first, then strip the code from full text
        name_el = (
            block.select_one("h3")
            or block.select_one("h4")
            or block.select_one(".course-name")
            or block.select_one(".field--name-title")
            or block.select_one("[class*='title']")
        )
        if name_el:
            course_name = name_el.get_text(strip=True)
        else:
            # Remove the course code from the block text to get a rough name
            course_name = block_text.replace(course_code, "").strip()[:80] or "Unknown"

        # Extract credit hours
        credit_el = (
            block.select_one(".credit-hours")
            or block.select_one("[class*='credit']")
            or block.select_one(".field--name-field-credit-hours")
        )
        credits_text = credit_el.get_text(strip=True) if credit_el else ""
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

    return found


def scrape_catalog_for_ge(refresh=False):
    """Scrape BYU catalog for GE courses by category."""
    init_db()

    if db_has_courses() and not refresh:
        print("[cache] Using cached course data. Pass --refresh to re-scrape.")
        return get_all_courses()

    print("[scraper] Scraping BYU catalog for GE courses...")
    all_courses = {}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    session = requests.Session()
    session.headers.update(headers)

    for category, slug in GE_CATEGORY_SLUGS.items():
        # Try multiple URL patterns — BYU has changed their catalog URLs over time
        candidate_urls = [
            f"https://catalog.byu.edu/search?attribute={slug}&type=ge",
            f"https://catalog.byu.edu/courses?ge={slug}",
            f"https://catalog.byu.edu/general-education/{slug}",
            f"https://catalog.byu.edu/ge/{slug}",
        ]

        print(f"  → Fetching: {category}")
        html = None
        for url in candidate_urls:
            html = _try_scrape_url(session, url)
            if html:
                break

        if not html:
            print(f"     [warn] All URLs failed for {category}")
            time.sleep(0.3)
            continue

        found = _parse_courses_from_html(html, category, all_courses)
        print(f"     Found {found} courses for {category}")
        time.sleep(0.5)

    # Merge with seed data to guarantee coverage even when live scrape misses courses.
    # Seed courses are only added if the live scrape didn't already include them.
    seed = get_seed_courses()
    for code, seed_course in seed.items():
        if code not in all_courses:
            all_courses[code] = seed_course
        else:
            # Merge categories: add any seed categories the scraper missed
            for cat in seed_course["ge_categories"]:
                if cat not in all_courses[code]["ge_categories"]:
                    all_courses[code]["ge_categories"].append(cat)

    if len(all_courses) < 10:
        print("\n[warn] Live scrape + seed still returned few results. Using seed only.")
        all_courses = seed

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
    Covers all 13 GE categories with multiple options each.
    Used when the live scraper can't access the catalog AND merged into
    live-scrape results to fill any gaps.
    Format: (course_code, course_name, credit_hours, [ge_categories])
    """
    seed = [
        # ── American Heritage ────────────────────────────────────────────────
        ("AMER H 100", "American Heritage", 3, ["American Heritage", "American Civilization"]),
        ("AMER H 200", "Development of Western Civilization", 3, ["American Heritage"]),
        ("ECON 110", "Economic Principles and Problems", 3, ["American Heritage", "Social and Behavioral Sciences"]),
        ("HONRS 240", "American Heritage Honors", 3, ["American Heritage"]),

        # ── American Civilization ─────────────────────────────────────────────
        ("HIST 220", "US History to 1877", 3, ["American Civilization"]),
        ("HIST 221", "US History from 1877", 3, ["American Civilization"]),
        ("POLI 110", "Introduction to American Government", 3, ["American Civilization", "Social and Behavioral Sciences"]),
        ("MFHD 210", "Foundations of Family Life", 3, ["American Civilization", "Social and Behavioral Sciences"]),
        ("HONRS 201", "American Heritage Honors Civ", 3, ["American Civilization"]),

        # ── Religion ──────────────────────────────────────────────────────────
        ("REL A 101", "Foundations of the Restoration", 2, ["Religion"]),
        ("REL A 111", "The Eternal Family", 2, ["Religion"]),
        ("REL A 121", "The Book of Mormon", 2, ["Religion"]),
        ("REL A 122", "The Book of Mormon", 2, ["Religion"]),
        ("REL A 211", "Doctrine and Covenants", 2, ["Religion"]),
        ("REL A 212", "Church History and Doctrine", 2, ["Religion"]),
        ("REL A 250", "Jesus Christ and the Everlasting Gospel", 2, ["Religion"]),
        ("REL A 275", "Teachings and Doctrine of the Book of Mormon", 2, ["Religion"]),
        ("REL A 301", "Studies in Scripture", 2, ["Religion"]),
        ("REL A 302", "The Latter-day Saint Canon", 2, ["Religion"]),
        ("REL A 341", "Teachings of the Living Prophets", 2, ["Religion"]),
        ("REL C 225", "Eternal Family", 2, ["Religion"]),
        ("REL C 234", "Moral Foundations", 2, ["Religion"]),
        ("REL C 293R", "Special Topics in Religion", 2, ["Religion"]),
        ("REL C 300", "Old Testament", 2, ["Religion"]),
        ("REL C 333", "New Testament", 2, ["Religion"]),
        ("REL C 350", "Pearl of Great Price", 2, ["Religion"]),
        ("REL C 472", "Teachings of the Book of Mormon", 2, ["Religion"]),
        ("REL E 341", "Enduring Questions and Latter-day Saint Thought", 2, ["Religion"]),

        # ── First-Year Writing ────────────────────────────────────────────────
        ("WRTG 150", "Writing and Rhetoric", 3, ["First-Year Writing"]),
        ("WRTG 150H", "Writing and Rhetoric Honors", 3, ["First-Year Writing"]),
        ("HONRS 150", "Honors Writing", 3, ["First-Year Writing"]),
        ("ENG 150", "Writing and Rhetoric (ENG)", 3, ["First-Year Writing"]),
        ("ENGL 115", "Rhetoric and Civic Life", 3, ["First-Year Writing"]),

        # ── Advanced Written and Oral Communication ───────────────────────────
        ("WRTG 316", "Technical Writing", 3, ["Advanced Written and Oral Communication"]),
        ("WRTG 320", "Business Writing", 3, ["Advanced Written and Oral Communication"]),
        ("WRTG 330", "Professional Writing", 3, ["Advanced Written and Oral Communication"]),
        ("WRTG 340", "Science Writing", 3, ["Advanced Written and Oral Communication"]),
        ("WRTG 410", "Advanced Editing", 3, ["Advanced Written and Oral Communication"]),
        ("WRTG 420", "Grant Writing", 3, ["Advanced Written and Oral Communication"]),
        ("WRTG 310", "Writing in the Professions", 3, ["Advanced Written and Oral Communication"]),
        ("COMM 101", "Principles of Public Speaking", 3, ["Advanced Written and Oral Communication"]),
        ("COMM 310", "Advanced Public Speaking", 3, ["Advanced Written and Oral Communication"]),
        ("ENGL 295", "Professional Writing for English Majors", 3, ["Advanced Written and Oral Communication"]),
        ("ENGL 310", "Technical Editing", 3, ["Advanced Written and Oral Communication"]),
        ("BUS M 341", "Business Communication", 3, ["Advanced Written and Oral Communication"]),

        # ── Languages of Learning (Quantitative) ─────────────────────────────
        ("MATH 110", "College Algebra", 3, ["Languages of Learning (Quantitative)"]),
        ("MATH 112", "Calculus 1", 4, ["Languages of Learning (Quantitative)"]),
        ("MATH 113", "Calculus 2", 4, ["Languages of Learning (Quantitative)"]),
        ("MATH 119", "Calculus of One Variable", 4, ["Languages of Learning (Quantitative)"]),
        ("MATH 213", "Elementary Linear Algebra", 3, ["Languages of Learning (Quantitative)"]),
        ("MATH 290", "Fundamentals of Mathematics", 3, ["Languages of Learning (Quantitative)"]),
        ("STAT 121", "Principles of Statistics", 3, ["Languages of Learning (Quantitative)"]),
        ("STAT 221", "Statistics for Research", 3, ["Languages of Learning (Quantitative)"]),
        ("STAT 230", "Applied Statistics", 3, ["Languages of Learning (Quantitative)"]),
        ("CS 110", "Python Programming", 3, ["Languages of Learning (Quantitative)"]),
        ("CS 142", "Introduction to Computer Programming", 3, ["Languages of Learning (Quantitative)"]),
        ("IT 201", "Information Technology Fundamentals", 3, ["Languages of Learning (Quantitative)"]),
        ("PSYCH 301", "Quantitative Research Methods in Psychology", 3, ["Languages of Learning (Quantitative)"]),

        # ── Arts ──────────────────────────────────────────────────────────────
        ("ART 100", "Foundations of Visual Arts", 3, ["Arts"]),
        ("ART 100R", "Foundation Studies in Art", 3, ["Arts"]),
        ("ART 114", "Drawing", 3, ["Arts"]),
        ("ART 115", "Painting", 3, ["Arts"]),
        ("ART 201", "Art History Survey 1", 3, ["Arts", "Comparative Civilization"]),
        ("MUSIC 101", "Introduction to Music", 3, ["Arts"]),
        ("MUSIC 202", "Music Theory", 3, ["Arts"]),
        ("MUSIC 206", "World Music", 3, ["Arts", "Global and Cultural Awareness"]),
        ("THEATRE 101", "Introduction to Theatre", 3, ["Arts"]),
        ("TMA 101", "Introduction to Theatre and Media Arts", 3, ["Arts"]),
        ("DANCE 180", "Introduction to Dance", 2, ["Arts"]),
        ("DES 101", "Design Foundations", 3, ["Arts"]),
        ("HONRS 202", "Great Works: Visual Arts", 3, ["Arts", "Comparative Civilization", "Letters"]),

        # ── Letters ───────────────────────────────────────────────────────────
        ("ENGL 251", "Introduction to Literature", 3, ["Letters"]),
        ("ENGL 292", "Introduction to Literary Theory", 3, ["Letters"]),
        ("ENGL 305", "Advanced Literary Studies", 3, ["Letters"]),
        ("ENGL 336", "British Literature", 3, ["Letters"]),
        ("ENGL 340", "Survey of World Literature", 3, ["Letters", "Global and Cultural Awareness"]),
        ("ENGL 359", "American Literature", 3, ["Letters"]),
        ("ENGL 382", "Creative Nonfiction", 3, ["Letters"]),
        ("PHIL 101", "Introduction to Philosophy", 3, ["Letters"]),
        ("PHIL 201", "Ethical Reasoning", 3, ["Letters"]),
        ("PHIL 218", "Logic", 3, ["Letters"]),
        ("HIST 201", "World History to 1500", 3, ["Letters", "Global and Cultural Awareness"]),
        ("HONRS 203R", "Great Works: Literature", 3, ["Letters"]),

        # ── Life Sciences ─────────────────────────────────────────────────────
        ("BIO 100", "Principles of Biology", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("BIO 130", "Human Biology", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("BIOL 130", "Human Biology", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("PDBIO 120", "Human Biology", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("PDBIO 220", "Human Physiology", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("MMBIO 101", "Microbiology and Infectious Disease", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("NDFS 100", "Fundamentals of Nutrition", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("NDFS 101", "Essentials of Nutrition", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),
        ("HLTH 100", "Foundations of Health", 3, ["Scientific Principles and Reasoning (Life Sciences)"]),

        # ── Physical Sciences ─────────────────────────────────────────────────
        ("CHEM 101", "Fundamentals of Chemistry", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("CHEM 105", "General Chemistry 1", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("CHEM 106", "General Chemistry 2", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("CHEM 111", "Preparation for General Chemistry", 2, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("PHSCS 100", "Descriptive Astronomy", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("PHSCS 105", "Introduction to Astronomy", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("PHSCS 106", "Conceptual Physics", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("PHY S 100", "Descriptive Astronomy", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("GEOL 101", "Principles of Geology", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),
        ("GEOG 111", "Physical Geography", 3, ["Scientific Principles and Reasoning (Physical Sciences)"]),

        # ── Social and Behavioral Sciences ────────────────────────────────────
        ("PSYCH 111", "Introduction to Psychology", 3, ["Social and Behavioral Sciences"]),
        ("SOC 111", "Introduction to Sociology", 3, ["Social and Behavioral Sciences"]),
        ("ANTHR 101", "Introduction to Anthropology", 3, ["Social and Behavioral Sciences", "Global and Cultural Awareness"]),
        ("HIST 310", "History and Social Theory", 3, ["Social and Behavioral Sciences"]),

        # ── Global and Cultural Awareness ─────────────────────────────────────
        ("GEOG 101", "World Regional Geography", 3, ["Global and Cultural Awareness"]),
        ("ANTHR 317", "Cultural Anthropology", 3, ["Global and Cultural Awareness"]),
        ("ANTHR 326", "Language and Culture", 3, ["Global and Cultural Awareness"]),
        ("ARTHC 203", "Art History Survey", 3, ["Global and Cultural Awareness"]),
        ("ASIAN 101", "Introduction to Asian Civilizations", 3, ["Global and Cultural Awareness", "Comparative Civilization"]),
        ("ENG T 231", "Introduction to Global Studies", 3, ["Global and Cultural Awareness", "Social and Behavioral Sciences"]),
        ("IHUM 240", "Humanities and the Arts", 3, ["Global and Cultural Awareness", "Arts", "Letters"]),
        ("INTL 201", "Introduction to International Studies", 3, ["Global and Cultural Awareness"]),
        ("LATIN 101", "Latin American Civilizations", 3, ["Global and Cultural Awareness", "Comparative Civilization"]),

        # ── Comparative Civilization ──────────────────────────────────────────
        ("HIST 202", "World History 1500-Present", 3, ["Comparative Civilization", "Global and Cultural Awareness"]),
        ("PHIL 202", "World Religions", 3, ["Comparative Civilization", "Global and Cultural Awareness"]),
        ("HON P 202", "Civilizations Honors", 3, ["Comparative Civilization"]),
        ("HONRS 212", "Great Civilizations", 3, ["Comparative Civilization"]),
        ("HONRS 213", "Non-Western Civilizations", 3, ["Comparative Civilization", "Global and Cultural Awareness"]),
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
