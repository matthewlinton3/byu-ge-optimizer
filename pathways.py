"""
BYU GE Flexible Requirement Pathways
Defines alternative ways to satisfy each GE requirement and picks the cheapest
path given courses the user has already completed.

Sources: https://catalog.byu.edu/student-handbook/general-education
"""

# ── Pathway definitions ───────────────────────────────────────────────────────
# Each GE category can have one or more alternative pathways.
# A pathway is satisfied when its `courses_needed` courses from `course_pool`
# have been taken (or `credits_needed` credits accumulated).
#
# Fields:
#   id              - unique identifier
#   description     - human-readable label
#   courses_needed  - how many courses from pool are required (default 1)
#   credits_needed  - total credit hours needed (for Religion)
#   course_pool     - list of course codes that qualify, OR "any_<dept>" pattern
#   also_satisfies  - other GE categories this pathway simultaneously satisfies

PATHWAYS = {

    # ── American Heritage ────────────────────────────────────────
    "American Heritage": [
        {
            "id": "amheritage_100",
            "description": "AMER H 100 (also satisfies American Civilization)",
            "courses_needed": 1,
            "course_pool": ["AMER H 100"],
            "also_satisfies": ["American Civilization"],
        },
        {
            "id": "amheritage_200",
            "description": "AMER H 200 alone",
            "courses_needed": 1,
            "course_pool": ["AMER H 200"],
            "also_satisfies": [],
        },
    ],

    # ── American Civilization ────────────────────────────────────
    # Pathway A: AMER H 100 alone (also satisfies American Heritage)
    # Pathway B: Any two courses from the qualifying pool
    "American Civilization": [
        {
            "id": "amciv_heritage",
            "description": "AMER H 100 alone (also satisfies American Heritage — best double-dipper)",
            "courses_needed": 1,
            "course_pool": ["AMER H 100"],
            "also_satisfies": ["American Heritage"],
        },
        {
            "id": "amciv_two_course",
            "description": "Two qualifying courses (e.g., ECON 110 + HIST 220)",
            "courses_needed": 2,
            "course_pool": [
                "ECON 110", "POLI 110", "HIST 220", "HIST 221",
                "SOC 111", "PSYCH 111",
            ],
            "also_satisfies": [],
        },
    ],

    # ── Religion ─────────────────────────────────────────────────
    # BYU requires 14 credit hours of religion — typically 7 × 2-credit courses
    "Religion": [
        {
            "id": "religion_credits",
            "description": "14 total credits of BYU Religion courses (typically 7 courses × 2 credits)",
            "courses_needed": 7,   # 7 × 2 credit = 14 credits
            "credits_needed": 14,
            "course_pool": [
                "REL A 121", "REL A 122", "REL A 211", "REL A 212",
                "REL C 225", "REL A 250", "REL A 275", "REL A 301",
                "REL A 302", "REL C 300", "REL C 333", "REL E 341",
            ],
            "also_satisfies": [],
        },
    ],

    # ── First-Year Writing ───────────────────────────────────────
    "First-Year Writing": [
        {
            "id": "writing_150",
            "description": "WRTG 150 (or equivalent transfer credit)",
            "courses_needed": 1,
            "course_pool": ["WRTG 150", "WRTG 150H"],
            "also_satisfies": [],
        },
    ],

    # ── Advanced Written and Oral Communication ──────────────────
    "Advanced Written and Oral Communication": [
        {
            "id": "awoc_writing",
            "description": "Any approved upper-division writing course",
            "courses_needed": 1,
            "course_pool": [
                "WRTG 316", "WRTG 320", "WRTG 330", "WRTG 340",
                "COMM 101", "COMM 310",
            ],
            "also_satisfies": [],
        },
    ],

    # ── Languages of Learning (Quantitative) ────────────────────
    "Languages of Learning (Quantitative)": [
        {
            "id": "lol_math",
            "description": "Any approved quantitative reasoning course",
            "courses_needed": 1,
            "course_pool": [
                "MATH 110", "MATH 112", "MATH 113", "MATH 119",
                "MATH 213", "STAT 121", "STAT 221", "CS 142",
            ],
            "also_satisfies": [],
        },
    ],

    # ── Arts ─────────────────────────────────────────────────────
    "Arts": [
        {
            "id": "arts_standard",
            "description": "One approved Arts distribution course",
            "courses_needed": 1,
            "course_pool": [
                "ART 100", "ART 201", "MUSIC 101", "THEATRE 101",
                "DANCE 180", "MUSIC 202",
            ],
            "also_satisfies": [],
        },
        {
            "id": "arts_double_dip",
            "description": "ART 201 (also satisfies Comparative Civilization)",
            "courses_needed": 1,
            "course_pool": ["ART 201"],
            "also_satisfies": ["Comparative Civilization"],
        },
    ],

    # ── Letters ──────────────────────────────────────────────────
    "Letters": [
        {
            "id": "letters_standard",
            "description": "One approved Letters distribution course",
            "courses_needed": 1,
            "course_pool": [
                "ENGL 251", "ENGL 292", "PHIL 201",
                "HIST 201", "ENGL 340",
            ],
            "also_satisfies": [],
        },
        {
            "id": "letters_global_double",
            "description": "HIST 201 or ENGL 340 (also satisfies Global/Cultural Awareness)",
            "courses_needed": 1,
            "course_pool": ["HIST 201", "ENGL 340"],
            "also_satisfies": ["Global and Cultural Awareness"],
        },
    ],

    # ── Life Sciences ─────────────────────────────────────────────
    "Scientific Principles and Reasoning (Life Sciences)": [
        {
            "id": "lifesci_standard",
            "description": "One approved Life Sciences course",
            "courses_needed": 1,
            "course_pool": [
                "BIO 100", "BIO 130", "PDBIO 120",
                "MMBIO 101", "NDFS 100",
            ],
            "also_satisfies": [],
        },
    ],

    # ── Physical Sciences ─────────────────────────────────────────
    "Scientific Principles and Reasoning (Physical Sciences)": [
        {
            "id": "physci_standard",
            "description": "One approved Physical Sciences course",
            "courses_needed": 1,
            "course_pool": [
                "CHEM 101", "PHSCS 100", "GEOL 101",
                "PHSCS 105", "CHEM 105",
            ],
            "also_satisfies": [],
        },
    ],

    # ── Social and Behavioral Sciences ───────────────────────────
    "Social and Behavioral Sciences": [
        {
            "id": "sbs_standard",
            "description": "One approved Social/Behavioral Sciences course",
            "courses_needed": 1,
            "course_pool": [
                "PSYCH 111", "SOC 111", "ECON 110", "POLI 110",
                "ANTHR 101", "MFHD 210", "COMMS 101",
            ],
            "also_satisfies": [],
        },
        {
            "id": "sbs_econ_double",
            "description": "ECON 110 (also satisfies American Civilization)",
            "courses_needed": 1,
            "course_pool": ["ECON 110"],
            "also_satisfies": ["American Civilization"],
        },
        {
            "id": "sbs_poli_double",
            "description": "POLI 110 (also satisfies American Civilization)",
            "courses_needed": 1,
            "course_pool": ["POLI 110"],
            "also_satisfies": ["American Civilization"],
        },
        {
            "id": "sbs_anthr_double",
            "description": "ANTHR 101 (also satisfies Global/Cultural Awareness)",
            "courses_needed": 1,
            "course_pool": ["ANTHR 101"],
            "also_satisfies": ["Global and Cultural Awareness"],
        },
    ],

    # ── Global and Cultural Awareness ────────────────────────────
    "Global and Cultural Awareness": [
        {
            "id": "global_standard",
            "description": "One approved Global/Cultural Awareness course",
            "courses_needed": 1,
            "course_pool": [
                "GEOG 101", "HIST 201", "HIST 202",
                "ANTHR 101", "ENGL 340", "PHIL 202",
                "ASIAN 101", "LATIN 101",
            ],
            "also_satisfies": [],
        },
    ],

    # ── Comparative Civilization ──────────────────────────────────
    "Comparative Civilization": [
        {
            "id": "compciv_standard",
            "description": "One approved Comparative Civilization course",
            "courses_needed": 1,
            "course_pool": [
                "ART 201", "HIST 202", "PHIL 202",
                "ASIAN 101", "LATIN 101",
            ],
            "also_satisfies": [],
        },
        {
            "id": "compciv_global_double",
            "description": "HIST 202 / PHIL 202 / ASIAN 101 / LATIN 101 (also satisfies Global/Cultural Awareness)",
            "courses_needed": 1,
            "course_pool": ["HIST 202", "PHIL 202", "ASIAN 101", "LATIN 101"],
            "also_satisfies": ["Global and Cultural Awareness"],
        },
    ],
}


