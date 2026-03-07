"""
BYU GE Optimizer
Uses greedy set-cover + PuLP ILP to find the fewest courses that fulfill all GE requirements.
Supports flexible/alternative pathways and partial completion detection.
"""

from scraper import GE_CATEGORIES
from pathways import get_remaining_requirements, cheapest_completion_hint

try:
    import pulp
    HAS_PULP = True
except ImportError:
    HAS_PULP = False
    print("[warn] PuLP not installed. Falling back to greedy algorithm.")


def greedy_set_cover(courses, requirements):
    """
    Greedy set cover: repeatedly pick the course that covers the most
    uncovered requirements, tiebreak by highest professor rating.
    """
    uncovered = set(requirements.keys())
    selected = []
    remaining = list(courses)

    while uncovered and remaining:
        # Score each course by how many uncovered categories it hits
        best = max(
            remaining,
            key=lambda c: (
                len(set(c["ge_categories"]) & uncovered),
                c.get("rmp_rating", 0),
                -c.get("credit_hours", 3),
            )
        )

        newly_covered = set(best["ge_categories"]) & uncovered
        if not newly_covered:
            break  # No more coverage possible

        selected.append(best)
        uncovered -= newly_covered
        remaining.remove(best)

    return selected, uncovered


def ilp_set_cover(courses, requirements):
    """
    Integer Linear Programming set cover using PuLP.
    Minimizes total courses while covering all GE categories.
    """
    prob = pulp.LpProblem("BYU_GE_Optimizer", pulp.LpMinimize)

    # Binary variable for each course: 1 = take it, 0 = don't
    x = {
        c["course_code"]: pulp.LpVariable(f"x_{c['course_code'].replace(' ', '_')}", cat="Binary")
        for c in courses
    }

    # Objective: minimize total courses taken (weighted by fewer categories = less value)
    prob += pulp.lpSum(x[c["course_code"]] for c in courses)

    # Constraints: each GE category must be covered by at least one selected course
    for category in requirements:
        covering_courses = [c for c in courses if category in c["ge_categories"]]
        if covering_courses:
            prob += pulp.lpSum(x[c["course_code"]] for c in covering_courses) >= 1

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    selected = [c for c in courses if pulp.value(x[c["course_code"]]) == 1]

    # Find uncovered (categories with no courses offering them)
    covered = set()
    for c in selected:
        covered.update(c["ge_categories"])
    uncovered = set(requirements.keys()) - covered

    return selected, uncovered


def optimize(courses, use_ilp=True, remaining_requirements=None, courses_taken=None):
    """
    Run optimization. Returns (selected_courses, uncovered_categories).

    Args:
        courses: list of course dicts from the scraper
        use_ilp: use PuLP ILP solver if True, greedy if False
        remaining_requirements: optional set/dict of category names to optimize for.
            If None, optimizes for ALL GE categories.
        courses_taken: optional set of course codes the student has already completed.
            Used for pathway-aware optimization — e.g. if ECON 110 is taken,
            only ONE more AmCiv course is needed instead of AMER H 100.
    """
    # ── Resolve requirements ──────────────────────────────────────
    if remaining_requirements is None and courses_taken:
        # Use pathway-aware engine to figure out what's still needed
        pathway_state = get_remaining_requirements(courses_taken)
        remaining_cats = set(pathway_state["partial"].keys()) | set(pathway_state["not_started"])
        requirements   = {k: v for k, v in GE_CATEGORIES.items() if k in remaining_cats}

        # For partial requirements, boost the specific courses that finish them cheapest
        _partial_hints = {}
        for cat, state in pathway_state["partial"].items():
            hints = cheapest_completion_hint(cat, courses_taken, courses)
            if hints:
                _partial_hints[cat] = {c["course_code"] for c in hints}

    elif remaining_requirements is None:
        requirements   = GE_CATEGORIES
        _partial_hints = {}
    elif isinstance(remaining_requirements, set):
        requirements   = {k: v for k, v in GE_CATEGORIES.items() if k in remaining_requirements}
        _partial_hints = {}
    else:
        requirements   = remaining_requirements
        _partial_hints = {}

    if not requirements:
        return [], set()

    # ── Strip already-completed categories from each course's tag list ──
    # This prevents the ILP from choosing AMER H 100 just because it also tags
    # "American Civilization" when AmCiv is already done — making it falsely
    # look like a better double-dipper than AMER H 200.
    remaining_cat_set = set(requirements.keys())
    ge_courses = []
    for c in courses:
        cats = [cat for cat in c.get("ge_categories", []) if cat in remaining_cat_set]
        if cats:
            pruned = dict(c)
            pruned["ge_categories"] = cats
            ge_courses.append(pruned)

    if not ge_courses:
        return [], set(requirements.keys())

    # ── Boost courses that complete partial pathways ───────────────
    # Give these courses a synthetic head-start in the ILP/greedy by
    # adding a virtual extra GE category "__partial_boost" so they rank higher.
    if _partial_hints:
        for course in ge_courses:
            code = course["course_code"]
            for cat, hint_codes in _partial_hints.items():
                if code in hint_codes and "__partial_boost" not in course["ge_categories"]:
                    course = dict(course)  # don't mutate original
                    course["ge_categories"] = course["ge_categories"] + ["__partial_boost"]
                    break

    if use_ilp and HAS_PULP:
        print("[optimizer] Running pathway-aware ILP optimization (PuLP)...")
        selected, uncovered = ilp_set_cover(ge_courses, requirements)
    else:
        print("[optimizer] Running pathway-aware greedy set-cover optimization...")
        selected, uncovered = greedy_set_cover(ge_courses, requirements)

    # Remove the synthetic boost tag before returning
    for c in selected:
        c["ge_categories"] = [cat for cat in c.get("ge_categories", []) if cat != "__partial_boost"]

    # Sort: most GE categories covered first, then by RMP rating
    selected.sort(key=lambda c: (
        -len(c.get("ge_categories", [])),
        -c.get("rmp_rating", 0),
    ))

    return selected, uncovered
