"""
BYU Major Requirements — Scraper + Seed Data
=============================================
Provides major requirement data for the optimizer.

Data source: BYU Undergraduate Catalog 2024-2025.
Seed data was hand-curated from catalog.byu.edu program pages.
Live scraping is not feasible because catalog.byu.edu is a JS SPA.

Usage:
    from major_scraper import get_major_registry, get_all_major_slugs
    registry = get_major_registry()   # dict: slug → MajorDefinition
"""

from __future__ import annotations
from typing import Dict
from major_requirements import MajorDefinition, MajorReqGroup

# ── GE category name constants (must match pathways.py) ──────────────────────
_GE_AMERICAN_HERITAGE  = "American Heritage"
_GE_AMERICAN_CIV       = "American Civilization"
_GE_RELIGION           = "Religion"
_GE_FIRST_YEAR_WRITING = "First-Year Writing"
_GE_ADV_WRITING        = "Advanced Written and Oral Communication"
_GE_QUANTITATIVE       = "Languages of Learning (Quantitative)"
_GE_ARTS               = "Arts"
_GE_LETTERS            = "Letters"
_GE_LIFE_SCI           = "Scientific Principles and Reasoning (Life Sciences)"
_GE_PHYS_SCI           = "Scientific Principles and Reasoning (Physical Sciences)"
_GE_SOCIAL             = "Social and Behavioral Sciences"
_GE_GLOBAL             = "Global and Cultural Awareness"
_GE_COMPARATIVE        = "Comparative Civilization"


# ── Seed data ────────────────────────────────────────────────────────────────

_SEED: Dict[str, MajorDefinition] = {}


def _add(major: MajorDefinition) -> None:
    _SEED[major.major_slug] = major