# ── Pathway evaluator ─────────────────────────────────────────────────────────

def evaluate_pathways(ge_category: str, courses_taken: set) -> dict:
    """
    Given a GE category and the set of courses a user has already taken,
    return the cheapest pathway to complete that requirement.

    Returns a dict:
        {
            "pathway": <pathway dict>,
            "already_taken": [list of qualifying courses already done],
            "still_needed": [list of courses still needed],
            "courses_remaining": int,
            "also_satisfies": [list of other GE categories this completes],
            "is_complete": bool,
        }
    """
    all_pathways = PATHWAYS.get(ge_category, [])
    if not all_pathways:
        return None

    best = None
    for pathway in all_pathways:
        pool = set(pathway.get("course_pool", []))
        already = pool & courses_taken
        needed  = pathway.get("courses_needed", 1)
        remaining_count = max(0, needed - len(already))

        result = {
            "pathway":          pathway,
            "already_taken":    sorted(already),
            "still_needed_count": remaining_count,
            "courses_remaining": remaining_count,
            "also_satisfies":   pathway.get("also_satisfies", []),
            "is_complete":      remaining_count == 0,
        }

        # Pick best pathway by: (1) fewest remaining, (2) most already taken
        # (captures partial progress), (3) most also_satisfies (maximises free bonuses)
        def score(r):
            return (
                r["courses_remaining"],       # lower = better
                -len(r["already_taken"]),     # more progress = better
                -len(r["also_satisfies"]),    # more bonuses = better
            )

        if best is None or score(result) < score(best):
            best = result

    return best


