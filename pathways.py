"""
BYU GE Flexible Requirement Pathways — Universal Solver
========================================================
Defines every alternative pathway for all 13 BYU GE categories and provides
a PathwaySolver that finds the globally cheapest completion for any student,
given their already-completed coursework.

Sources:
  https://catalog.byu.edu/student-handbook/general-education
  https://registrar.byu.edu/general-education
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


# ── Pathway definitions ───────────────────────────────────────────────────────
# Structure:
#   PATHWAYS[ge_category] = list of Pathway objects
#
# Each Pathway describes ONE way to satisfy that GE category:
#   id              – unique slug
#   description     – human-readable label shown in the UI
#   courses_needed  – how many courses from course_pool are required
#   credits_needed  – minimum total credit hours (used for Religion)
#   course_pool     – course codes that qualify; None means "any course in dept"
#   dept_prefix     – if course_pool is None, any course matching this prefix counts
#   also_satisfies  – other GE categories automatically satisfied by THIS pathway
#                     (e.g. AMER H 100 satisfies both American Heritage AND AmCiv)

@dataclass
class Pathway:
    id:             str
    description:    str
    courses_needed: int          = 1
    credits_needed: int          = 0   # 0 = not enforced; >0 = must also hit credit total
    course_pool:    List[str]    = field(default_factory=list)
    dept_prefix:    Optional[str] = None   # e.g. "REL" matches any REL xxx course
    also_satisfies: List[str]    = field(default_factory=list)

    def pool_set(self) -> Set[str]:
        return set(self.course_pool)

    def matches(self, course_code: str) -> bool:
        """Return True if course_code qualifies for this pathway."""
        if course_code in self.course_pool:
            return True
        if self.dept_prefix and course_code.startswith(self.dept_prefix):
            return True
        return False

    def courses_in_common(self, taken: Set[str]) -> Set[str]:
        """Return the subset of `taken` that count toward this pathway."""
        result = {c for c in taken if self.matches(c)}
        return result


PATHWAYS: Dict[str, List[Pathway]] = {

    # ── American Heritage ────────────────────────────────────────
    # BYU requires 3 credits of American Heritage.
    # Option A: AMER H 100 alone (it also satisfies American Civilization)
    # Option B: AMER H 200 alone
    "American Heritage": [
        Pathway(
            id="amheritage_100",
            description="AMER H 100 — also satisfies American Civilization",
            courses_needed=1,
            course_pool=["AMER H 100"],
            also_satisfies=["American Civilization"],
        ),
        Pathway(
            id="amheritage_200",
            description="AMER H 200 — Development of Western Civilization",
            courses_needed=1,
            course_pool=["AMER H 200"],
        ),
    ],

    # ── American Civilization ────────────────────────────────────
    # Option A: AMER H 100 alone (simultaneously satisfies American Heritage)
    # Option B: Any 2 qualifying social/history courses from the approved pool
    "American Civilization": [
        Pathway(
            id="amciv_heritage100",
            description="AMER H 100 alone — also satisfies American Heritage",
            courses_needed=1,
            course_pool=["AMER H 100"],
            also_satisfies=["American Heritage"],
        ),
        Pathway(
            id="amciv_two_course",
            description="Any 2 qualifying courses (e.g. ECON 110 + HIST 220)",
            courses_needed=2,
            course_pool=[
                "ECON 110", "POLI 110", "HIST 220", "HIST 221",
                "SOC 111", "PSYCH 111", "MFHD 210",
            ],
        ),
    ],

    # ── Religion ─────────────────────────────────────────────────
    # BYU requires 14 credit hours of religion (typically 7 × 2-credit courses).
    # Note: credits_needed is enforced in addition to courses_needed.
    "Religion": [
        Pathway(
            id="religion_14cr",
            description="14 total credit hours of BYU Religion courses (7 × 2-credit courses)",
            courses_needed=7,
            credits_needed=14,
            dept_prefix="REL",         # any REL xxx course qualifies
            course_pool=[
                "REL A 121", "REL A 122", "REL A 211", "REL A 212",
                "REL C 225", "REL A 250", "REL A 275", "REL A 301",
                "REL A 302", "REL C 300", "REL C 333", "REL E 341",
                "REL A 341", "REL C 350",
            ],
        ),
    ],

    # ── First-Year Writing ───────────────────────────────────────
    # Satisfied by WRTG 150 or an approved equivalent / transfer course.
    "First-Year Writing": [
        Pathway(
            id="fyw_150",
            description="WRTG 150 — Writing and Rhetoric (or approved transfer equivalent)",
            courses_needed=1,
            course_pool=["WRTG 150", "WRTG 150H", "ENG 150"],
        ),
    ],

    # ── Advanced Written and Oral Communication ──────────────────
    # One approved upper-division writing or communication course.
    # Option A: Upper-division writing courses
    # Option B: Speech/communication courses
    "Advanced Written and Oral Communication": [
        Pathway(
            id="awoc_writing",
            description="Any approved upper-division writing course",
            courses_needed=1,
            course_pool=[
                "WRTG 316", "WRTG 320", "WRTG 330", "WRTG 340",
                "WRTG 410", "WRTG 420",
            ],
        ),
        Pathway(
            id="awoc_comm",
            description="Approved oral communication / public speaking course",
            courses_needed=1,
            course_pool=[
                "COMM 101", "COMM 310", "COMM 318",
                "BUS M 341", "ENGL 315",
            ],
        ),
    ],

    # ── Languages of Learning (Quantitative) ─────────────────────
    # One approved quantitative reasoning or computer programming course.
    # Option A: Mathematics
    # Option B: Statistics
    # Option C: Computer Science (programming counts at BYU)
    "Languages of Learning (Quantitative)": [
        Pathway(
            id="lol_math",
            description="Approved mathematics course (College Algebra or higher)",
            courses_needed=1,
            course_pool=[
                "MATH 110", "MATH 112", "MATH 113", "MATH 119",
                "MATH 213", "MATH 290",
            ],
        ),
        Pathway(
            id="lol_stats",
            description="Approved statistics course",
            courses_needed=1,
            course_pool=["STAT 121", "STAT 221", "STAT 230"],
        ),
        Pathway(
            id="lol_cs",
            description="Approved computer science / programming course",
            courses_needed=1,
            course_pool=["CS 110", "CS 142", "IT 201"],
        ),
    ],

    # ── Arts ─────────────────────────────────────────────────────
    # One approved Arts distribution course.
    # Option A: Standard arts course (visual art, music, theatre, dance)
    # Option B: ART 201 — double-dips with Comparative Civilization
    "Arts": [
        Pathway(
            id="arts_standard",
            description="Any approved Arts course (visual arts, music, theatre, dance)",
            courses_needed=1,
            course_pool=[
                "ART 100", "MUSIC 101", "THEATRE 101", "DANCE 180",
                "MUSIC 202", "ART 100R",
            ],
        ),
        Pathway(
            id="arts_art201",
            description="ART 201 — Art History Survey I (also satisfies Comparative Civilization)",
            courses_needed=1,
            course_pool=["ART 201"],
            also_satisfies=["Comparative Civilization"],
        ),
    ],

    # ── Letters ──────────────────────────────────────────────────
    # One approved Letters distribution course.
    # Option A: Standard literature/philosophy
    # Option B: HIST 201 or ENGL 340 — double-dip with Global/Cultural Awareness
    "Letters": [
        Pathway(
            id="letters_standard",
            description="Any approved Letters course (literature, philosophy, history)",
            courses_needed=1,
            course_pool=["ENGL 251", "ENGL 292", "PHIL 201", "PHIL 101"],
        ),
        Pathway(
            id="letters_hist201",
            description="HIST 201 — World History to 1500 (also satisfies Global/Cultural Awareness)",
            courses_needed=1,
            course_pool=["HIST 201"],
            also_satisfies=["Global and Cultural Awareness"],
        ),
        Pathway(
            id="letters_engl340",
            description="ENGL 340 — Survey of World Literature (also satisfies Global/Cultural Awareness)",
            courses_needed=1,
            course_pool=["ENGL 340"],
            also_satisfies=["Global and Cultural Awareness"],
        ),
    ],

    # ── Life Sciences ─────────────────────────────────────────────
    # One approved Life Sciences course.
    # Option A: Biology courses
    # Option B: Human biology / health sciences
    # Option C: Nutrition & food science
    "Scientific Principles and Reasoning (Life Sciences)": [
        Pathway(
            id="lifesci_bio",
            description="Approved biology course",
            courses_needed=1,
            course_pool=["BIO 100", "BIO 130", "MMBIO 101"],
        ),
        Pathway(
            id="lifesci_humanbio",
            description="Human biology or anatomy/physiology",
            courses_needed=1,
            course_pool=["PDBIO 120", "PDBIO 220", "HLTH 100"],
        ),
        Pathway(
            id="lifesci_nutrition",
            description="Nutrition and food science",
            courses_needed=1,
            course_pool=["NDFS 100", "NDFS 101"],
        ),
    ],

    # ── Physical Sciences ─────────────────────────────────────────
    # One approved Physical Sciences course.
    # Option A: Chemistry
    # Option B: Physics / astronomy
    # Option C: Earth sciences (geology)
    "Scientific Principles and Reasoning (Physical Sciences)": [
        Pathway(
            id="physci_chem",
            description="Approved chemistry course",
            courses_needed=1,
            course_pool=["CHEM 101", "CHEM 105", "CHEM 106"],
        ),
        Pathway(
            id="physci_physics",
            description="Physics or astronomy",
            courses_needed=1,
            course_pool=["PHSCS 100", "PHSCS 105", "PHSCS 106"],
        ),
        Pathway(
            id="physci_earth",
            description="Earth sciences (geology, geography)",
            courses_needed=1,
            course_pool=["GEOL 101", "GEOG 111"],
        ),
    ],

    # ── Social and Behavioral Sciences ───────────────────────────
    # One approved SBS course.
    # Multiple options, several of which also satisfy American Civilization
    # or Global/Cultural Awareness.
    "Social and Behavioral Sciences": [
        Pathway(
            id="sbs_psych",
            description="Psychology — Introduction to Psychology",
            courses_needed=1,
            course_pool=["PSYCH 111"],
        ),
        Pathway(
            id="sbs_soc",
            description="Sociology — Introduction to Sociology",
            courses_needed=1,
            course_pool=["SOC 111"],
        ),
        Pathway(
            id="sbs_econ",
            description="ECON 110 — also satisfies American Civilization",
            courses_needed=1,
            course_pool=["ECON 110"],
            also_satisfies=["American Civilization"],
        ),
        Pathway(
            id="sbs_poli",
            description="POLI 110 — also satisfies American Civilization",
            courses_needed=1,
            course_pool=["POLI 110"],
            also_satisfies=["American Civilization"],
        ),
        Pathway(
            id="sbs_anthr",
            description="ANTHR 101 — also satisfies Global and Cultural Awareness",
            courses_needed=1,
            course_pool=["ANTHR 101"],
            also_satisfies=["Global and Cultural Awareness"],
        ),
        Pathway(
            id="sbs_family",
            description="MFHD 210 — Foundations of Family Life",
            courses_needed=1,
            course_pool=["MFHD 210"],
        ),
    ],

    # ── Global and Cultural Awareness ────────────────────────────
    # One approved Global/Cultural Awareness course.
    # Many options; several also satisfy Comparative Civilization or Letters.
    "Global and Cultural Awareness": [
        Pathway(
            id="global_geog",
            description="GEOG 101 — World Regional Geography",
            courses_needed=1,
            course_pool=["GEOG 101"],
        ),
        Pathway(
            id="global_anthr",
            description="ANTHR 101 — also satisfies Social/Behavioral Sciences",
            courses_needed=1,
            course_pool=["ANTHR 101"],
            also_satisfies=["Social and Behavioral Sciences"],
        ),
        Pathway(
            id="global_hist201",
            description="HIST 201 — also satisfies Letters",
            courses_needed=1,
            course_pool=["HIST 201"],
            also_satisfies=["Letters"],
        ),
        Pathway(
            id="global_engl340",
            description="ENGL 340 — also satisfies Letters",
            courses_needed=1,
            course_pool=["ENGL 340"],
            also_satisfies=["Letters"],
        ),
        Pathway(
            id="global_hist202",
            description="HIST 202 — also satisfies Comparative Civilization",
            courses_needed=1,
            course_pool=["HIST 202"],
            also_satisfies=["Comparative Civilization"],
        ),
        Pathway(
            id="global_phil202",
            description="PHIL 202 — World Religions, also satisfies Comparative Civilization",
            courses_needed=1,
            course_pool=["PHIL 202"],
            also_satisfies=["Comparative Civilization"],
        ),
        Pathway(
            id="global_asian",
            description="ASIAN 101 — also satisfies Comparative Civilization",
            courses_needed=1,
            course_pool=["ASIAN 101"],
            also_satisfies=["Comparative Civilization"],
        ),
        Pathway(
            id="global_latin",
            description="LATIN 101 — also satisfies Comparative Civilization",
            courses_needed=1,
            course_pool=["LATIN 101"],
            also_satisfies=["Comparative Civilization"],
        ),
    ],

    # ── Comparative Civilization ──────────────────────────────────
    # One approved Comparative Civilization course.
    # Most options also satisfy Global/Cultural Awareness.
    "Comparative Civilization": [
        Pathway(
            id="compciv_art201",
            description="ART 201 — also satisfies Arts",
            courses_needed=1,
            course_pool=["ART 201"],
            also_satisfies=["Arts"],
        ),
        Pathway(
            id="compciv_hist202",
            description="HIST 202 — also satisfies Global and Cultural Awareness",
            courses_needed=1,
            course_pool=["HIST 202"],
            also_satisfies=["Global and Cultural Awareness"],
        ),
        Pathway(
            id="compciv_phil202",
            description="PHIL 202 — also satisfies Global and Cultural Awareness",
            courses_needed=1,
            course_pool=["PHIL 202"],
            also_satisfies=["Global and Cultural Awareness"],
        ),
        Pathway(
            id="compciv_asian",
            description="ASIAN 101 — also satisfies Global and Cultural Awareness",
            courses_needed=1,
            course_pool=["ASIAN 101"],
            also_satisfies=["Global and Cultural Awareness"],
        ),
        Pathway(
            id="compciv_latin",
            description="LATIN 101 — also satisfies Global and Cultural Awareness",
            courses_needed=1,
            course_pool=["LATIN 101"],
            also_satisfies=["Global and Cultural Awareness"],
        ),
    ],
}


# ── PathwayResult dataclass ────────────────────────────────────────────────────

@dataclass
class PathwayResult:
    category:          str
    pathway:           Pathway
    already_taken:     List[str]      # courses from pool already completed
    courses_remaining: int            # additional courses still needed
    credits_remaining: int            # additional credits still needed (Religion)
    also_satisfies:    List[str]      # bonus categories satisfied for free
    is_complete:       bool

    @property
    def description(self) -> str:
        return self.pathway.description


# ── SolveResult dataclass ─────────────────────────────────────────────────────

@dataclass
class SolveResult:
    completed:    Set[str]                      # categories already fully satisfied
    partial:      Dict[str, PathwayResult]      # started but not yet complete
    not_started:  Set[str]                      # no progress at all
    recommendations: Dict[str, PathwayResult]  # cheapest pathway per remaining category

    @property
    def remaining_categories(self) -> Set[str]:
        return set(self.partial.keys()) | self.not_started


# ── Core evaluator ────────────────────────────────────────────────────────────

def evaluate_pathways(category: str, courses_taken: Set[str]) -> Optional[PathwayResult]:
    """
    Given a GE category and the set of courses a student has already taken,
    return the PathwayResult for the CHEAPEST pathway to complete that category.

    Cheapest = (fewest courses remaining, then most already taken, then most bonus satisfies).
    Returns None if no pathways are defined for the category.
    """
    pathways = PATHWAYS.get(category, [])
    if not pathways:
        return None

    best: Optional[PathwayResult] = None

    for pathway in pathways:
        taken_from_pool = pathway.courses_in_common(courses_taken)
        courses_remaining = max(0, pathway.courses_needed - len(taken_from_pool))

        # Credit check for Religion (and any future credit-gated pathway)
        credits_remaining = 0
        if pathway.credits_needed > 0:
            # Assume all religion courses are 2 credits each for now
            credits_earned = len(taken_from_pool) * 2
            credits_remaining = max(0, pathway.credits_needed - credits_earned)
            # Reconcile: take the max of course-based and credit-based remaining
            courses_from_credits = max(0, credits_remaining // 2)
            courses_remaining = max(courses_remaining, courses_from_credits)

        is_complete = (courses_remaining == 0)

        result = PathwayResult(
            category=category,
            pathway=pathway,
            already_taken=sorted(taken_from_pool),
            courses_remaining=courses_remaining,
            credits_remaining=credits_remaining,
            also_satisfies=pathway.also_satisfies,
            is_complete=is_complete,
        )

        # Score: (fewer remaining = better) → (more already taken = better) → (more bonuses = better)
        def score(r: PathwayResult):
            return (
                r.courses_remaining,
                -len(r.already_taken),
                -len(r.also_satisfies),
            )

        if best is None or score(result) < score(best):
            best = result

    return best


# ── Universal PathwaySolver ───────────────────────────────────────────────────

class PathwaySolver:
    """
    Evaluates ALL 13 GE categories simultaneously for a given student,
    finds the cheapest pathway for each, cascades also_satisfies bonuses,
    and returns a unified SolveResult.

    This is the single source of truth used by both the optimizer and the UI.
    """

    def solve(
        self,
        courses_taken: Set[str],
        manually_completed: Optional[Set[str]] = None,
    ) -> SolveResult:
        """
        Parameters
        ----------
        courses_taken       : set of course codes the student has completed
        manually_completed  : optional set of categories the user checked off manually

        Returns
        -------
        SolveResult with completed / partial / not_started / recommendations
        """
        courses_taken     = set(courses_taken or [])
        manually_completed = set(manually_completed or [])

        completed:    Set[str]                   = set(manually_completed)
        partial:      Dict[str, PathwayResult]   = {}
        not_started:  Set[str]                   = set()
        recommendations: Dict[str, PathwayResult] = {}

        # ── Pass 1: evaluate every category ─────────────────────
        for category in PATHWAYS:
            if category in completed:
                continue

            result = evaluate_pathways(category, courses_taken)
            if result is None:
                not_started.add(category)
                continue

            if result.is_complete:
                completed.add(category)
                # Cascade: mark also_satisfies as complete too
                for bonus in result.also_satisfies:
                    completed.add(bonus)
            elif result.already_taken:
                partial[category] = result
                recommendations[category] = result
            else:
                not_started.add(category)
                recommendations[category] = result

        # ── Pass 2: propagate cascades (repeat until stable) ────
        changed = True
        while changed:
            changed = False
            for cat in list(partial.keys()) + list(not_started):
                if cat in completed:
                    if cat in partial:
                        del partial[cat]
                        changed = True
                    not_started.discard(cat)

        # ── Pass 3: for not_started, find cheapest pathway ──────
        for category in not_started:
            if category not in recommendations:
                result = evaluate_pathways(category, courses_taken)
                if result:
                    recommendations[category] = result

        # ── Pass 4: prefer pathways with also_satisfies that cover remaining ──
        # Re-score recommendations so pathways that cover TWO remaining
        # categories rank above equal-cost pathways that cover only one.
        remaining = (set(partial.keys()) | not_started) - completed
        for category in list(remaining):
            result = evaluate_pathways(category, courses_taken)
            if not result:
                continue

            # Try to find a pathway that also covers another REMAINING category
            best_with_bonus = None
            for pathway in PATHWAYS.get(category, []):
                taken_from_pool = pathway.courses_in_common(courses_taken)
                courses_remaining = max(0, pathway.courses_needed - len(taken_from_pool))
                bonus_remaining = [b for b in pathway.also_satisfies if b in remaining and b != category]

                if courses_remaining > result.courses_remaining:
                    continue  # strictly worse, skip

                if bonus_remaining:
                    candidate = PathwayResult(
                        category=category,
                        pathway=pathway,
                        already_taken=sorted(taken_from_pool),
                        courses_remaining=courses_remaining,
                        credits_remaining=0,
                        also_satisfies=pathway.also_satisfies,
                        is_complete=(courses_remaining == 0),
                    )
                    if best_with_bonus is None or courses_remaining < best_with_bonus.courses_remaining:
                        best_with_bonus = candidate

            if best_with_bonus is not None:
                recommendations[category] = best_with_bonus

        return SolveResult(
            completed=completed,
            partial={k: v for k, v in partial.items() if k not in completed},
            not_started=not_started - completed,
            recommendations={k: v for k, v in recommendations.items() if k not in completed},
        )


# ── Module-level convenience functions (backward-compatible) ──────────────────

_solver = PathwaySolver()


def get_remaining_requirements(
    courses_taken: Set[str],
    manually_completed: Optional[Set[str]] = None,
) -> dict:
    """
    Backward-compatible wrapper around PathwaySolver.solve().
    Returns dict with keys: completed, partial, not_started.
    """
    result = _solver.solve(courses_taken, manually_completed)
    return {
        "completed":   result.completed,
        "partial":     result.partial,
        "not_started": result.not_started,
    }


def evaluate_pathway_compat(category: str, courses_taken: Set[str]) -> Optional[dict]:
    """
    Backward-compatible wrapper: returns a plain dict instead of PathwayResult.
    Used by optimizer.py's cheapest_completion_hint.
    """
    r = evaluate_pathways(category, courses_taken)
    if r is None:
        return None
    return {
        "pathway":           r.pathway.__dict__,
        "already_taken":     r.already_taken,
        "courses_remaining": r.courses_remaining,
        "also_satisfies":    r.also_satisfies,
        "is_complete":       r.is_complete,
    }


def cheapest_completion_hint(category: str, courses_taken: Set[str], all_courses: list) -> list:
    """
    For a partially-completed requirement, return the specific course dicts
    from all_courses that would cheapest-finish the best pathway.
    """
    result = evaluate_pathways(category, courses_taken)
    if not result:
        return []

    pool    = result.pathway.pool_set()
    taken   = set(result.already_taken)
    needed  = pool - taken

    return [c for c in all_courses if c["course_code"] in needed]


def build_pathway_aware_requirements(
    courses_taken: Set[str],
    manually_completed: Optional[Set[str]] = None,
) -> Set[str]:
    """
    Return the set of GE categories still needing work.
    Passed to the optimizer as remaining_requirements.
    """
    state = get_remaining_requirements(courses_taken, manually_completed)
    return set(state["partial"].keys()) | state["not_started"]