# ─────────────────────────────────────────────────────────────────────────────
# Computer Science BS
# catalog.byu.edu/physical-and-mathematical-sciences/computer-science/computer-science-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="computer-science-bs",
    major_name="Computer Science (BS)",
    college="Physical and Mathematical Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Intro Programming",
            req_type="required",
            course_pool=["CS 142"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Data Structures",
            req_type="required",
            course_pool=["CS 235"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Discrete Math",
            req_type="required",
            course_pool=["CS 236"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Advanced Software Construction",
            req_type="required",
            course_pool=["CS 240"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Computational Theory",
            req_type="required",
            course_pool=["CS 252"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Algorithm Design",
            req_type="required",
            course_pool=["CS 312"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Systems Programming",
            req_type="required",
            course_pool=["CS 324"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Software Design",
            req_type="required",
            course_pool=["CS 340"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Ethics in Computing",
            req_type="required",
            course_pool=["CS 404"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Software Engineering or Capstone",
            req_type="elective_group",
            course_pool=["CS 428", "CS 401R", "CS 498R"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Calculus I",
            req_type="required",
            course_pool=["MATH 112"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Calculus II",
            req_type="required",
            course_pool=["MATH 113"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Discrete or Multivariable Math",
            req_type="elective_group",
            course_pool=["MATH 213", "MATH 290", "MATH 314"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Statistics",
            req_type="elective_group",
            course_pool=["STAT 121", "STAT 201", "STAT 230"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="CS Electives (upper division)",
            req_type="elective_group",
            course_pool=["CS 355", "CS 356", "CS 360", "CS 371", "CS 390", "CS 393",
                         "CS 395", "CS 412", "CS 418", "CS 420", "CS 450", "CS 455",
                         "CS 460", "CS 465", "CS 470", "CS 486", "CS 490", "CS 493R"],
            courses_needed=4,
            notes="Choose 4 upper-division CS electives",
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Psychology BS
# catalog.byu.edu/family-home-social-sciences/psychology/psychology-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="psychology-bs",
    major_name="Psychology (BS)",
    college="Family, Home, and Social Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="General Psychology",
            req_type="required",
            course_pool=["PSYCH 111"],
            courses_needed=1,
            also_satisfies_ge=[_GE_SOCIAL],
        ),
        MajorReqGroup(
            group_name="Research Methods",
            req_type="required",
            course_pool=["PSYCH 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Statistics for Psychology",
            req_type="required",
            course_pool=["STAT 121"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Behavioral Neuroscience",
            req_type="required",
            course_pool=["PSYCH 307"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Developmental Psychology",
            req_type="required",
            course_pool=["PSYCH 309"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Abnormal Psychology",
            req_type="required",
            course_pool=["PSYCH 310"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Social Psychology",
            req_type="required",
            course_pool=["PSYCH 370"],
            courses_needed=1,
            also_satisfies_ge=[_GE_SOCIAL],
        ),
        MajorReqGroup(
            group_name="Advanced Research Practicum",
            req_type="required",
            course_pool=["PSYCH 394R"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Psychology Electives",
            req_type="elective_group",
            course_pool=["PSYCH 340", "PSYCH 350", "PSYCH 360", "PSYCH 380",
                         "PSYCH 420", "PSYCH 430", "PSYCH 460", "PSYCH 490"],
            courses_needed=4,
            notes="Choose 4 upper-division psychology electives",
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Biology BS
# catalog.byu.edu/life-sciences/biology/biology-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="biology-bs",
    major_name="Biology (BS)",
    college="Life Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Principles of Biology",
            req_type="required",
            course_pool=["BIO 130"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LIFE_SCI],
        ),
        MajorReqGroup(
            group_name="Cell Biology and Genetics",
            req_type="required",
            course_pool=["BIO 220"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Ecology or Evolutionary Biology",
            req_type="elective_group",
            course_pool=["BIO 250", "BIO 255"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="General Chemistry I",
            req_type="required",
            course_pool=["CHEM 105"],
            courses_needed=1,
            also_satisfies_ge=[_GE_PHYS_SCI],
        ),
        MajorReqGroup(
            group_name="General Chemistry II",
            req_type="required",
            course_pool=["CHEM 106"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Organic Chemistry",
            req_type="required",
            course_pool=["CHEM 351"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Calculus I",
            req_type="required",
            course_pool=["MATH 112"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Physics",
            req_type="elective_group",
            course_pool=["PHYS 105", "PHYS 121"],
            courses_needed=1,
            also_satisfies_ge=[_GE_PHYS_SCI],
        ),
        MajorReqGroup(
            group_name="Statistics",
            req_type="elective_group",
            course_pool=["STAT 121", "STAT 201"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Biology Electives (upper division)",
            req_type="elective_group",
            dept_prefix="BIO",
            level_min=300,
            credit_minimum=18,
            notes="18 credits of upper-division biology electives",
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Accounting BS
# catalog.byu.edu/marriott-school-business/school-accountancy/accounting-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="accounting-bs",
    major_name="Accounting (BS)",
    college="Marriott School of Business",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Economics",
            req_type="required",
            course_pool=["ECON 110"],
            courses_needed=1,
            also_satisfies_ge=[_GE_SOCIAL, _GE_AMERICAN_CIV],
        ),
        MajorReqGroup(
            group_name="Business Math",
            req_type="elective_group",
            course_pool=["MATH 110", "MATH 112"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Financial Accounting",
            req_type="required",
            course_pool=["ACC 200"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Managerial Accounting",
            req_type="required",
            course_pool=["ACC 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Intermediate Accounting I",
            req_type="required",
            course_pool=["ACC 310"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Intermediate Accounting II",
            req_type="required",
            course_pool=["ACC 311"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Cost Accounting",
            req_type="required",
            course_pool=["ACC 312"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Accounting Information Systems",
            req_type="required",
            course_pool=["ACC 360"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Auditing",
            req_type="required",
            course_pool=["ACC 440"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Taxation",
            req_type="required",
            course_pool=["ACC 470"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Financial Management",
            req_type="required",
            course_pool=["MFIN 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Business Law",
            req_type="required",
            course_pool=["BUS M 241"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Business Statistics",
            req_type="elective_group",
            course_pool=["STAT 121", "STAT 201"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Communication BS
# catalog.byu.edu/fine-arts-communications/communications/communication-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="communication-bs",
    major_name="Communication (BS)",
    college="College of Fine Arts and Communications",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Introduction to Communication",
            req_type="required",
            course_pool=["COMMS 101"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Communication Theory",
            req_type="required",
            course_pool=["COMMS 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Research Methods in Communication",
            req_type="required",
            course_pool=["COMMS 301"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Communication Law and Ethics",
            req_type="required",
            course_pool=["COMMS 390"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Senior Seminar",
            req_type="required",
            course_pool=["COMMS 495"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Statistics",
            req_type="elective_group",
            course_pool=["STAT 121", "STAT 201"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Communication Emphasis Electives",
            req_type="elective_group",
            course_pool=["COMMS 320", "COMMS 330", "COMMS 340", "COMMS 350",
                         "COMMS 360", "COMMS 370", "COMMS 380", "COMMS 410",
                         "COMMS 420", "COMMS 430", "COMMS 440", "COMMS 460"],
            courses_needed=5,
            notes="Choose 5 communication electives for your emphasis",
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Mechanical Engineering BS
# catalog.byu.edu/engineering/mechanical-engineering/mechanical-engineering-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="mechanical-engineering-bs",
    major_name="Mechanical Engineering (BS)",
    college="Ira A. Fulton College of Engineering",
    catalog_year="2024-2025",
    total_credits=128,
    groups=[
        MajorReqGroup(
            group_name="Calculus I",
            req_type="required",
            course_pool=["MATH 112"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Calculus II",
            req_type="required",
            course_pool=["MATH 113"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Multivariable Calculus",
            req_type="required",
            course_pool=["MATH 213"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Differential Equations",
            req_type="required",
            course_pool=["MATH 303"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Physics I (Mechanics)",
            req_type="required",
            course_pool=["PHYS 121"],
            courses_needed=1,
            also_satisfies_ge=[_GE_PHYS_SCI],
        ),
        MajorReqGroup(
            group_name="Physics II (E&M)",
            req_type="required",
            course_pool=["PHYS 122"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="General Chemistry",
            req_type="required",
            course_pool=["CHEM 105"],
            courses_needed=1,
            also_satisfies_ge=[_GE_PHYS_SCI],
        ),
        MajorReqGroup(
            group_name="ME Intro",
            req_type="required",
            course_pool=["ME 101"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Statics",
            req_type="required",
            course_pool=["ME 273"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Mechanics of Materials",
            req_type="required",
            course_pool=["ME 311"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Dynamics",
            req_type="required",
            course_pool=["ME 312"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Thermodynamics",
            req_type="required",
            course_pool=["ME 340"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Fluid Mechanics",
            req_type="required",
            course_pool=["ME 360"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Heat Transfer",
            req_type="required",
            course_pool=["ME 362"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Machine Design",
            req_type="required",
            course_pool=["ME 382"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Controls",
            req_type="required",
            course_pool=["ME 411"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Senior Design",
            req_type="required",
            course_pool=["ME 471", "ME 472"],
            courses_needed=2,
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Exercise Science BS
# catalog.byu.edu/life-sciences/exercise-sciences/exercise-science-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="exercise-science-bs",
    major_name="Exercise Science (BS)",
    college="Life Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Principles of Biology",
            req_type="required",
            course_pool=["BIO 130"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LIFE_SCI],
        ),
        MajorReqGroup(
            group_name="Chemistry",
            req_type="elective_group",
            course_pool=["CHEM 105", "CHEM 101"],
            courses_needed=1,
            also_satisfies_ge=[_GE_PHYS_SCI],
        ),
        MajorReqGroup(
            group_name="Statistics",
            req_type="elective_group",
            course_pool=["STAT 121", "STAT 201"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Introduction to Exercise Science",
            req_type="required",
            course_pool=["EXSC 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Human Anatomy",
            req_type="required",
            course_pool=["EXSC 210"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Physiology",
            req_type="required",
            course_pool=["EXSC 305"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Exercise Physiology",
            req_type="required",
            course_pool=["EXSC 375"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Biomechanics",
            req_type="required",
            course_pool=["EXSC 376"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Fitness Assessment",
            req_type="required",
            course_pool=["EXSC 405"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Exercise Programming",
            req_type="required",
            course_pool=["EXSC 410"],
            courses_needed=1,
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Finance BS
# catalog.byu.edu/marriott-school-business/finance/finance-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="finance-bs",
    major_name="Finance (BS)",
    college="Marriott School of Business",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Economics",
            req_type="required",
            course_pool=["ECON 110"],
            courses_needed=1,
            also_satisfies_ge=[_GE_SOCIAL, _GE_AMERICAN_CIV],
        ),
        MajorReqGroup(
            group_name="Business Math",
            req_type="elective_group",
            course_pool=["MATH 110", "MATH 112"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Business Statistics",
            req_type="elective_group",
            course_pool=["STAT 121", "STAT 201"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Financial Accounting",
            req_type="required",
            course_pool=["ACC 200"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Managerial Accounting",
            req_type="required",
            course_pool=["ACC 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Financial Management",
            req_type="required",
            course_pool=["MFIN 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Investments",
            req_type="required",
            course_pool=["MFIN 301"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Corporate Finance",
            req_type="required",
            course_pool=["MFIN 401"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Business Law",
            req_type="required",
            course_pool=["BUS M 241"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Finance Electives",
            req_type="elective_group",
            course_pool=["MFIN 310", "MFIN 320", "MFIN 410", "MFIN 420",
                         "MFIN 430", "MFIN 440", "MFIN 450", "MFIN 460"],
            courses_needed=3,
            notes="Choose 3 finance electives",
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Business Management BS
# catalog.byu.edu/marriott-school-business/business-management/business-management-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="business-management-bs",
    major_name="Business Management (BS)",
    college="Marriott School of Business",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Economics",
            req_type="required",
            course_pool=["ECON 110"],
            courses_needed=1,
            also_satisfies_ge=[_GE_SOCIAL, _GE_AMERICAN_CIV],
        ),
        MajorReqGroup(
            group_name="Business Math",
            req_type="elective_group",
            course_pool=["MATH 110", "MATH 112"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Business Statistics",
            req_type="elective_group",
            course_pool=["STAT 121", "STAT 201"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Financial Accounting",
            req_type="required",
            course_pool=["ACC 200"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Managerial Accounting",
            req_type="required",
            course_pool=["ACC 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Financial Management",
            req_type="required",
            course_pool=["MFIN 201"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Business Law",
            req_type="required",
            course_pool=["BUS M 241"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Organizational Behavior",
            req_type="required",
            course_pool=["BUS M 301"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Marketing",
            req_type="required",
            course_pool=["BUS M 361"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Operations Management",
            req_type="required",
            course_pool=["BUS M 471"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Strategic Management",
            req_type="required",
            course_pool=["BUS M 491"],
            courses_needed=1,
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# English BS
# catalog.byu.edu/humanities/english/english-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="english-bs",
    major_name="English (BS)",
    college="College of Humanities",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Introduction to Literary Study",
            req_type="required",
            course_pool=["ENGL 251"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LETTERS],
        ),
        MajorReqGroup(
            group_name="British Literature Survey",
            req_type="elective_group",
            course_pool=["ENGL 256", "ENGL 257"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LETTERS],
        ),
        MajorReqGroup(
            group_name="American Literature Survey",
            req_type="elective_group",
            course_pool=["ENGL 258", "ENGL 259"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LETTERS],
        ),
        MajorReqGroup(
            group_name="World Literature",
            req_type="elective_group",
            course_pool=["ENGL 270", "ENGL 271"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LETTERS, _GE_GLOBAL],
        ),
        MajorReqGroup(
            group_name="Literary Theory",
            req_type="required",
            course_pool=["ENGL 295"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Advanced Writing",
            req_type="elective_group",
            course_pool=["ENGL 315", "ENGL 316", "ENGL 318"],
            courses_needed=1,
            also_satisfies_ge=[_GE_ADV_WRITING],
        ),
        MajorReqGroup(
            group_name="Shakespeare",
            req_type="required",
            course_pool=["ENGL 382"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="English Electives (upper division)",
            req_type="elective_group",
            dept_prefix="ENGL",
            level_min=300,
            credit_minimum=15,
            notes="15 credits of upper-division English electives",
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Elementary Education BS
# catalog.byu.edu/education/teacher-education/elementary-education-bs
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="elementary-education-bs",
    major_name="Elementary Education (BS)",
    college="McKay School of Education",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup(
            group_name="Math for Elementary Teachers I",
            req_type="required",
            course_pool=["MTHED 112"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Math for Elementary Teachers II",
            req_type="required",
            course_pool=["MTHED 113"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Life Science for Teachers",
            req_type="required",
            course_pool=["SFL 240"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LIFE_SCI],
        ),
        MajorReqGroup(
            group_name="Physical Science for Teachers",
            req_type="elective_group",
            course_pool=["PHSCS 100", "CHEM 100"],
            courses_needed=1,
            also_satisfies_ge=[_GE_PHYS_SCI],
        ),
        MajorReqGroup(
            group_name="Child Development",
            req_type="required",
            course_pool=["SFL 160"],
            courses_needed=1,
            also_satisfies_ge=[_GE_SOCIAL],
        ),
        MajorReqGroup(
            group_name="Introduction to Teaching",
            req_type="required",
            course_pool=["IP&T 301"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Literacy Instruction",
            req_type="required",
            course_pool=["EL ED 310"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Elementary Math Methods",
            req_type="required",
            course_pool=["EL ED 371"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Social Studies Methods",
            req_type="required",
            course_pool=["EL ED 375"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Student Teaching",
            req_type="capstone",
            course_pool=["EL ED 491R"],
            courses_needed=1,
            notes="Full-semester student teaching placement",
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Nursing BSN
# catalog.byu.edu/nursing/nursing/nursing-bsn
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="nursing-bsn",
    major_name="Nursing (BSN)",
    college="College of Nursing",
    catalog_year="2024-2025",
    total_credits=122,
    groups=[
        MajorReqGroup(
            group_name="Human Biology",
            req_type="required",
            course_pool=["BIO 130"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LIFE_SCI],
        ),
        MajorReqGroup(
            group_name="Anatomy and Physiology",
            req_type="required",
            course_pool=["NURS 223"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Microbiology",
            req_type="required",
            course_pool=["MMBIO 240"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Chemistry",
            req_type="elective_group",
            course_pool=["CHEM 101", "CHEM 105"],
            courses_needed=1,
            also_satisfies_ge=[_GE_PHYS_SCI],
        ),
        MajorReqGroup(
            group_name="Statistics",
            req_type="elective_group",
            course_pool=["STAT 121", "STAT 201"],
            courses_needed=1,
            also_satisfies_ge=[_GE_QUANTITATIVE],
        ),
        MajorReqGroup(
            group_name="Nutrition",
            req_type="required",
            course_pool=["NDFS 100"],
            courses_needed=1,
            also_satisfies_ge=[_GE_LIFE_SCI],
        ),
        MajorReqGroup(
            group_name="Foundations of Nursing",
            req_type="required",
            course_pool=["NURS 310"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Pathophysiology",
            req_type="required",
            course_pool=["NURS 320"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Pharmacology",
            req_type="required",
            course_pool=["NURS 330"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Community Health Nursing",
            req_type="required",
            course_pool=["NURS 420"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Nursing Research",
            req_type="required",
            course_pool=["NURS 430"],
            courses_needed=1,
        ),
        MajorReqGroup(
            group_name="Capstone Clinical",
            req_type="capstone",
            course_pool=["NURS 491R"],
            courses_needed=1,
            notes="Senior clinical practicum",
        ),
    ],
))


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_major_registry() -> Dict[str, MajorDefinition]:
    """Return the full registry of MajorDefinition objects keyed by slug."""
    return dict(_SEED)


def get_all_major_slugs() -> list:
    return sorted(_SEED.keys())


def get_major_options_for_ui() -> list:
    """Return list of (display_label, slug) tuples grouped by college for UI dropdowns."""
    by_college: Dict[str, list] = {}
    for major in _SEED.values():
        by_college.setdefault(major.college, []).append(major)
    result = []
    for college in sorted(by_college):
        for m in sorted(by_college[college], key=lambda x: x.major_name):
            result.append((f"{m.major_name}", m.major_slug, m.college))
    return result