def get_remaining_requirements(courses_taken: set, manually_completed: set = None) -> dict:
    """
    Given the full set of courses a student has already taken (course codes),
    compute which GE categories are:
      - fully complete
      - partially started (and which pathway is cheapest to finish)
      - not started

    Also detects cross-category benefits: e.g. if ECON 110 is taken,
    American Civilization is partially satisfied via the two-course pathway.

    Returns:
        {
            "completed":  set of category names fully done
            "partial":    { category: pathway_result } for in-progress requirements
            "not_started": set of category names with no progress
            "pathway_bonuses": { category: [also_satisfies list] }
                              categories that will be auto-satisfied when another is completed
        }
    """
    if manually_completed is None:
        manually_completed = set()

    completed   = set(manually_completed)
    partial     = {}
    not_started = set()

    for category in PATHWAYS:
        if category in completed:
            continue

        result = evaluate_pathways(category, courses_taken)
        if result is None:
            not_started.add(category)
            continue

        if result["is_complete"]:
            completed.add(category)
            # Also mark any bonus categories this satisfies
            for bonus in result["also_satisfies"]:
                completed.add(bonus)
        elif result["already_taken"]:
            partial[category] = result
        else:
            not_started.add(category)

    # Re-check: anything in partial/not_started that is now in completed?
    partial     = {k: v for k, v in partial.items() if k not in completed}
    not_started = not_started - completed

    return {
        "completed":   completed,
        "partial":     partial,
        "not_started": not_started,
    }


def build_pathway_aware_requirements(courses_taken: set, manually_completed: set = None) -> set:
    """
    Returns the set of GE categories that still need work
    (partial + not_started), excluding already-completed ones.
    This is passed to the optimizer as `remaining_requirements`.
    """
    state = get_remaining_requirements(courses_taken, manually_completed)
    return state["partial"].keys() | state["not_started"]


def cheapest_completion_hint(category: str, courses_taken: set, all_courses: list) -> list:
    """
    For a partially-completed requirement, return the specific course codes
    that would most cheaply finish it (used to guide the optimizer).
    """
    result = evaluate_pathways(category, courses_taken)
    if not result:
        return []

    pool      = set(result["pathway"].get("course_pool", []))
    taken     = set(result["already_taken"])
    remaining = pool - taken

    # Match remaining pool courses against the full course database
    matching = [c for c in all_courses if c["course_code"] in remaining]
    return matching
