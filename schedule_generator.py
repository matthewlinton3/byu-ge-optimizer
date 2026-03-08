"""
Schedule Generator — conflict-free section combinations and ranking.

Uses section data (days, start_time, end_time, room) from schedule_scraper
to find valid schedules and rank by user preferences.
"""

from schedule_scraper import attach_sections_to_courses, parse_course_code
import itertools


def _sections_overlap(sec_a: dict, sec_b: dict) -> bool:
    """True if the two sections have overlapping meeting times."""
    days_a = sec_a.get("days_set") or set()
    days_b = sec_b.get("days_set") or set()
    if not days_a or not days_b or not (days_a & days_b):
        return False
    start_a = sec_a.get("start_time")
    end_a = sec_a.get("end_time")
    start_b = sec_b.get("start_time")
    end_b = sec_b.get("end_time")
    if start_a is None or end_a is None or start_b is None or end_b is None:
        return False
    return not (end_a <= start_b or end_b <= start_a)


def _has_conflict(selection: list[tuple[dict, dict]]) -> bool:
    """selection is list of (course_dict, section_dict). True if any pair conflicts."""
    for i in range(len(selection)):
        for j in range(i + 1, len(selection)):
            if _sections_overlap(selection[i][1], selection[j][1]):
                return True
    return False


def _enumerate_combinations(courses_with_sections: list[dict]) -> list[list[tuple[dict, dict]]]:
    """
    courses_with_sections: list of course dicts each with 'sections' list.
    Returns list of conflict-free combinations; each combination is a list of
    (course_dict, section_dict) with one section per course.
    """
    # Only use sections that have times (for conflict check)
    course_section_lists = []
    for c in courses_with_sections:
        secs = [s for s in c.get("sections", []) if s.get("start_time") is not None and s.get("end_time") is not None and (s.get("days_set") or set())]
        if not secs:
            all_secs = c.get("sections", [])
            secs = all_secs[:1] if all_secs else [{
                "instructor_name": "TBA", "days": "", "room": "",
                "start_time": None, "end_time": None, "days_set": set(),
                "start_time_display": "TBA", "end_time_display": "TBA",
            }]
        course_section_lists.append([(c, s) for s in secs])

    combos = []
    for choice in itertools.product(*course_section_lists):
        if not _has_conflict(list(choice)):
            combos.append(list(choice))
    return combos


# Preference scoring
def _start_preference_score(sec: dict, pref: str) -> float:
    """Higher = better. pref in ('Early', 'Mid', 'Late')."""
    start = sec.get("start_time")
    if start is None:
        return 0.0
    if pref == "Early":
        return 1.0 if 7 <= start < 9 else 0.0
    if pref == "Mid":
        return 1.0 if 9 <= start < 11 else 0.0
    if pref == "Late":
        return 1.0 if start >= 11 else 0.0
    return 0.0


def _days_preference_score(sec: dict, pref: str) -> float:
    """Higher = better. pref in ('MWF', 'TTh', 'No preference')."""
    if pref == "No preference":
        return 1.0
    days_set = sec.get("days_set") or set()
    if not days_set:
        return 0.0
    mwf = {0, 2, 4}
    tth = {1, 3}
    if pref == "MWF" and days_set <= mwf:
        return 1.0
    if pref == "TTh" and days_set <= tth:
        return 1.0
    return 0.0


def _gap_minutes(selection: list[tuple[dict, dict]]) -> float:
    """Total gap between consecutive classes on the same day (in minutes)."""
    # Build per-day list of (start, end) then sort and sum gaps
    by_day = {}
    for course, sec in selection:
        days_set = sec.get("days_set") or set()
        start = sec.get("start_time")
        end = sec.get("end_time")
        if start is None or end is None:
            continue
        for d in days_set:
            by_day.setdefault(d, []).append((start, end))
    total_gap = 0.0
    for d, slots in by_day.items():
        slots.sort(key=lambda x: x[0])
        for i in range(1, len(slots)):
            gap = (slots[i][0] - slots[i - 1][1]) * 60  # minutes
            if gap > 0:
                total_gap += gap
    return total_gap


def rank_combinations(
    combos: list[list[tuple[dict, dict]]],
    preferred_start: str,
    preferred_days: str,
    minimize_gaps: bool,
) -> list[list[tuple[dict, dict]]]:
    """
    Rank conflict-free combinations. Returns sorted list (best first), up to 3.
    preferred_start: 'Early' | 'Mid' | 'Late'
    preferred_days: 'MWF' | 'TTh' | 'No preference'
    minimize_gaps: if True, prefer schedules with fewer gaps between classes.
    """
    def score(combo):
        start_score = sum(_start_preference_score(s, preferred_start) for _, s in combo) / max(len(combo), 1)
        days_score = sum(_days_preference_score(s, preferred_days) for _, s in combo) / max(len(combo), 1)
        gap = _gap_minutes(combo)
        # Lower gap = better when minimize_gaps; use -gap so higher key wins
        gap_component = -gap if minimize_gaps else 0
        return (start_score, days_score, gap_component)

    ranked = sorted(combos, key=score, reverse=True)
    return ranked[:3]


def format_schedule_for_export(selection: list[tuple[dict, dict]]) -> str:
    """Plain text for Google Calendar / iCal paste."""
    lines = []
    for course, sec in selection:
        code = course.get("course_code", "")
        name = course.get("course_name", "")
        inst = sec.get("instructor_name", "TBA")
        days = sec.get("days", "") or "TBA"
        start_d = sec.get("start_time_display") or "TBA"
        end_d = sec.get("end_time_display") or "TBA"
        room = sec.get("room", "") or "TBA"
        lines.append(f"{code} — {name}")
        lines.append(f"  Instructor: {inst}")
        lines.append(f"  Days: {days}  Time: {start_d} - {end_d}")
        lines.append(f"  Room: {room}")
        lines.append("")
    return "\n".join(lines).strip()
