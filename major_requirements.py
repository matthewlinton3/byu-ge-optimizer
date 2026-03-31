"""
BYU Major Requirements
========================
Data model and solver for tracking major requirement completion.
Parallel to pathways.py (which handles GE requirements).

Each major is defined as a list of MajorReqGroup objects. A group can be:
  - "required"      : a single mandatory course
  - "elective_group": choose N courses (or N credits) from a pool
  - "capstone"      : informational milestone, not course-matchable

MajorSolver evaluates which groups are satisfied given a set of taken courses
and returns a MajorState with completed/remaining groups.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class MajorReqGroup:
    """One logical requirement block within a major."""
    group_name: str            # e.g. "Core Courses", "CS Electives", "Capstone"
    req_type: str              # "required" | "elective_group" | "capstone"

    # Course-based requirements
    course_pool: List[str] = field(default_factory=list)   # eligible course codes
    courses_needed: int = 1    # how many courses from pool must be taken

    # Credit-based requirements (when course_pool is empty)
    credit_minimum: int = 0    # minimum credit hours needed
    dept_prefix: str = ""      # e.g. "CS" for open-ended dept electives
    level_min: int = 0         # e.g. 300 for upper-division only

    # GE categories this group can satisfy (for double-dipper detection)
    also_satisfies_ge: List[str] = field(default_factory=list)

    notes: str = ""


@dataclass
class MajorDefinition:
    """Full definition of one major's requirements."""
    major_slug: str            # e.g. "computer-science-bs"
    major_name: str            # e.g. "Computer Science (BS)"
    college: str               # e.g. "Physical and Mathematical Sciences"
    catalog_year: str          # e.g. "2024-2025"
    total_credits: int         # approximate total degree credits
    groups: List[MajorReqGroup] = field(default_factory=list)


@dataclass
class GroupStatus:
    """Satisfaction status of one requirement group."""
    group: MajorReqGroup
    satisfied: bool
    courses_taken_in_group: List[str]   # codes from course_pool that student has taken
    credits_taken: int
    courses_still_needed: int           # 0 if satisfied
    remaining_pool: List[str]           # courses in pool not yet taken


@dataclass
class MajorState:
    """Full evaluation result for one major given a student's taken courses."""
    major_slug: str
    major_name: str
    completed_groups: List[GroupStatus]
    remaining_groups: List[GroupStatus]
    # Courses that satisfy both a major group AND a GE category
    ge_double_dippers: List[str]        # course codes
    completion_pct: float               # 0.0–1.0


# ── Solver ────────────────────────────────────────────────────────────────────

