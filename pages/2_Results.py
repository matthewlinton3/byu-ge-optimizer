"""
BYU GE Optimizer — Results page (page 2).
Dark theme: course cards with RMP badges, week-view calendar, GE coverage.
"""

import streamlit as st
import pandas as pd
from styles import inject_styles
from scraper import scrape_catalog_for_ge, GE_CATEGORIES, init_db
from optimizer import optimize
from rmp import enrich_with_rmp
from ge_requirements import GE_REQUIREMENTS
from schedule_scraper import attach_sections_to_courses
from schedule_generator import (
    filter_sections_by_blackout,
    _enumerate_combinations,
    rank_combinations,
    format_schedule_for_export,
)

inject_styles()

# ── Redirect if Setup was not completed ───────────────────────────
if not st.session_state.get("setup_done") or st.session_state.get("completed_categories") is None:
    st.warning("Please complete Setup first: upload your degree audit and click **Find My GE Courses**.")
    if st.button("Go to Setup"):
        st.switch_page("pages/1_Setup.py")
    st.stop()

if "blackout_slots" not in st.session_state:
    st.session_state.blackout_slots = []

blackout_slots = st.session_state.get("blackout_slots") or []
completed_categories = st.session_state.completed_categories or set()
remaining_categories = st.session_state.remaining_categories or set(GE_CATEGORIES.keys())
courses_taken = st.session_state.get("courses_taken") or set()
locked_courses = st.session_state.get("locked_courses") or []
preferred_days = st.session_state.get("preferred_days") or "No preference"
preferred_start = st.session_state.get("preferred_start") or "Mid"
minimize_gaps = st.session_state.get("minimize_gaps", True)
major_slug = st.session_state.get("major_slug") or None
major_state = st.session_state.get("major_state") or None

# ── Back button + options ──────────────────────────────────────────
back_col, opt_col = st.columns([1, 3])
with back_col:
    if st.button("Back to Setup", key="back_setup"):
        st.switch_page("pages/1_Setup.py")

with st.expander("Options", expanded=False):
    opt1, opt2, opt3, opt4, opt5 = st.columns(5)
    with opt1:
        use_ilp = st.toggle("ILP Optimization", value=True, help="Minimum courses. Turn off for faster greedy.")
    with opt2:
        skip_rmp = st.toggle("Skip RMP Ratings", value=False, help="Faster run, no professor data.")
    with opt3:
        refresh = st.toggle("Refresh Catalog", value=False, help="Re-scrape BYU catalog (slow).")
    with opt4:
        include_honors = st.toggle("Include Honors", value=False, help="Show Honors-only courses (require Honors program enrollment).")
    with opt5:
        sort_priority = st.radio(
            "Sort by",
            options=["Balanced", "Fewest Classes", "Best Professor", "Easiest Classes"],
            index=0,
            key="sort_priority",
        )

st.markdown("## Results")

# ── GE completion status ───────────────────────────────────────────
prog_col1, prog_col2 = st.columns(2)
with prog_col1:
    st.markdown("**Completed**")
    done_pills = "".join(
        f'<span class="byu-pill byu-pill-done">&#10003; {cat}</span>'
        for cat in sorted(completed_categories)
    )
    st.markdown(f'<div>{done_pills or "&#8212;"}</div>', unsafe_allow_html=True)
with prog_col2:
    st.markdown("**Remaining**")
    rem_pills = "".join(
        f'<span class="byu-pill byu-pill-remaining">{cat}</span>'
        for cat in sorted(remaining_categories)
    )
    st.markdown(f'<div>{rem_pills or "&#8212;"}</div>', unsafe_allow_html=True)


