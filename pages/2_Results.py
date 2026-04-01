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

inject_styles()

# ── Redirect if Setup was not completed ───────────────────────────
if not st.session_state.get("setup_done") or st.session_state.get("completed_categories") is None:
    st.warning("Please complete Setup first: upload your degree audit and click **Find My GE Courses**.")
    if st.button("Go to Setup"):
        st.switch_page("pages/1_Setup.py")
    st.stop()

completed_categories = st.session_state.completed_categories or set()
remaining_categories = st.session_state.remaining_categories or set(GE_CATEGORIES.keys())
courses_taken = st.session_state.get("courses_taken") or set()
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


if st.session_state.get("results") is None or st.session_state.get("uncovered") is None:
    selected, uncovered = run_optimizer(
        use_ilp, skip_rmp, refresh, remaining_categories, courses_taken
    )
    st.session_state.results = selected
    st.session_state.uncovered = uncovered
    st.rerun()

selected = list(st.session_state.results)
uncovered = st.session_state.uncovered

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
m1.metric("Courses to take", len(selected))
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


# ── Results tabs ───────────────────────────────────────────────────
_tab_labels = ["Recommended Courses", "Full GE Map", "Double-Dippers"]
if major_slug:
    _tab_labels.append("Major Requirements")
_tabs = st.tabs(_tab_labels)
tab1, tab2, tab3 = _tabs[0], _tabs[1], _tabs[2]
tab_major = _tabs[3] if major_slug else None

with tab1:
    st.caption(f"Sorted by: **{sort_priority}**.")

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

    # CSV export
    rows = []
    for c in selected:
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