class MajorSolver:
    """
    Evaluates major requirement completion given a set of taken courses.

    Usage:
        solver = MajorSolver()
        state = solver.solve("computer-science-bs", {"CS 142", "CS 235", "MATH 112"})
    """

    def __init__(self):
        # Lazy-load the registry on first use
        self._registry: Optional[Dict[str, MajorDefinition]] = None

    def _load_registry(self) -> Dict[str, MajorDefinition]:
        if self._registry is None:
            from major_scraper import get_major_registry
            self._registry = get_major_registry()
        return self._registry

    def available_majors(self) -> List[Dict[str, str]]:
        """Return list of {slug, name, college} dicts for UI dropdowns."""
        reg = self._load_registry()
        return sorted(
            [{"slug": m.major_slug, "name": m.major_name, "college": m.college}
             for m in reg.values()],
            key=lambda x: (x["college"], x["name"]),
        )

    def solve(self, major_slug: str, courses_taken: Set[str]) -> MajorState:
        """
        Evaluate which requirement groups are satisfied by courses_taken.
        Returns a MajorState with completed/remaining breakdowns.
        """
        reg = self._load_registry()
        major = reg.get(major_slug)
        if major is None:
            return MajorState(
                major_slug=major_slug,
                major_name=major_slug,
                completed_groups=[],
                remaining_groups=[],
                ge_double_dippers=[],
                completion_pct=0.0,
            )

        taken_normalized = {_norm(c) for c in courses_taken}
        completed: List[GroupStatus] = []
        remaining: List[GroupStatus] = []

        for group in major.groups:
            status = self._evaluate_group(group, taken_normalized)
            if status.satisfied:
                completed.append(status)
            else:
                remaining.append(status)

        total = len(major.groups) or 1
        pct = len(completed) / total

        # Find double-dippers: courses that appear in remaining groups and also
        # satisfy a GE category
        ge_dippers = []
        for grp_status in remaining:
            for code in grp_status.remaining_pool:
                if grp_status.group.also_satisfies_ge:
                    ge_dippers.append(code)

        return MajorState(
            major_slug=major_slug,
            major_name=major.major_name,
            completed_groups=completed,
            remaining_groups=remaining,
            ge_double_dippers=list(set(ge_dippers)),
            completion_pct=pct,
        )

    def _evaluate_group(self, group: MajorReqGroup, taken: Set[str]) -> GroupStatus:
        if group.req_type == "capstone":
            return GroupStatus(
                group=group,
                satisfied=False,
                courses_taken_in_group=[],
                credits_taken=0,
                courses_still_needed=0,
                remaining_pool=[],
            )

        pool_norm = {_norm(c): c for c in group.course_pool}
        matched = [orig for norm, orig in pool_norm.items() if norm in taken]
        remaining_pool = [orig for norm, orig in pool_norm.items() if norm not in taken]

        if group.credit_minimum > 0:
            # Credit-based: approximate 3 credits per course
            credits = len(matched) * 3
            satisfied = credits >= group.credit_minimum
            still_needed = max(0, (group.credit_minimum - credits + 2) // 3)
        else:
            credits = len(matched) * 3
            satisfied = len(matched) >= group.courses_needed
            still_needed = max(0, group.courses_needed - len(matched))

        return GroupStatus(
            group=group,
            satisfied=satisfied,
            courses_taken_in_group=matched,
            credits_taken=credits,
            courses_still_needed=still_needed,
            remaining_pool=remaining_pool,
        )

    def get_remaining_courses(self, major_slug: str, courses_taken: Set[str]) -> List[str]:
        """
        Return a flat list of course codes that could still satisfy remaining
        major requirement groups. Used by the optimizer to find double-dippers.
        """
        state = self.solve(major_slug, courses_taken)
        codes = []
        for gs in state.remaining_groups:
            codes.extend(gs.remaining_pool)
        return list(set(codes))


# ── Utilities ─────────────────────────────────────────────────────────────────

def _norm(code: str) -> str:
    """Normalize a course code for comparison (uppercase, collapse spaces)."""
    import re
    return re.sub(r"\s+", " ", code.strip().upper())


def get_major_double_dippers(
    major_slug: str,
    courses_taken: Set[str],
    ge_catalog: List[dict],
    remaining_ge: Set[str],
) -> List[dict]:
    """
    Find courses that satisfy BOTH a remaining major requirement
    AND at least one remaining GE category.

    Returns list of course dicts enriched with 'major_req_groups' key.
    """
    solver = MajorSolver()
    major_courses = set(solver.get_remaining_courses(major_slug, courses_taken))

    state = solver.solve(major_slug, courses_taken)
    # Build a map: course_code → list of major group names it satisfies
    code_to_groups: Dict[str, List[str]] = {}
    for gs in state.remaining_groups:
        for code in gs.remaining_pool:
            code_to_groups.setdefault(_norm(code), []).append(gs.group.group_name)

    results = []
    for course in ge_catalog:
        code_norm = _norm(course.get("course_code", ""))
        ge_cats = [c for c in course.get("ge_categories", []) if c in remaining_ge]
        if ge_cats and code_norm in code_to_groups:
            enriched = dict(course)
            enriched["major_req_groups"] = code_to_groups[code_norm]
            results.append(enriched)

    return sorted(results, key=lambda c: -len(c.get("major_req_groups", [])))