def run_optimizer(use_ilp, skip_rmp, refresh, remaining_reqs, courses_taken_set):
    init_db()
    with st.status("Running optimizer...", expanded=True) as status:
        st.write("Loading BYU GE course data...")
        courses = scrape_catalog_for_ge(refresh=refresh)
        st.write(f"Loaded {len(courses)} GE courses")
        st.write(f"Optimizing for {len(remaining_reqs)} remaining categories...")
        selected, uncovered = optimize(
            courses,
            use_ilp=use_ilp,
            remaining_requirements=remaining_reqs,
            courses_taken=courses_taken_set or None,
            major_slug=st.session_state.get("major_slug") or None,
        )
        st.write(f"Selected {len(selected)} courses")
        if not skip_rmp:
            st.write("Fetching RateMyProfessors ratings...")
            selected = enrich_with_rmp(selected, refresh=refresh)
        status.update(label="Optimization complete", state="complete")
    return selected, uncovered


locked_codes = {c["course_code"] for c in locked_courses}
locked_covered = set()
for lc in locked_courses:
    locked_covered.update(lc.get("ge_categories_all", lc.get("ge_categories", [])))
remaining_after_lock = remaining_categories - locked_covered

if st.session_state.get("results") is None or st.session_state.get("uncovered") is None:
    selected, uncovered = run_optimizer(
        use_ilp, skip_rmp, refresh, remaining_categories, courses_taken
    )
    st.session_state.results = selected
    st.session_state.uncovered = uncovered
    st.rerun()

if not locked_courses:
    selected = list(st.session_state.results)
    uncovered = st.session_state.uncovered
elif not remaining_after_lock:
    selected = []
    uncovered = set()
else:
    courses = scrape_catalog_for_ge(refresh=refresh)
    filtered = [c for c in courses if c["course_code"] not in locked_codes]
    selected, uncovered = optimize(
        filtered,
        use_ilp=use_ilp,
        remaining_requirements=remaining_after_lock,
        courses_taken=courses_taken or None,
        major_slug=major_slug,
    )
    if not skip_rmp:
        selected = enrich_with_rmp(selected, refresh=refresh)

# Sort
def _rating_for_sort(c):
    v = c.get("rmp_rating")
    return v if v is not None else -1

def _difficulty_for_sort(c):
    v = c.get("rmp_difficulty")
    return v if v is not None else 99

num_cats = lambda c: len(c.get("ge_categories", []))
if sort_priority == "Best Professor":
    selected.sort(key=lambda c: (-_rating_for_sort(c), -num_cats(c), _difficulty_for_sort(c)))
elif sort_priority == "Easiest Classes":
    selected.sort(key=lambda c: (_difficulty_for_sort(c), -_rating_for_sort(c), -num_cats(c)))
elif sort_priority == "Fewest Classes":
    selected.sort(key=lambda c: (-num_cats(c), -_rating_for_sort(c), _difficulty_for_sort(c)))
else:
    selected.sort(key=lambda c: (-num_cats(c), -_rating_for_sort(c), _difficulty_for_sort(c)))

def _is_honors(c):
    code = c.get("course_code", "")
    name = c.get("course_name", "")
    dept = code.split()[0] if code else ""
    if dept.upper() in ("HONRS", "HON"):
        return True
    if code.upper().endswith("H") and len(code) > 1 and code[-2].isdigit():
        return True
    if "honors" in name.lower():
        return True
    return False

if not include_honors:
    selected = [c for c in selected if not _is_honors(c)]

all_cats = set(GE_CATEGORIES.keys())
covered_by_optimizer = all_cats - uncovered - completed_categories
total_credits = sum(c.get("credit_hours", 3) for c in selected) + sum(
    c.get("credit_hours", 3) for c in locked_courses
)
double_dippers = [c for c in selected if len(c.get("ge_categories_all", c.get("ge_categories", []))) > 1]

