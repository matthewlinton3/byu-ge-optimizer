"""
BYU GE Optimizer — Results page (page 2).
Reads session state from Setup; runs optimizer; shows course cards with lock/unlock and schedule generator.
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

# Ensure blackout_slots exists (list of (day, start, end))
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

# ── Back to Setup ──────────────────────────────────────────────────
if st.button("← Back to Setup", key="back_setup"):
    st.switch_page("pages/1_Setup.py")

st.markdown("## Results")

# ── GE completion status pills ─────────────────────────────────────
st.markdown("### GE progress")
prog_col1, prog_col2 = st.columns(2)
with prog_col1:
    st.markdown("**Completed**")
    done_pills = "".join(
        f'<span class="byu-pill byu-pill-done">✓ {cat}</span>'
        for cat in sorted(completed_categories)
    )
    st.markdown(f'<div class="ge-pills">{done_pills or "—"}</div>', unsafe_allow_html=True)
with prog_col2:
    st.markdown("**Remaining**")
    rem_pills = "".join(
        f'<span class="byu-pill byu-pill-remaining">{cat}</span>'
        for cat in sorted(remaining_categories)
    )
    st.markdown(f'<div class="ge-pills">{rem_pills or "—"}</div>', unsafe_allow_html=True)

# ── Run optimizer (once) and cache in session state ─────────────────
with st.sidebar:
    st.markdown("### Options")
    use_ilp = st.toggle("ILP Optimization", value=True, help="Minimum courses. Turn off for faster greedy.")
    skip_rmp = st.toggle("Skip RMP Ratings", value=False, help="Faster run, no professor data.")
    refresh = st.toggle("Refresh Catalog", value=False, help="Re-scrape BYU catalog (slow).")
    st.divider()
    st.markdown("### Sort results by")
    sort_priority = st.radio(
        "Sort results by",
        options=["Balanced", "Fewest Classes", "Best Professor", "Easiest Classes"],
        index=0,
        label_visibility="collapsed",
        key="sort_priority",
    )


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
        )
        st.write(f"Selected {len(selected)} courses")
        if not skip_rmp:
            st.write("Fetching RateMyProfessors ratings...")
            selected = enrich_with_rmp(selected, refresh=refresh)
        status.update(label="Optimization complete", state="complete")
    return selected, uncovered


# Run optimizer on first load or when we need fresh results
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

# Recompute selected/uncovered when we have locked courses
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

all_cats = set(GE_CATEGORIES.keys())
covered_by_optimizer = all_cats - uncovered - completed_categories
total_credits = sum(c.get("credit_hours", 3) for c in selected) + sum(
    c.get("credit_hours", 3) for c in locked_courses
)
double_dippers = [c for c in selected if len(c.get("ge_categories_all", c.get("ge_categories", []))) > 1]

# ── Locked courses section ──────────────────────────────────────────
if locked_courses:
    lock_header_col1, lock_header_col2 = st.columns([3, 1])
    with lock_header_col1:
        st.markdown("### ✅ Your Locked Courses")
    with lock_header_col2:
        if st.button("Reset All", key="reset_locked", help="Clear all locked courses"):
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
                f'<span class="course-code">{lc["course_code"]}</span> — {lc["course_name"]} '
                f'<div class="ge-pills">{pills}</div></div>',
                unsafe_allow_html=True,
            )
        with row2:
            if st.button("🔓 Unlock", key=f"unlock_{lc['course_code']}"):
                st.session_state.locked_courses = [
                    x for x in st.session_state.locked_courses if x["course_code"] != lc["course_code"]
                ]
                st.session_state.schedule_options = None
                st.rerun()
    st.markdown("")

# Progress: completed | covered | uncovered
st.markdown("### GE coverage")
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("**Completed**")
    done_pills = "".join(f'<span class="byu-pill byu-pill-done">✓ {cat}</span>' for cat in sorted(completed_categories))
    st.markdown(f'<div class="ge-pills">{done_pills or "—"}</div>', unsafe_allow_html=True)
with p2:
    st.markdown("**Covered by recommendations**")
    cov_pills = "".join(f'<span class="byu-pill byu-pill-remaining">{cat}</span>' for cat in sorted(covered_by_optimizer))
    st.markdown(f'<div class="ge-pills">{cov_pills or "—"}</div>', unsafe_allow_html=True)
with p3:
    st.markdown("**Still uncovered**")
    unc_pills = "".join(f'<span class="byu-pill byu-pill-uncovered">{cat}</span>' for cat in sorted(uncovered))
    st.markdown(f'<div class="ge-pills">{unc_pills or "None"}</div>', unsafe_allow_html=True)

total_done = len(completed_categories) + len(covered_by_optimizer)
st.progress(total_done / len(all_cats))
st.caption(f"Overall: {total_done}/{len(all_cats)} categories")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Courses to take", len(locked_courses) + len(selected))
m2.metric("Est. credits", f"~{total_credits}")
m3.metric("Already done", len(completed_categories))
m4.metric("Covered", len(covered_by_optimizer))
m5.metric("Double-dippers", len(double_dippers))

st.divider()

# ── Recommended course cards (with sections filtered by blackout) ───
tab1, tab2, tab3 = st.tabs(["Recommended courses", "Full GE map", "Double-dippers"])

with tab1:
    st.caption(f"Sorted by: **{sort_priority}**. Sections that conflict with your blackout times are hidden.")
    if locked_courses:
        st.caption("Lock courses you want to keep; the optimizer will recommend the best options for the rest.")
    if not remaining_after_lock and locked_courses:
        st.success("All remaining GE categories are covered by your locked courses.")

    for c in selected:
        cats = c.get("ge_categories", [])
        ge_pills_html = "".join(
            f'<span class="byu-pill byu-pill-remaining">{cat}</span>' for cat in cats
        )
        profs = c.get("professors", [])
        prof_rows = []
        if profs:
            for p in profs:
                rating = p.get("rating") or 0
                diff = p.get("difficulty")
                wta = p.get("would_take_again")
                star_str = f'<span class="stars">★ {rating:.1f}</span>' if rating else "—"
                diff_str = f"Difficulty {diff:.1f}/5" if diff else ""
                wta_str = f"{wta:.0f}% would take again" if wta is not None and wta >= 0 else ""
                parts = [f'<span class="prof-name">{p.get("name", "—")}</span>', star_str, diff_str, wta_str]
                prof_rows.append("<div class=\"prof-row\">" + " · ".join(p for p in parts if p) + "</div>")
        else:
            prof_rows.append("<div class=\"prof-row\">No professor ratings yet</div>")
        card_html = f"""
        <div class="byu-course-card">
            <div class="course-title"><span class="course-code">{c['course_code']}</span> — {c['course_name']}</div>
            <div class="ge-pills">{ge_pills_html}</div>
            {"".join(prof_rows)}
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        if st.button("🔒 Lock this course", key=f"lock_{c['course_code']}"):
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
    st.download_button("Download CSV", data=df_export.to_csv(index=False), file_name="byu_ge_optimizer_results.csv", mime="text/csv", key="dl_csv")

