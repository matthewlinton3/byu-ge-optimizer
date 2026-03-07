"""
BYU GE Optimizer
Uses greedy set-cover + PuLP ILP to find the fewest courses that fulfill all GE requirements.
"""

from scraper import GE_CATEGORIES

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


def optimize(courses, use_ilp=True, remaining_requirements=None):
    """
    Run optimization. Returns (selected_courses, uncovered_categories).

    Args:
        courses: list of course dicts from the scraper
        use_ilp: use PuLP ILP solver if True, greedy if False
        remaining_requirements: optional set/dict of category names to optimize for.
            If None, optimizes for ALL GE categories.
            Pass a subset to only find courses for incomplete requirements
            (e.g. after parsing a degree audit PDF).
    """
    if remaining_requirements is None:
        requirements = GE_CATEGORIES
    elif isinstance(remaining_requirements, set):
        # Convert set of category names to dict matching GE_CATEGORIES format
        requirements = {k: v for k, v in GE_CATEGORIES.items() if k in remaining_requirements}
    else:
        requirements = remaining_requirements

    if not requirements:
        # Everything is already done!
        return [], set()

    # Only consider courses that fulfill at least one REMAINING GE category
    ge_courses = [
        c for c in courses
        if c.get("ge_categories") and
        any(cat in requirements for cat in c["ge_categories"])
    ]

    if not ge_courses:
        return [], set(requirements.keys())

    if use_ilp and HAS_PULP:
        print("[optimizer] Running ILP optimization (PuLP)...")
        selected, uncovered = ilp_set_cover(ge_courses, requirements)
    else:
        print("[optimizer] Running greedy set-cover optimization...")
        selected, uncovered = greedy_set_cover(ge_courses, requirements)

    # Sort: most GE categories covered first, then by RMP rating
    selected.sort(key=lambda c: (
        -len(c.get("ge_categories", [])),
        -c.get("rmp_rating", 0),
    ))

    return selected, uncovered