# ── Locked courses ─────────────────────────────────────────────────
if locked_courses:
    lock_col1, lock_col2 = st.columns([3, 1])
    with lock_col1:
        st.markdown("### &#10003; Locked Courses")
    with lock_col2:
        if st.button("Reset All", key="reset_locked"):
            st.session_state.locked_courses = []
            st.session_state.schedule_options = None
            st.rerun()
    for lc in locked_courses:
        cats = lc.get("ge_categories", lc.get("ge_categories_all", []))
        pills = "".join(f'<span class="byu-pill byu-pill-done">{cat}</span>' for cat in cats)
        row1, row2 = st.columns([5, 1])
        with row1:
            st.markdown(
                f'<div class="byu-locked-section">'
                f'<span class="course-code">{lc["course_code"]}</span>'
                f' &mdash; {lc["course_name"]}'
                f'<div style="margin-top:0.5rem">{pills}</div></div>',
                unsafe_allow_html=True,
            )
        with row2:
            if st.button("Unlock", key=f"unlock_{lc['course_code']}"):
                st.session_state.locked_courses = [
                    x for x in st.session_state.locked_courses
                    if x["course_code"] != lc["course_code"]
                ]
                st.session_state.schedule_options = None
                st.rerun()
    st.markdown("")

# ── GE coverage summary ────────────────────────────────────────────
st.markdown("### GE Coverage")
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("**Completed**")
    done_pills = "".join(
        f'<span class="byu-pill byu-pill-done">&#10003; {cat}</span>'
        for cat in sorted(completed_categories)
    )
    st.markdown(f'<div>{done_pills or "&#8212;"}</div>', unsafe_allow_html=True)
with p2:
    st.markdown("**Covered by recommendations**")
    cov_pills = "".join(
        f'<span class="byu-pill byu-pill-remaining">{cat}</span>'
        for cat in sorted(covered_by_optimizer)
    )
    st.markdown(f'<div>{cov_pills or "&#8212;"}</div>', unsafe_allow_html=True)
with p3:
    st.markdown("**Still uncovered**")
    unc_pills = "".join(
        f'<span class="byu-pill byu-pill-uncovered">{cat}</span>'
        for cat in sorted(uncovered)
    )
    st.markdown(f'<div>{unc_pills or "&#8212;"}</div>', unsafe_allow_html=True)

total_done = len(completed_categories) + len(covered_by_optimizer)
st.progress(total_done / len(all_cats))
st.caption(f"Overall: {total_done}/{len(all_cats)} categories covered")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Courses to take", len(locked_courses) + len(selected))
m2.metric("Est. credits", f"~{total_credits}")
m3.metric("Already done", len(completed_categories))
m4.metric("Covered", len(covered_by_optimizer))
m5.metric("Double-dippers", len(double_dippers))

st.divider()


# ── Helpers ────────────────────────────────────────────────────────
def _rmp_badge(profs: list) -> str:
    """Return the best RMP badge HTML across a professor list."""
    ratings = [p.get("rating") for p in profs if p.get("rating") is not None]
    if not ratings:
        return '<span class="rmp-badge rmp-none">No rating</span>'
    best = max(ratings)
    if best >= 4.0:
        cls = "rmp-good"
    elif best >= 3.0:
        cls = "rmp-mid"
    else:
        cls = "rmp-bad"
    return f'<span class="rmp-badge {cls}">&#9733; {best:.1f}</span>'