with tab2:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**Completed**")
        for cat in sorted(completed_categories):
            st.markdown(f'<span class="byu-pill byu-pill-done">✓ {cat}</span>', unsafe_allow_html=True)
    with col_b:
        st.markdown("**Covered by optimizer**")
        for cat in sorted(covered_by_optimizer):
            courses_for = [c for c in selected if cat in c.get("ge_categories", [])]
            courses_for += [c for c in locked_courses if cat in c.get("ge_categories", c.get("ge_categories_all", []))]
            codes = ", ".join(c["course_code"] for c in courses_for)
            st.markdown(f'<span class="byu-pill byu-pill-remaining">{cat}</span> <span style="color:#666;font-size:0.8rem;">→ {codes}</span>', unsafe_allow_html=True)
    with col_c:
        st.markdown("**Uncovered**")
        if uncovered:
            for cat in sorted(uncovered):
                st.markdown(f'<span class="byu-pill byu-pill-uncovered">{cat}</span>', unsafe_allow_html=True)
            st.warning("No courses in catalog for these categories.")
        else:
            st.success("All remaining requirements covered.")

with tab3:
    if double_dippers:
        for c in sorted(double_dippers, key=lambda x: -len(x.get("ge_categories_all", x.get("ge_categories", [])))):
            cats_all = c.get("ge_categories_all", c.get("ge_categories", []))
            cats_rem = c.get("ge_categories", [])
            with st.container(border=True):
                st.markdown(f"**{c['course_code']}** — {c['course_name']}")
                pills = "".join(f'<span class="byu-pill byu-pill-remaining">{cat}</span>' for cat in cats_rem)
                st.markdown(pills, unsafe_allow_html=True)
                st.caption(f"Covers {len(cats_all)} categories · {len(cats_rem)} still needed")
    else:
        st.info("No double-dipping courses in this selection.")

