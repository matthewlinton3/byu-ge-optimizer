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
# Electrical Engineering BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="electrical-engineering-bs",
    major_name="Electrical Engineering (BS)",
    college="Ira A. Fulton College of Engineering",
    catalog_year="2024-2025",
    total_credits=128,
    groups=[
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Calculus II", "required", ["MATH 113"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Multivariable Calculus", "required", ["MATH 213"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Differential Equations", "required", ["MATH 303"], 1),
        MajorReqGroup("Physics I (Mechanics)", "required", ["PHYS 121"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Physics II (E&M)", "required", ["PHYS 122"], 1),
        MajorReqGroup("General Chemistry", "required", ["CHEM 105"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Intro to EE", "required", ["ECEn 191"], 1),
        MajorReqGroup("Circuits I", "required", ["ECEn 220"], 1),
        MajorReqGroup("Circuits II", "required", ["ECEn 221"], 1),
        MajorReqGroup("Signals and Systems", "required", ["ECEn 240"], 1),
        MajorReqGroup("Digital Circuits", "required", ["ECEn 220", "ECEn 323"], 1),
        MajorReqGroup("Electromagnetics", "required", ["ECEn 360"], 1),
        MajorReqGroup("Electronics", "required", ["ECEn 370"], 1),
        MajorReqGroup("EE Electives", "elective_group",
            ["ECEn 380", "ECEn 390", "ECEn 420", "ECEn 425", "ECEn 450", "ECEn 462", "ECEn 471", "ECEn 485"],
            courses_needed=3, notes="3 upper-division EE electives"),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Computer Engineering BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="computer-engineering-bs",
    major_name="Computer Engineering (BS)",
    college="Ira A. Fulton College of Engineering",
    catalog_year="2024-2025",
    total_credits=128,
    groups=[
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Calculus II", "required", ["MATH 113"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Multivariable Calculus", "required", ["MATH 213"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Differential Equations", "required", ["MATH 303"], 1),
        MajorReqGroup("Physics I", "required", ["PHYS 121"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Physics II", "required", ["PHYS 122"], 1),
        MajorReqGroup("Intro Programming", "required", ["CS 142"], 1),
        MajorReqGroup("Data Structures", "required", ["CS 235"], 1),
        MajorReqGroup("Discrete Math", "required", ["CS 236"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Digital Logic", "required", ["ECEn 220"], 1),
        MajorReqGroup("Circuits", "required", ["ECEn 221"], 1),
        MajorReqGroup("Computer Architecture", "required", ["ECEn 323"], 1),
        MajorReqGroup("Operating Systems", "required", ["CS 324"], 1),
        MajorReqGroup("Embedded Systems", "required", ["ECEn 425"], 1),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Civil Engineering BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="civil-engineering-bs",
    major_name="Civil Engineering (BS)",
    college="Ira A. Fulton College of Engineering",
    catalog_year="2024-2025",
    total_credits=128,
    groups=[
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Calculus II", "required", ["MATH 113"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Multivariable Calculus", "required", ["MATH 213"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Differential Equations", "required", ["MATH 303"], 1),
        MajorReqGroup("Physics I", "required", ["PHYS 121"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("General Chemistry", "required", ["CHEM 105"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Statistics for Engineers", "required", ["CE 321"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Statics", "required", ["ME 273"], 1),
        MajorReqGroup("Mechanics of Materials", "required", ["CE 305"], 1),
        MajorReqGroup("Fluid Mechanics", "required", ["CE 340"], 1),
        MajorReqGroup("Structural Analysis", "required", ["CE 361"], 1),
        MajorReqGroup("Soil Mechanics", "required", ["CE 370"], 1),
        MajorReqGroup("Transportation Engineering", "required", ["CE 351"], 1),
        MajorReqGroup("Senior Design", "capstone", ["CE 471", "CE 472"], 2),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Chemical Engineering BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="chemical-engineering-bs",
    major_name="Chemical Engineering (BS)",
    college="Ira A. Fulton College of Engineering",
    catalog_year="2024-2025",
    total_credits=128,
    groups=[
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Calculus II", "required", ["MATH 113"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Multivariable Calculus", "required", ["MATH 213"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Differential Equations", "required", ["MATH 303"], 1),
        MajorReqGroup("Physics I", "required", ["PHYS 121"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("General Chemistry I", "required", ["CHEM 105"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("General Chemistry II", "required", ["CHEM 106"], 1),
        MajorReqGroup("Organic Chemistry I", "required", ["CHEM 351"], 1),
        MajorReqGroup("Intro to ChemEn", "required", ["ChEn 110"], 1),
        MajorReqGroup("Material and Energy Balances", "required", ["ChEn 273"], 1),
        MajorReqGroup("Thermodynamics", "required", ["ChEn 374"], 1),
        MajorReqGroup("Fluid Mechanics", "required", ["ChEn 376"], 1),
        MajorReqGroup("Heat and Mass Transfer", "required", ["ChEn 378"], 1),
        MajorReqGroup("Reaction Engineering", "required", ["ChEn 475"], 1),
        MajorReqGroup("Senior Design", "capstone", ["ChEn 492"], 1),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Mathematics BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="mathematics-bs",
    major_name="Mathematics (BS)",
    college="Physical and Mathematical Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Calculus II", "required", ["MATH 113"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Multivariable Calculus", "required", ["MATH 213"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Linear Algebra", "required", ["MATH 213"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Foundations of Analysis", "required", ["MATH 290"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Differential Equations", "required", ["MATH 303"], 1),
        MajorReqGroup("Real Analysis", "required", ["MATH 341"], 1),
        MajorReqGroup("Abstract Algebra", "required", ["MATH 371"], 1),
        MajorReqGroup("Complex Analysis or Topology", "elective_group", ["MATH 342", "MATH 450"], 1),
        MajorReqGroup("Math Electives (upper division)", "elective_group",
            ["MATH 302", "MATH 313", "MATH 314", "MATH 334", "MATH 352", "MATH 372",
             "MATH 411", "MATH 431", "MATH 451", "MATH 461", "MATH 487"],
            courses_needed=4, notes="4 additional upper-division math courses"),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Statistics BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="statistics-bs",
    major_name="Statistics (BS)",
    college="Physical and Mathematical Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Calculus II", "required", ["MATH 113"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Principles of Statistics", "required", ["STAT 121"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Intro Statistical Theory", "required", ["STAT 230"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Linear Models", "required", ["STAT 330"], 1),
        MajorReqGroup("Probability Theory", "required", ["STAT 340"], 1),
        MajorReqGroup("Mathematical Statistics", "required", ["STAT 441"], 1),
        MajorReqGroup("Applied Regression", "required", ["STAT 330"], 1),
        MajorReqGroup("Statistical Computing", "required", ["STAT 428"], 1),
        MajorReqGroup("Statistics Electives", "elective_group",
            ["STAT 431", "STAT 442", "STAT 461", "STAT 465", "STAT 470", "STAT 480"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Economics BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="economics-bs",
    major_name="Economics (BS)",
    college="Family, Home, and Social Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Economic Principles", "required", ["ECON 110"], 1, also_satisfies_ge=[_GE_SOCIAL, _GE_AMERICAN_CIV]),
        MajorReqGroup("Microeconomics", "required", ["ECON 210"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Macroeconomics", "required", ["ECON 211"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Statistics", "required", ["STAT 121"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Intermediate Microeconomics", "required", ["ECON 380"], 1),
        MajorReqGroup("Intermediate Macroeconomics", "required", ["ECON 381"], 1),
        MajorReqGroup("Econometrics", "required", ["ECON 388"], 1),
        MajorReqGroup("Economics Electives", "elective_group",
            ["ECON 301", "ECON 310", "ECON 382", "ECON 420", "ECON 430", "ECON 450", "ECON 460", "ECON 488"],
            courses_needed=4),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Political Science BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="political-science-bs",
    major_name="Political Science (BS)",
    college="Family, Home, and Social Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Introduction to Political Science", "required", ["POLI 110"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("American Government", "required", ["POLI 200"], 1, also_satisfies_ge=[_GE_AMERICAN_CIV, _GE_SOCIAL]),
        MajorReqGroup("Research Methods", "required", ["POLI 300"], 1),
        MajorReqGroup("Statistics", "required", ["STAT 121"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Political Theory", "required", ["POLI 310"], 1),
        MajorReqGroup("International Relations", "required", ["POLI 320"], 1, also_satisfies_ge=[_GE_GLOBAL]),
        MajorReqGroup("Comparative Politics", "required", ["POLI 330"], 1, also_satisfies_ge=[_GE_GLOBAL, _GE_COMPARATIVE]),
        MajorReqGroup("Political Science Electives", "elective_group",
            ["POLI 340", "POLI 350", "POLI 360", "POLI 370", "POLI 380",
             "POLI 410", "POLI 420", "POLI 430", "POLI 440", "POLI 460"],
            courses_needed=5),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# History BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="history-bs",
    major_name="History (BS)",
    college="College of Humanities",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("US History Survey", "elective_group", ["HIST 220", "HIST 221"], 1, also_satisfies_ge=[_GE_AMERICAN_CIV]),
        MajorReqGroup("World History Survey", "elective_group", ["HIST 200", "HIST 201"], 1, also_satisfies_ge=[_GE_GLOBAL, _GE_COMPARATIVE]),
        MajorReqGroup("Historical Methods", "required", ["HIST 291"], 1),
        MajorReqGroup("Advanced Writing for Historians", "required", ["HIST 395"], 1, also_satisfies_ge=[_GE_ADV_WRITING]),
        MajorReqGroup("Senior Seminar", "capstone", ["HIST 490"], 1),
        MajorReqGroup("US History Electives", "elective_group",
            ["HIST 301", "HIST 302", "HIST 361", "HIST 362", "HIST 365", "HIST 370"],
            courses_needed=2, notes="Upper-division US history"),
        MajorReqGroup("World/Comparative History Electives", "elective_group",
            ["HIST 310", "HIST 320", "HIST 330", "HIST 340", "HIST 350", "HIST 380", "HIST 385"],
            courses_needed=3, notes="Upper-division world/comparative history", also_satisfies_ge=[_GE_GLOBAL]),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Sociology BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="sociology-bs",
    major_name="Sociology (BS)",
    college="Family, Home, and Social Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Introduction to Sociology", "required", ["SOC 111"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Social Theory", "required", ["SOC 301"], 1),
        MajorReqGroup("Research Methods", "required", ["SOC 307"], 1),
        MajorReqGroup("Statistics", "required", ["STAT 121"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Race and Ethnicity", "elective_group", ["SOC 321", "ANTHR 320"], 1, also_satisfies_ge=[_GE_SOCIAL, _GE_GLOBAL]),
        MajorReqGroup("Sociology Electives", "elective_group",
            ["SOC 310", "SOC 320", "SOC 330", "SOC 340", "SOC 350", "SOC 360",
             "SOC 370", "SOC 380", "SOC 390", "SOC 420", "SOC 430"],
            courses_needed=5),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Neuroscience BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="neuroscience-bs",
    major_name="Neuroscience (BS)",
    college="Life Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Principles of Biology", "required", ["BIO 130"], 1, also_satisfies_ge=[_GE_LIFE_SCI]),
        MajorReqGroup("Cell Biology and Genetics", "required", ["BIO 220"], 1),
        MajorReqGroup("General Chemistry I", "required", ["CHEM 105"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("General Chemistry II", "required", ["CHEM 106"], 1),
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Physics", "elective_group", ["PHYS 105", "PHYS 121"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Statistics", "elective_group", ["STAT 121", "STAT 201"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("General Psychology", "required", ["PSYCH 111"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Intro to Neuroscience", "required", ["NEURO 205"], 1),
        MajorReqGroup("Cellular Neuroscience", "required", ["NEURO 305"], 1),
        MajorReqGroup("Systems Neuroscience", "required", ["NEURO 310"], 1),
        MajorReqGroup("Neuroscience Electives", "elective_group",
            ["NEURO 401", "NEURO 410", "NEURO 420", "NEURO 430", "NEURO 450", "PSYCH 307"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Biochemistry BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="biochemistry-bs",
    major_name="Biochemistry (BS)",
    college="Life Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Principles of Biology", "required", ["BIO 130"], 1, also_satisfies_ge=[_GE_LIFE_SCI]),
        MajorReqGroup("Cell Biology and Genetics", "required", ["BIO 220"], 1),
        MajorReqGroup("General Chemistry I", "required", ["CHEM 105"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("General Chemistry II", "required", ["CHEM 106"], 1),
        MajorReqGroup("Organic Chemistry I", "required", ["CHEM 351"], 1),
        MajorReqGroup("Organic Chemistry II", "required", ["CHEM 352"], 1),
        MajorReqGroup("Biochemistry I", "required", ["CHEM 481"], 1),
        MajorReqGroup("Biochemistry II", "required", ["CHEM 482"], 1),
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Physics", "elective_group", ["PHYS 105", "PHYS 121"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Statistics", "elective_group", ["STAT 121", "STAT 201"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Information Systems BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="information-systems-bs",
    major_name="Information Systems (BS)",
    college="Marriott School of Business",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Economics", "required", ["ECON 110"], 1, also_satisfies_ge=[_GE_SOCIAL, _GE_AMERICAN_CIV]),
        MajorReqGroup("Business Math", "elective_group", ["MATH 110", "MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Business Statistics", "elective_group", ["STAT 121", "STAT 201"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Intro Programming", "required", ["CS 142"], 1),
        MajorReqGroup("Financial Accounting", "required", ["ACC 200"], 1),
        MajorReqGroup("IS Core I", "required", ["IS 201"], 1),
        MajorReqGroup("IS Core II", "required", ["IS 301"], 1),
        MajorReqGroup("Database Management", "required", ["IS 304"], 1),
        MajorReqGroup("Systems Analysis", "required", ["IS 401"], 1),
        MajorReqGroup("Project Management", "required", ["IS 410"], 1),
        MajorReqGroup("IS Electives", "elective_group",
            ["IS 411", "IS 420", "IS 430", "IS 440", "IS 450", "IS 460"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Marriage, Family, and Human Development BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="marriage-family-human-development-bs",
    major_name="Marriage, Family, and Human Development (BS)",
    college="Family, Home, and Social Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Introduction to Family Processes", "required", ["SFL 101"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Child Development", "required", ["SFL 160"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Marriage and Family Relations", "required", ["SFL 210"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Research Methods", "required", ["SFL 301"], 1),
        MajorReqGroup("Statistics", "required", ["STAT 121"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Adolescent Development", "required", ["SFL 260"], 1),
        MajorReqGroup("Adult Development and Aging", "required", ["SFL 360"], 1),
        MajorReqGroup("Family Theory", "required", ["SFL 400"], 1),
        MajorReqGroup("SFL Electives", "elective_group",
            ["SFL 240", "SFL 290", "SFL 315", "SFL 320", "SFL 340", "SFL 380", "SFL 420", "SFL 450"],
            courses_needed=4),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Public Health BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="public-health-bs",
    major_name="Public Health (BS)",
    college="Life Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Principles of Biology", "required", ["BIO 130"], 1, also_satisfies_ge=[_GE_LIFE_SCI]),
        MajorReqGroup("Introduction to Public Health", "required", ["HLTH 100"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Statistics", "required", ["STAT 121"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Chemistry", "elective_group", ["CHEM 101", "CHEM 105"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Epidemiology", "required", ["HLTH 310"], 1),
        MajorReqGroup("Environmental Health", "required", ["HLTH 320"], 1),
        MajorReqGroup("Health Behavior", "required", ["HLTH 330"], 1),
        MajorReqGroup("Health Program Planning", "required", ["HLTH 410"], 1),
        MajorReqGroup("Global Health", "required", ["HLTH 350"], 1, also_satisfies_ge=[_GE_GLOBAL]),
        MajorReqGroup("Public Health Electives", "elective_group",
            ["HLTH 360", "HLTH 370", "HLTH 380", "HLTH 420", "HLTH 430", "HLTH 460"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Music BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="music-bs",
    major_name="Music (BS)",
    college="College of Fine Arts and Communications",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Music Theory I", "required", ["MUSIC 101"], 1, also_satisfies_ge=[_GE_ARTS]),
        MajorReqGroup("Music Theory II", "required", ["MUSIC 102"], 1),
        MajorReqGroup("Music Theory III", "required", ["MUSIC 201"], 1),
        MajorReqGroup("Music History I", "required", ["MUSIC 241"], 1, also_satisfies_ge=[_GE_ARTS, _GE_LETTERS]),
        MajorReqGroup("Music History II", "required", ["MUSIC 242"], 1, also_satisfies_ge=[_GE_ARTS]),
        MajorReqGroup("Aural Skills I", "required", ["MUSIC 131"], 1),
        MajorReqGroup("Aural Skills II", "required", ["MUSIC 132"], 1),
        MajorReqGroup("Applied Lessons", "elective_group",
            ["MUSIC 195R", "MUSIC 295R", "MUSIC 395R", "MUSIC 495R"], courses_needed=4),
        MajorReqGroup("Ensemble", "elective_group",
            ["MUSIC 160R", "MUSIC 260R", "MUSIC 360R"], courses_needed=3),
        MajorReqGroup("Music Electives", "elective_group",
            ["MUSIC 310", "MUSIC 320", "MUSIC 330", "MUSIC 340", "MUSIC 410", "MUSIC 420"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Animation BFA
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="animation-bfa",
    major_name="Animation (BFA)",
    college="College of Fine Arts and Communications",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Drawing Fundamentals", "required", ["ART 115"], 1, also_satisfies_ge=[_GE_ARTS]),
        MajorReqGroup("Art History", "required", ["ART 201"], 1, also_satisfies_ge=[_GE_ARTS, _GE_COMPARATIVE]),
        MajorReqGroup("Intro to Animation", "required", ["ANIM 101"], 1),
        MajorReqGroup("2D Animation", "required", ["ANIM 201"], 1),
        MajorReqGroup("3D Modeling", "required", ["ANIM 210"], 1),
        MajorReqGroup("3D Animation", "required", ["ANIM 301"], 1),
        MajorReqGroup("Character Animation", "required", ["ANIM 310"], 1),
        MajorReqGroup("Story and Script", "required", ["ANIM 250"], 1),
        MajorReqGroup("Senior Film Production", "capstone", ["ANIM 491R"], 1),
        MajorReqGroup("Animation Electives", "elective_group",
            ["ANIM 320", "ANIM 330", "ANIM 340", "ANIM 350", "ANIM 410", "ANIM 420"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# International Relations BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="international-relations-bs",
    major_name="International Relations (BS)",
    college="College of Humanities",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Introduction to International Relations", "required", ["POLI 320"], 1, also_satisfies_ge=[_GE_GLOBAL]),
        MajorReqGroup("Comparative Politics", "required", ["POLI 330"], 1, also_satisfies_ge=[_GE_GLOBAL, _GE_COMPARATIVE]),
        MajorReqGroup("International Political Economy", "required", ["POLI 340"], 1, also_satisfies_ge=[_GE_GLOBAL]),
        MajorReqGroup("World History", "elective_group", ["HIST 200", "HIST 201"], 1, also_satisfies_ge=[_GE_GLOBAL, _GE_COMPARATIVE]),
        MajorReqGroup("Economics", "required", ["ECON 110"], 1, also_satisfies_ge=[_GE_SOCIAL, _GE_AMERICAN_CIV]),
        MajorReqGroup("Statistics or Research Methods", "elective_group", ["STAT 121", "POLI 300"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Foreign Language (upper division)", "elective_group",
            ["CHIN 321", "SPAN 321", "FREN 321", "PORT 321", "GERM 321", "RUSS 321", "ARAB 321", "JAPN 321"],
            courses_needed=1, also_satisfies_ge=[_GE_GLOBAL]),
        MajorReqGroup("IR Electives", "elective_group",
            ["POLI 350", "POLI 360", "POLI 410", "POLI 420", "POLI 430", "POLI 440", "POLI 460"],
            courses_needed=4),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Social Work BSW
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="social-work-bsw",
    major_name="Social Work (BSW)",
    college="Family, Home, and Social Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Introduction to Social Work", "required", ["SOC WK 101"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Human Behavior and Social Environment I", "required", ["SOC WK 201"], 1),
        MajorReqGroup("Human Behavior and Social Environment II", "required", ["SOC WK 202"], 1),
        MajorReqGroup("Research Methods", "required", ["SOC WK 301"], 1),
        MajorReqGroup("Statistics", "required", ["STAT 121"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Social Policy", "required", ["SOC WK 310"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Practice I", "required", ["SOC WK 401"], 1),
        MajorReqGroup("Practice II", "required", ["SOC WK 402"], 1),
        MajorReqGroup("Field Practicum", "capstone", ["SOC WK 491R"], 1),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Entrepreneurial Management BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="entrepreneurial-management-bs",
    major_name="Entrepreneurial Management (BS)",
    college="Marriott School of Business",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Economics", "required", ["ECON 110"], 1, also_satisfies_ge=[_GE_SOCIAL, _GE_AMERICAN_CIV]),
        MajorReqGroup("Business Math", "elective_group", ["MATH 110", "MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Business Statistics", "elective_group", ["STAT 121", "STAT 201"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Financial Accounting", "required", ["ACC 200"], 1),
        MajorReqGroup("Managerial Accounting", "required", ["ACC 201"], 1),
        MajorReqGroup("Financial Management", "required", ["MFIN 201"], 1),
        MajorReqGroup("Intro to Entrepreneurship", "required", ["ENT 301"], 1),
        MajorReqGroup("Opportunity Recognition", "required", ["ENT 310"], 1),
        MajorReqGroup("New Venture Planning", "required", ["ENT 410"], 1),
        MajorReqGroup("Entrepreneurship Electives", "elective_group",
            ["ENT 320", "ENT 330", "ENT 340", "ENT 420", "ENT 430", "ENT 480"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Dietetics BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="dietetics-bs",
    major_name="Dietetics (BS)",
    college="Life Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Nutrition Fundamentals", "required", ["NDFS 100"], 1, also_satisfies_ge=[_GE_LIFE_SCI]),
        MajorReqGroup("Principles of Biology", "required", ["BIO 130"], 1, also_satisfies_ge=[_GE_LIFE_SCI]),
        MajorReqGroup("General Chemistry I", "required", ["CHEM 105"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("General Chemistry II", "required", ["CHEM 106"], 1),
        MajorReqGroup("Organic Chemistry", "required", ["CHEM 351"], 1),
        MajorReqGroup("Biochemistry", "required", ["CHEM 481"], 1),
        MajorReqGroup("Statistics", "elective_group", ["STAT 121", "STAT 201"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Physiology", "required", ["EXSC 305"], 1),
        MajorReqGroup("Nutrition Science", "required", ["NDFS 310"], 1),
        MajorReqGroup("Medical Nutrition Therapy", "required", ["NDFS 410"], 1),
        MajorReqGroup("Food Service Management", "required", ["NDFS 350"], 1),
        MajorReqGroup("Dietetics Practicum", "capstone", ["NDFS 491R"], 1),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Theatre Arts BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="theatre-arts-bs",
    major_name="Theatre Arts (BS)",
    college="College of Fine Arts and Communications",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Introduction to Theatre", "required", ["TMA 101"], 1, also_satisfies_ge=[_GE_ARTS]),
        MajorReqGroup("Theatre History I", "required", ["TMA 215"], 1, also_satisfies_ge=[_GE_ARTS, _GE_LETTERS]),
        MajorReqGroup("Theatre History II", "required", ["TMA 216"], 1, also_satisfies_ge=[_GE_ARTS]),
        MajorReqGroup("Script Analysis", "required", ["TMA 250"], 1),
        MajorReqGroup("Acting I", "required", ["TMA 261"], 1),
        MajorReqGroup("Acting II", "required", ["TMA 362"], 1),
        MajorReqGroup("Directing", "required", ["TMA 371"], 1),
        MajorReqGroup("Theatre Electives", "elective_group",
            ["TMA 310", "TMA 320", "TMA 330", "TMA 340", "TMA 350", "TMA 410", "TMA 420", "TMA 430"],
            courses_needed=4),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Linguistics BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="linguistics-bs",
    major_name="Linguistics (BS)",
    college="College of Humanities",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Introduction to Linguistics", "required", ["LING 101"], 1, also_satisfies_ge=[_GE_LETTERS]),
        MajorReqGroup("Phonetics and Phonology", "required", ["LING 201"], 1),
        MajorReqGroup("Morphology and Syntax", "required", ["LING 202"], 1),
        MajorReqGroup("Language Acquisition", "required", ["LING 301"], 1),
        MajorReqGroup("Statistics or Research Methods", "elective_group", ["STAT 121", "LING 350"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Sociolinguistics", "required", ["LING 310"], 1, also_satisfies_ge=[_GE_GLOBAL]),
        MajorReqGroup("Computational Linguistics", "elective_group", ["LING 360", "CS 470"], 1),
        MajorReqGroup("Linguistics Electives", "elective_group",
            ["LING 320", "LING 330", "LING 340", "LING 380", "LING 410", "LING 420", "LING 430"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Supply Chain Management BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="supply-chain-management-bs",
    major_name="Supply Chain Management (BS)",
    college="Marriott School of Business",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Economics", "required", ["ECON 110"], 1, also_satisfies_ge=[_GE_SOCIAL, _GE_AMERICAN_CIV]),
        MajorReqGroup("Business Math", "elective_group", ["MATH 110", "MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Business Statistics", "elective_group", ["STAT 121", "STAT 201"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Financial Accounting", "required", ["ACC 200"], 1),
        MajorReqGroup("Operations Management", "required", ["BUS M 471"], 1),
        MajorReqGroup("Supply Chain Fundamentals", "required", ["SCM 301"], 1),
        MajorReqGroup("Logistics", "required", ["SCM 310"], 1),
        MajorReqGroup("Procurement and Sourcing", "required", ["SCM 320"], 1),
        MajorReqGroup("Supply Chain Analytics", "required", ["SCM 410"], 1),
        MajorReqGroup("SCM Electives", "elective_group",
            ["SCM 330", "SCM 340", "SCM 420", "SCM 430", "SCM 440"],
            courses_needed=2),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Graphic Design BFA
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="graphic-design-bfa",
    major_name="Graphic Design (BFA)",
    college="College of Fine Arts and Communications",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Drawing Fundamentals", "required", ["ART 115"], 1, also_satisfies_ge=[_GE_ARTS]),
        MajorReqGroup("Art History", "required", ["ART 201"], 1, also_satisfies_ge=[_GE_ARTS, _GE_COMPARATIVE]),
        MajorReqGroup("Design Fundamentals I", "required", ["DESN 101"], 1),
        MajorReqGroup("Design Fundamentals II", "required", ["DESN 102"], 1),
        MajorReqGroup("Typography", "required", ["DESN 210"], 1),
        MajorReqGroup("Graphic Design I", "required", ["DESN 301"], 1),
        MajorReqGroup("Graphic Design II", "required", ["DESN 302"], 1),
        MajorReqGroup("Branding and Identity", "required", ["DESN 380"], 1),
        MajorReqGroup("Design Electives", "elective_group",
            ["DESN 310", "DESN 320", "DESN 330", "DESN 340", "DESN 410", "DESN 420"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Physics BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="physics-bs",
    major_name="Physics (BS)",
    college="Physical and Mathematical Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Calculus I", "required", ["MATH 112"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Calculus II", "required", ["MATH 113"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Multivariable Calculus", "required", ["MATH 213"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Differential Equations", "required", ["MATH 303"], 1),
        MajorReqGroup("Physics I (Mechanics)", "required", ["PHYS 121"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Physics II (E&M)", "required", ["PHYS 122"], 1),
        MajorReqGroup("Modern Physics", "required", ["PHYS 222"], 1),
        MajorReqGroup("Classical Mechanics", "required", ["PHYS 318"], 1),
        MajorReqGroup("Electricity and Magnetism", "required", ["PHYS 360"], 1),
        MajorReqGroup("Quantum Mechanics", "required", ["PHYS 451"], 1),
        MajorReqGroup("Thermal Physics", "required", ["PHYS 370"], 1),
        MajorReqGroup("Physics Electives", "elective_group",
            ["PHYS 340", "PHYS 420", "PHYS 430", "PHYS 441", "PHYS 461", "PHYS 471"],
            courses_needed=3),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Athletic Training BS
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="athletic-training-bs",
    major_name="Athletic Training (BS)",
    college="Life Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("Principles of Biology", "required", ["BIO 130"], 1, also_satisfies_ge=[_GE_LIFE_SCI]),
        MajorReqGroup("Chemistry", "elective_group", ["CHEM 101", "CHEM 105"], 1, also_satisfies_ge=[_GE_PHYS_SCI]),
        MajorReqGroup("Statistics", "elective_group", ["STAT 121", "STAT 201"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Human Anatomy", "required", ["EXSC 210"], 1),
        MajorReqGroup("Physiology", "required", ["EXSC 305"], 1),
        MajorReqGroup("Intro to Athletic Training", "required", ["AT 201"], 1),
        MajorReqGroup("Injury Evaluation I", "required", ["AT 301"], 1),
        MajorReqGroup("Injury Evaluation II", "required", ["AT 302"], 1),
        MajorReqGroup("Therapeutic Exercise", "required", ["AT 401"], 1),
        MajorReqGroup("Clinical Experience", "capstone", ["AT 491R"], 1),
    ],
))

# ─────────────────────────────────────────────────────────────────────────────
# Pre-Law (Political Science emphasis)
# ─────────────────────────────────────────────────────────────────────────────
_add(MajorDefinition(
    major_slug="pre-law-political-science",
    major_name="Pre-Law / Political Science (BS)",
    college="Family, Home, and Social Sciences",
    catalog_year="2024-2025",
    total_credits=120,
    groups=[
        MajorReqGroup("American Government", "required", ["POLI 200"], 1, also_satisfies_ge=[_GE_AMERICAN_CIV, _GE_SOCIAL]),
        MajorReqGroup("Introduction to Law", "required", ["POLI 215"], 1, also_satisfies_ge=[_GE_SOCIAL]),
        MajorReqGroup("Constitutional Law", "required", ["POLI 316"], 1),
        MajorReqGroup("Research Methods", "required", ["POLI 300"], 1),
        MajorReqGroup("Statistics", "required", ["STAT 121"], 1, also_satisfies_ge=[_GE_QUANTITATIVE]),
        MajorReqGroup("Political Theory", "required", ["POLI 310"], 1),
        MajorReqGroup("Writing for Law", "elective_group", ["WRTG 316", "WRTG 318"], 1, also_satisfies_ge=[_GE_ADV_WRITING]),
        MajorReqGroup("Pre-Law Electives", "elective_group",
            ["POLI 317", "POLI 318", "POLI 360", "POLI 410", "POLI 420", "BUS M 241"],
            courses_needed=4),
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