def render_calendar(selection: list) -> None:
    """Render a dark-themed week-view calendar from a list of (course, section) tuples."""
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    START_HOUR = 7
    END_HOUR = 20
    SLOT_MINS = 30

    COLORS = [
        ("#1e3a5f", "#4a9eff"),
        ("#1e3d2f", "#4ade80"),
        ("#3d1e3a", "#e879f9"),
        ("#3d2e1e", "#fb923c"),
        ("#1e3d3a", "#2dd4bf"),
        ("#3d1e1e", "#f87171"),
    ]

    # Build half-hour slot list
    slots = []
    sh, sm = START_HOUR, 0
    while sh < END_HOUR:
        slots.append((sh, sm))
        sm += SLOT_MINS
        if sm >= 60:
            sm = 0
            sh += 1

    # Map (day_idx, slot_idx) -> cell data
    course_cells: dict = {}
    for i, (course, sec) in enumerate(selection):
        code = course.get("course_code", "")
        color_bg, color_text = COLORS[i % len(COLORS)]
        days_set = sec.get("days_set") or set()
        start_t = sec.get("start_time")
        end_t = sec.get("end_time")
        room = (sec.get("room") or "").strip()

        if start_t is None or end_t is None:
            continue

        for j, (h, m) in enumerate(slots):
            slot_start = h + m / 60.0
            slot_end = slot_start + SLOT_MINS / 60.0
            if slot_start >= end_t or slot_end <= start_t:
                continue
            is_start = slot_start <= start_t < slot_end
            for day_idx in range(5):
                if day_idx in days_set and (day_idx, j) not in course_cells:
                    course_cells[(day_idx, j)] = {
                        "code": code,
                        "room": room,
                        "color_bg": color_bg,
                        "color_text": color_text,
                        "is_start": is_start,
                    }

    html = """
<style>
.cal-wrap { overflow-x: auto; margin: 1.5rem 0; }
.cal-table { border-collapse: collapse; width: 100%; min-width: 500px;
             font-family: 'IBM Plex Sans', sans-serif; font-size: 0.78rem; }
.cal-table th { background: #1A1F2E; color: #8892A4; padding: 0.5rem;
                text-align: center; font-weight: 600; letter-spacing: 0.05em;
                border: 1px solid #2D3548; }
.cal-table td { border: 1px solid #2D3548; padding: 0; vertical-align: top; height: 28px; }
.cal-time { background: #12161F; color: #5A6478; padding: 0.25rem 0.5rem;
            text-align: right; font-size: 0.7rem; white-space: nowrap; width: 48px; }
.cal-hour-line td { border-top: 1px solid #2D3548 !important; }
.cal-half td { border-top: 1px dashed #1E2535 !important; }
.cal-cell-empty { background: #0F1117; }
.cal-block { border-radius: 4px; padding: 3px 6px; height: 100%;
             display: flex; flex-direction: column; justify-content: flex-start;
             font-weight: 600; font-size: 0.7rem; line-height: 1.3; overflow: hidden; }
.cal-room  { font-weight: 400; font-size: 0.62rem; opacity: 0.8;
             white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
<div class="cal-wrap"><table class="cal-table"><thead><tr>
<th style="width:48px"></th>
"""
    for day in DAYS:
        html += f"<th>{day}</th>"
    html += "</tr></thead><tbody>"

    for j, (h, m) in enumerate(slots):
        row_cls = "cal-hour-line" if m == 0 else "cal-half"
        if m == 0:
            h12 = h if h <= 12 else h - 12
            ampm = "am" if h < 12 else "pm"
            time_str = f"{h12}:{m:02d}{ampm}"
        else:
            time_str = ""
        html += f'<tr class="{row_cls}"><td class="cal-time">{time_str}</td>'
        for d in range(5):
            cell = course_cells.get((d, j))
            if cell:
                label = ""
                if cell["is_start"]:
                    label = cell["code"]
                    if cell["room"]:
                        label += f'<span class="cal-room">{cell["room"]}</span>'
                else:
                    label = "&nbsp;"
                html += (
                    f'<td style="background:{cell["color_bg"]};padding:0">'
                    f'<div class="cal-block" style="color:{cell["color_text"]}">'
                    f'{label}</div></td>'
                )
            else:
                html += '<td class="cal-cell-empty"></td>'
        html += "</tr>"

    html += "</tbody></table></div>"
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ── Results tabs ───────────────────────────────────────────────────
_tab_labels = ["Recommended Courses", "Full GE Map", "Double-Dippers"]
if major_slug:
    _tab_labels.append("Major Requirements")
_tabs = st.tabs(_tab_labels)
tab1, tab2, tab3 = _tabs[0], _tabs[1], _tabs[2]
tab_major = _tabs[3] if major_slug else None