st.divider()

# ── Schedule Generator (locked courses only, respect blackout) ───────
if locked_courses:
    st.markdown("## Schedule Generator")
    st.caption("Conflict-free section combinations for your locked courses, excluding your blackout times.")

    start_options = ["Early (7–9am)", "Mid (9–11am)", "Late (11am+)"]
    start_idx = min(["Early", "Mid", "Late"].index(preferred_start) if preferred_start in ("Early", "Mid", "Late") else 1, 2)
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
        # Filter out sections that conflict with blackout
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
        sel = st.radio("Schedule option", names, index=min(idx, len(opts) - 1), key="sched_choice", horizontal=True)
        st.session_state.schedule_index = names.index(sel)
        selection = opts[st.session_state.schedule_index]
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        colors = ["#0062B8", "#1B5E20", "#B71C1C", "#E65100", "#4A148C", "#004D40"]
        course_colors = {c[0].get("course_code"): colors[i % len(colors)] for i, c in enumerate(selection)}

        def _time_label(slot):
            h = 7 + slot // 2
            m = (slot % 2) * 30
            if h < 12:
                return f"{h}:{m:02d} am"
            if h == 12:
                return f"12:{m:02d} pm"
            return f"{h-12}:{m:02d} pm"

        grid_html = '<div class="sched-grid" style="grid-template-rows: 32px repeat(22, 28px);">'
        grid_html += '<div class="sched-cell time"></div>' + "".join(f'<div class="sched-cell day">{d}</div>' for d in day_names)
        for slot in range(22):
            grid_html += f'<div class="sched-cell time">{_time_label(slot)}</div>'
            for day_idx in range(5):
                parts = []
                for course, sec in selection:
                    days_set = sec.get("days_set") or set()
                    if day_idx not in days_set:
                        continue
                    start_t = sec.get("start_time")
                    end_t = sec.get("end_time")
                    if start_t is None or end_t is None:
                        continue
                    slot_start = 7 + slot / 2
                    slot_end = 7 + (slot + 1) / 2
                    if slot_start < end_t and slot_end > start_t:
                        color = course_colors.get(course.get("course_code"), "#666")
                        parts.append(f'<div class="sched-block" style="background:{color}"><span class="code">{course.get("course_code", "")}</span><br>{sec.get("instructor_name", "TBA")}<br>{sec.get("room", "") or "—"}</div>')
                grid_html += f'<div class="sched-cell">{"".join(parts)}</div>'
        grid_html += "</div>"
        st.markdown(grid_html, unsafe_allow_html=True)

        export_text = format_schedule_for_export(selection)
        st.download_button(
            "Copy to Clipboard / Download as text",
            data=export_text,
            file_name="byu_schedule.txt",
            mime="text/plain",
            key="sched_export",
        )
        st.caption("Paste into Google Calendar or import as plain text. Each block shows course code, professor, and room.")
