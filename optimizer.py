"""
BYU GE Optimizer
Uses greedy set-cover + PuLP ILP to find the fewest courses that fulfill all GE requirements.
Uses PathwaySolver for universal, cross-category pathway-aware optimization.
"""

from scraper import GE_CATEGORIES
from pathways import PathwaySolver, cheapest_completion_hint
from ge_requirements import GE_REQUIREMENTS, is_category_complete

try:
    import pulp
    HAS_PULP = True
except ImportError:
    HAS_PULP = False
    print("[warn] PuLP not installed. Falling back to greedy algorithm.")

_solver = PathwaySolver()


def greedy_set_cover(courses, requirements):
    """
    Greedy set cover: repeatedly pick the course that covers the most
    uncovered requirements. Tiebreak: highest RMP rating, then fewest credits.
    """
    uncovered = set(requirements.keys())
    selected  = []
    remaining = list(courses)

    while uncovered and remaining:
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
            break
        selected.append(best)
        uncovered -= newly_covered
        remaining.remove(best)

    return selected, uncovered


def ilp_set_cover(courses, requirements):
    """
    Integer Linear Programming set cover using PuLP.
    Minimizes total courses while covering all remaining GE categories.
    """
    prob = pulp.LpProblem("BYU_GE_Optimizer", pulp.LpMinimize)

    x = {
        c["course_code"]: pulp.LpVariable(
            f"x_{c['course_code'].replace(' ', '_').replace('/', '_')}",
            cat="Binary"
        )
        for c in courses
    }

    # Objective: minimize number of courses selected
    prob += pulp.lpSum(x[c["course_code"]] for c in courses)

    # Constraint: each remaining GE category must be covered by ≥1 selected course
    for category in requirements:
        covering = [c for c in courses if category in c["ge_categories"]]
        if covering:
            prob += pulp.lpSum(x[c["course_code"]] for c in covering) >= 1

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    selected  = [c for c in courses if pulp.value(x[c["course_code"]]) == 1]
    covered   = set(cat for c in selected for cat in c["ge_categories"])
    uncovered = set(requirements.keys()) - covered

    return selected, uncovered


def _resolve_requirements(courses_taken, remaining_requirements):
    """
    Use PathwaySolver to determine which categories still need work,
    then return (requirements_dict, partial_hints) where partial_hints maps
    category → {course_codes that cheapest-complete it}.
    """
    solve_result  = _solver.solve(courses_taken)
    remaining_cats = solve_result.remaining_categories

    # Cross-reference against GE_REQUIREMENTS (American Heritage needs 2 courses; Religion needs 14 credit hours).
    ge_req_completed = {
        cat for cat in GE_REQUIREMENTS if is_category_complete(cat, courses_taken)
    }
    remaining_cats -= ge_req_completed

    # If caller passed explicit overrides (e.g. from PDF), intersect with them
    if remaining_requirements is not None:
        if isinstance(remaining_requirements, set):
            remaining_cats &= remaining_requirements
        elif isinstance(remaining_requirements, dict):
            remaining_cats &= set(remaining_requirements.keys())

    requirements  = {k: v for k, v in GE_CATEGORIES.items() if k in remaining_cats}

    # Build partial hints: for categories already started, which courses finish cheapest?
    partial_hints = {}
    for cat, pathway_result in solve_result.partial.items():
        if cat not in remaining_cats:
            continue
        hints = cheapest_completion_hint(cat, courses_taken, [])  # courses list not needed here
        # We use the pathway pool directly since we have it
        pool  = set(pathway_result.pathway.course_pool)
        taken = set(pathway_result.already_taken)
        partial_hints[cat] = pool - taken

    return requirements, partial_hints


def optimize(courses, use_ilp=True, remaining_requirements=None, courses_taken=None):
    """
    Run optimization. Returns (selected_courses, uncovered_categories).

    Parameters
    ----------
    courses               : list of course dicts from the scraper
    use_ilp               : use PuLP ILP solver if True, greedy if False
    remaining_requirements: optional set/dict of category names — if supplied,
                            only these categories are optimized for (e.g. from PDF)
    courses_taken         : optional set of course codes already completed.
                            Activates PathwaySolver for universal pathway-aware
                            optimization across ALL 13 GE requirements.
    """

    # ── 1. Resolve which categories still need work ───────────────
    if courses_taken:
        requirements, partial_hints = _resolve_requirements(
            set(courses_taken), remaining_requirements
        )
    elif remaining_requirements is not None:
        partial_hints = {}
        if isinstance(remaining_requirements, set):
            requirements = {k: v for k, v in GE_CATEGORIES.items()
                            if k in remaining_requirements}
        elif isinstance(remaining_requirements, dict):
            requirements = remaining_requirements
        else:
            requirements = GE_CATEGORIES
    else:
        requirements  = GE_CATEGORIES
        partial_hints = {}

    if not requirements:
        return [], set()

    # ── 2. Prune course catalog to remaining categories only ──────
    # Strip already-done categories from each course's tag list so the ILP
    # doesn't over-value a double-dipper whose second category is already done.
    # We preserve the full original list as ge_categories_all for display.
    # Also exclude any course the student has already taken.
    remaining_cat_set = set(requirements.keys())
    taken_set = set(courses_taken) if courses_taken else set()
    ge_courses = []
    for c in courses:
        if c.get("course_code") in taken_set:
            continue
        cats = [cat for cat in c.get("ge_categories", []) if cat in remaining_cat_set]
        if cats:
            pruned = dict(c)
            pruned["ge_categories_all"] = c.get("ge_categories", [])  # full original list
            pruned["ge_categories"] = cats
            ge_courses.append(pruned)

    if not ge_courses:
        return [], set(requirements.keys())

    # ── 3. Inject pathway-completion bonus tags ───────────────────
    # For partially-completed pathways, tag the qualifying completion courses
    # with a synthetic "__pathway_<cat>" category. The ILP/greedy will then
    # naturally prefer these over unrelated alternatives — without distorting
    # the actual GE coverage constraints.
    if partial_hints:
        boosted = []
        for course in ge_courses:
            code   = course["course_code"]
            extras = []
            for cat, hint_codes in partial_hints.items():
                if code in hint_codes:
                    extras.append(f"__pathway_{cat.replace(' ', '_')}")
            if extras:
                course = dict(course)
                course["ge_categories"] = course["ge_categories"] + extras
            boosted.append(course)
        ge_courses = boosted

    # ── 4. Solve ──────────────────────────────────────────────────
    if use_ilp and HAS_PULP:
        print("[optimizer] Running PathwaySolver-aware ILP (PuLP)...")
        selected, uncovered = ilp_set_cover(ge_courses, requirements)
    else:
        print("[optimizer] Running PathwaySolver-aware greedy set-cover...")
        selected, uncovered = greedy_set_cover(ge_courses, requirements)

    # ── 5. Clean up synthetic tags before returning ───────────────
    for c in selected:
        c["ge_categories"] = [
            cat for cat in c.get("ge_categories", [])
            if not cat.startswith("__")
        ]

    # ── 6. Sort: most categories covered → highest RMP rating ─────
    selected.sort(key=lambda c: (
        -len(c.get("ge_categories", [])),
        -c.get("rmp_rating", 0),
    ))

    return selected, uncovered