with tab1:
    st.caption(f"Sorted by: **{sort_priority}**. Sections conflicting with your blackout times are hidden.")
    if locked_courses:
        st.caption("Lock courses you want to keep; the optimizer recommends the best options for the rest.")
    if not remaining_after_lock and locked_courses:
        st.success("All remaining GE categories are covered by your locked courses.")

    for idx, c in enumerate(selected, start=1):
        cats = c.get("ge_categories", [])
        profs = c.get("professors", [])
        badge = _rmp_badge(profs)
        ge_pills_html = "".join(f'<span class="ge-pill">{cat}</span>' for cat in cats)

        # Professor rows
        prof_rows_html = ""
        if profs:
            for p in profs:
                rating = p.get("rating")
                diff = p.get("difficulty")
                wta = p.get("would_take_again")
                star_str = f'<span class="stars">&#9733; {rating:.1f}</span>' if rating else ""
                diff_str = f"Difficulty {diff:.1f}/5" if diff else ""
                wta_str = f"{wta:.0f}% would take again" if wta is not None and wta >= 0 else ""
                parts = [f'<span class="prof-name">{p.get("name", "")}</span>']
                if star_str:
                    parts.append(star_str)
                if diff_str:
                    parts.append(diff_str)
                if wta_str:
                    parts.append(wta_str)
                prof_rows_html += f'<div class="prof-row">{" &middot; ".join(parts)}</div>'
        else:
            prof_rows_html = '<div class="prof-row" style="color:#5A6478">No professor ratings yet</div>'

        card_html = f"""
<div class="course-card">
  <div class="course-card-header">
    <span style="color:#5A6478;font-size:0.85rem;font-weight:600;margin-right:8px;min-width:1.5rem;text-align:right;">{idx}.</span>
    <span class="course-code">{c['course_code']}</span>
    {badge}
  </div>
  <div class="course-name">{c['course_name']}</div>
  <div class="ge-pills">{ge_pills_html}</div>
  {prof_rows_html}
</div>
"""
        st.markdown(card_html, unsafe_allow_html=True)
        if st.button("Lock this course", key=f"lock_{c['course_code']}"):
            if c["course_code"] not in locked_codes:
                st.session_state.locked_courses = st.session_state.locked_courses + [dict(c)]
                st.session_state.schedule_options = None
            st.rerun()

    # CSV export
    rows = []
    for c in locked_courses + selected:
        profs = c.get("professors", [])
        cats = c.get("ge_categories", [])
        if profs:
            for p in profs:
                rows.append({
                    "Course": c["course_code"], "Name": c["course_name"],
                    "GE Categories": ", ".join(cats),
                    "Professor": p.get("name", ""),
                    "Rating": round(p["rating"], 1) if p.get("rating") else None,
                    "Difficulty": round(p["difficulty"], 1) if p.get("difficulty") else None,
                    "Would Take Again": f"{p['would_take_again']:.0f}%" if p.get("would_take_again") is not None and p["would_take_again"] >= 0 else "—",
                })
        else:
            rows.append({
                "Course": c["course_code"], "Name": c["course_name"],
                "GE Categories": ", ".join(cats),
                "Professor": "—", "Rating": None, "Difficulty": None, "Would Take Again": "—",
            })
    df_export = pd.DataFrame(rows)
    st.download_button(
        "Download CSV",
        data=df_export.to_csv(index=False),
        file_name="byu_ge_optimizer_results.csv",
        mime="text/csv",
        key="dl_csv",
    )

with tab2:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**Completed**")
        for cat in sorted(completed_categories):
            st.markdown(f'<span class="byu-pill byu-pill-done">&#10003; {cat}</span>', unsafe_allow_html=True)
    with col_b:
        st.markdown("**Covered by optimizer**")
        for cat in sorted(covered_by_optimizer):
            courses_for = [c for c in selected if cat in c.get("ge_categories", [])]
            courses_for += [c for c in locked_courses if cat in c.get("ge_categories", c.get("ge_categories_all", []))]
            codes = ", ".join(c["course_code"] for c in courses_for)
            st.markdown(
                f'<span class="byu-pill byu-pill-remaining">{cat}</span>'
                f'<span style="color:#5A6478;font-size:0.8rem;"> &rarr; {codes}</span>',
                unsafe_allow_html=True,
            )
    with col_c:
        st.markdown("**Uncovered**")
        if uncovered:
            for cat in sorted(uncovered):
                st.markdown(f'<span class="byu-pill byu-pill-uncovered">{cat}</span>', unsafe_allow_html=True)
            st.warning("No courses in catalog for these categories.")
        else:
            st.success("All remaining requirements covered.")

with tab3:
    ge_dippers = [c for c in selected if len(c.get("ge_categories_all", c.get("ge_categories", []))) > 1]
    major_dippers = [c for c in selected if c.get("major_req_groups")]

    if ge_dippers:
        st.markdown("**GE double-dippers** — satisfy 2+ GE categories")
        for c in sorted(ge_dippers, key=lambda x: -len(x.get("ge_categories_all", x.get("ge_categories", [])))):
            cats_rem = c.get("ge_categories", [])
            cats_all = c.get("ge_categories_all", cats_rem)
            profs = c.get("professors", [])
            badge = _rmp_badge(profs)
            ge_pills_html = "".join(f'<span class="ge-pill">{cat}</span>' for cat in cats_rem)
            st.markdown(f"""
<div class="course-card">
  <div class="course-card-header"><span class="course-code">{c['course_code']}</span>{badge}</div>
  <div class="course-name">{c['course_name']}</div>
  <div class="ge-pills">{ge_pills_html}</div>
  <div style="margin-top:0.5rem;font-size:0.75rem;color:#5A6478">Covers {len(cats_all)} categories &middot; {len(cats_rem)} still needed</div>
</div>
""", unsafe_allow_html=True)

    if major_dippers:
        st.markdown("**GE + Major double-dippers** — satisfy a GE requirement AND your major")
        for c in sorted(major_dippers, key=lambda x: -len(x.get("major_req_groups", []))):
            cats_rem = c.get("ge_categories", [])
            maj_groups = c.get("major_req_groups", [])
            profs = c.get("professors", [])
            badge = _rmp_badge(profs)
            ge_pills = "".join(f'<span class="ge-pill">{cat}</span>' for cat in cats_rem)
            maj_pills = "".join(f'<span class="ge-pill" style="background:#D4A017;color:#000;">{g}</span>' for g in maj_groups)
            st.markdown(f"""
<div class="course-card">
  <div class="course-card-header"><span class="course-code">{c['course_code']}</span>{badge}</div>
  <div class="course-name">{c['course_name']}</div>
  <div class="ge-pills">{ge_pills}{maj_pills}</div>
  <div style="margin-top:0.5rem;font-size:0.75rem;color:#5A6478">{len(cats_rem)} GE categories + {len(maj_groups)} major requirement(s)</div>
</div>
""", unsafe_allow_html=True)

    if not ge_dippers and not major_dippers:
        st.info("No double-dipping courses in this selection.")

if tab_major is not None:
    with tab_major:
        if major_state is None:
            st.info("Go back to Setup and select your major to see requirement details.")
        else:
            st.markdown(f"### {major_state.major_name}")
            st.progress(major_state.completion_pct,
                        text=f"{int(major_state.completion_pct * 100)}% complete")
            _rec_codes = {c["course_code"] for c in selected}
            col_done, col_rem = st.columns(2)
            with col_done:
                st.markdown("**Completed**")
                if major_state.completed_groups:
                    for gs in major_state.completed_groups:
                        taken_str = ", ".join(gs.courses_taken_in_group) if gs.courses_taken_in_group else "satisfied"
                        st.markdown(
                            f'<span class="byu-pill byu-pill-done">&#10003; {gs.group.group_name}</span>'
                            f'<span style="color:#5A6478;font-size:0.75rem;margin-left:6px;">{taken_str}</span>',
                            unsafe_allow_html=True)
                else:
                    st.caption("None yet")
            with col_rem:
                st.markdown("**Still needed**")
                if major_state.remaining_groups:
                    for gs in major_state.remaining_groups:
                        rec_in_pool = [c for c in gs.remaining_pool if c in _rec_codes]
                        badge = f'<span style="background:#0062B8;color:#fff;border-radius:4px;padding:1px 6px;font-size:0.7rem;margin-left:4px;">&#10132; {rec_in_pool[0]} recommended</span>' if rec_in_pool else ""
                        still = f" ({gs.courses_still_needed} more)" if gs.courses_still_needed > 1 else ""
                        st.markdown(
                            f'<span class="byu-pill byu-pill-remaining">{gs.group.group_name}{still}</span>{badge}',
                            unsafe_allow_html=True)
                        if gs.remaining_pool:
                            with st.expander(f"Options for {gs.group.group_name}", expanded=False):
                                for code in gs.remaining_pool[:15]:
                                    is_rec = " ✓ recommended" if code in _rec_codes else ""
                                    st.markdown(f"- `{code}`{is_rec}")
                else:
                    st.success("All major requirements complete!")

st.divider()

# ── Schedule Generator ─────────────────────────────────────────────
if locked_courses:
    st.markdown("## Schedule Generator")
    st.caption("Conflict-free section combinations for your locked courses, excluding your blackout times.")

    start_options = ["Early (7–9am)", "Mid (9–11am)", "Late (11am+)"]
    start_idx = min(
        ["Early", "Mid", "Late"].index(preferred_start)
        if preferred_start in ("Early", "Mid", "Late") else 1,
        2,
    )
    pref_start_label = st.radio(
        "Preferred start time",
        options=start_options,
        index=start_idx,
        key="sched_pref_start",
        horizontal=True,
    )
    start_map = {"Early (7–9am)": "Early", "Mid (9–11am)": "Mid", "Late (11am+)": "Late"}
    pref_start_val = start_map.get(pref_start_label, "Mid")

    pref_days_label = st.radio(
        "Preferred days",
        options=["MWF", "TTh", "No preference"],
        index=["MWF", "TTh", "No preference"].index(preferred_days),
        key="sched_pref_days",
        horizontal=True,
    )
    min_gaps = st.checkbox("Minimize gaps between classes", value=minimize_gaps, key="sched_min_gaps")

    if st.button("Generate My Schedule", type="primary", key="gen_schedule"):
        locked_copy = [dict(c) for c in locked_courses]
        with st.spinner("Fetching section times from BYU class schedule..."):
            attach_sections_to_courses(locked_copy)
        for co in locked_copy:
            co["sections"] = filter_sections_by_blackout(co.get("sections", []), blackout_slots)
        combos = _enumerate_combinations(locked_copy)
        if not combos:
            st.warning(
                "No conflict-free schedule found for your locked courses. "
                "Sections may overlap, fall in your blackout times, or have missing time data."
            )
        else:
            ranked = rank_combinations(combos, pref_start_val, pref_days_label, min_gaps)
            st.session_state.schedule_options = ranked
            st.session_state.schedule_index = 0
            st.rerun()

    if st.session_state.get("schedule_options"):
        opts = st.session_state.schedule_options
        idx = st.session_state.schedule_index
        names = [f"Option {i+1}" for i in range(len(opts))]
        sel_name = st.radio(
            "Schedule option",
            names,
            index=min(idx, len(opts) - 1),
            key="sched_choice",
            horizontal=True,
        )
        st.session_state.schedule_index = names.index(sel_name)
        selection = opts[st.session_state.schedule_index]

        render_calendar(selection)

        export_text = format_schedule_for_export(selection)
        st.download_button(
            "Download schedule as text",
            data=export_text,
            file_name="byu_schedule.txt",
            mime="text/plain",
            key="sched_export",
        )
        st.caption("Each block shows course code and room. Import into Google Calendar or paste as plain text.")
