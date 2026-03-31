"""
BYU GE Optimizer — Setup page (page 1).
Hero, PDF upload, blackout times grid, preferences, CTA to Results.
"""

import os
import streamlit as st
import streamlit.components.v1 as components
from styles import inject_styles
from scraper import GE_CATEGORIES
from pdf_parser import parse_degree_audit, HAS_PDFPLUMBER
from ge_requirements import GE_REQUIREMENTS, is_category_complete
from pathways import get_remaining_requirements

_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "components", "blackout_calendar")
_blackout_calendar = components.declare_component("blackout_calendar", path=_COMPONENT_DIR)

inject_styles()

# ── Session state defaults ───────────────────────────────────────

for key, default in [
    ("courses_taken", set()),
    ("completed_categories", None),
    ("remaining_categories", None),
    ("pathway_state", None),
    ("data_source", None),
    ("pdf_confidence", None),
    ("pdf_parse_error", None),
    ("manual_override", False),
    ("manual_completed", set()),
    ("blackout_cells", set()),  # set of (day_index 0-4, slot_index 0-27)
    ("blackout_slots", []),     # list of (day, start_time, end_time) for Results
    ("preferred_days", "No preference"),
    ("preferred_start", "Mid"),
    ("minimize_gaps", True),
    ("setup_done", False),
    ("results", None),
    ("uncovered", set()),
    ("locked_courses", []),
    ("schedule_options", None),
    ("schedule_index", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def _completed_from_courses(courses_taken: set) -> set:
    return {cat for cat in GE_REQUIREMENTS if is_category_complete(cat, courses_taken)}


def _blackout_slots_from_cells(cells: set) -> list:
    """Convert set of (day, slot_index) to list of (day, start_time, end_time)."""
    return [
        (day, 7.0 + slot * 0.5, 7.0 + (slot + 1) * 0.5)
        for (day, slot) in cells
    ]


# ── Hero ──────────────────────────────────────────────────────────
st.markdown("""
<div class="byu-hero">
    <h1>BYU GE Optimizer</h1>
    <p class="byu-hero-desc">Find the minimum number of courses to finish your General Education requirements—with professor ratings and a schedule that fits your availability.</p>
</div>
""", unsafe_allow_html=True)

# ── PDF upload card ───────────────────────────────────────────────
st.markdown("## Step 1 — Import Your Degree Audit")
st.markdown('<div class="byu-card byu-card-upload">', unsafe_allow_html=True)
col_upload = st.columns([1, 2, 1])
with col_upload[1]:
    st.markdown("""
**How to get your degree audit PDF:**
1. Open **[mymap.byu.edu](https://mymap.byu.edu)** in a new tab and log in with your BYU NetID.
2. Click **Degree Audit** in the sidebar.
3. In your browser, press **File → Print → Save as PDF** (or Ctrl/Cmd+P → Save as PDF).
4. Upload that PDF here.
""")
    st.info("Your PDF is processed in your browser only and is never stored or shared.")
    uploaded_pdf = st.file_uploader(
        "Upload BYU MyMap Degree Audit PDF",
        type=["pdf"],
        help="MyMap → Degree Audit → Print → Save as PDF",
        key="setup_pdf_upload",
    )
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_pdf is not None:
    if not HAS_PDFPLUMBER:
        st.error("pdfplumber is not installed. Use Manual Entry below.")
        st.session_state.manual_override = True
    else:
        with st.spinner("Parsing PDF..."):
            parse_result = parse_degree_audit(uploaded_pdf)
        if parse_result["error"]:
            st.warning(f"Could not fully parse PDF: {parse_result['error']}. Use Manual Entry.")
            st.session_state.manual_override = True
        elif parse_result["parse_confidence"] == "low":
            st.warning("Low confidence parse — verify below or use Manual Entry.")
            st.session_state.completed_categories = parse_result["completed"]
            st.session_state.remaining_categories = parse_result["remaining"]
            st.session_state.manual_override = True
        else:
            courses_taken = parse_result.get("courses_taken", set())
            completed = _completed_from_courses(courses_taken)
            remaining = set(GE_CATEGORIES.keys()) - completed
            st.session_state.completed_categories = completed
            st.session_state.remaining_categories = remaining
            st.session_state.pdf_confidence = parse_result["parse_confidence"]
            st.session_state.courses_taken = courses_taken
            st.session_state.manual_override = False
            st.session_state.data_source = "pdf"
            if courses_taken:
                st.session_state.pathway_state = get_remaining_requirements(courses_taken, completed)
            st.success(
                f"PDF parsed ({parse_result['parse_confidence']} confidence). "
                f"**{len(completed)}** completed, **{len(courses_taken)}** courses detected."
            )

# Manual entry tab
with st.expander("✏️ Manual Entry — select completed GE categories", expanded=st.session_state.manual_override):
    st.caption("Check every requirement you've already completed.")
    all_cats = sorted(GE_CATEGORIES.keys())
    default_checked = sorted(st.session_state.completed_categories or st.session_state.manual_completed or set())
    manual_cols = st.columns(2)
    manual_selected = set()
    for i, cat in enumerate(all_cats):
        col = manual_cols[i % 2]
        if col.checkbox(cat, value=(cat in default_checked), key=f"manual_{cat}"):
            manual_selected.add(cat)
    if st.button("Apply Manual Selection", key="apply_manual"):
        st.session_state.manual_completed = manual_selected
        st.session_state.completed_categories = manual_selected
        st.session_state.remaining_categories = set(GE_CATEGORIES.keys()) - manual_selected
        st.session_state.data_source = "manual"
        st.session_state.manual_override = False
        st.success(f"**{len(manual_selected)}** complete → **{len(st.session_state.remaining_categories)}** remaining.")
        st.rerun()

# Progress pills when we have data
if st.session_state.completed_categories is not None and st.session_state.data_source:
    st.markdown('<div class="byu-progress-section">', unsafe_allow_html=True)
    st.markdown('<p class="byu-progress-title">Completed</p>', unsafe_allow_html=True)
    _none_span = '<span style="color:#888;">None</span>'
    done_html = "".join(
        f'<span class="byu-pill byu-pill-done">✓ {cat}</span>'
        for cat in sorted(st.session_state.completed_categories)
    )
    st.markdown(f'<div class="byu-card">{done_html or _none_span}</div>', unsafe_allow_html=True)
    st.markdown('<p class="byu-progress-title">Remaining</p>', unsafe_allow_html=True)
    rem = st.session_state.remaining_categories or set()
    rem_html = "".join(
        f'<span class="byu-pill byu-pill-remaining">{cat}</span>' for cat in sorted(rem)
    )
    st.markdown(f'<div class="byu-card">{rem_html or _none_span}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ── Blackout times ─────────────────────────────────────────────────
st.markdown("## Step 2 — When are you unavailable?")
st.caption("Click and drag to block times (navy). Drag again to unblock. Blocked times are excluded from recommended sections.")

# Convert stored set of (day, slot) tuples to list-of-lists for the component
_current_selected = [list(cell) for cell in st.session_state.blackout_cells]

raw = _blackout_calendar(selected=_current_selected, key="blackout_cal", default=_current_selected)

# raw is a list of [day, slot] pairs returned by the component
if raw is not None:
    new_cells = set(tuple(pair) for pair in raw)
    if new_cells != st.session_state.blackout_cells:
        st.session_state.blackout_cells = new_cells

st.divider()

# ── Preferences ────────────────────────────────────────────────────
st.markdown("## Step 3 — Preferences")
pref_col1, pref_col2 = st.columns(2)
with pref_col1:
    st.session_state.preferred_days = st.radio(
        "Preferred class days",
        options=["MWF", "TTh", "No preference"],
        index=["MWF", "TTh", "No preference"].index(st.session_state.preferred_days),
        key="pref_days",
        horizontal=True,
    )
    st.session_state.preferred_start = st.radio(
        "Preferred start time",
        options=["Early", "Mid", "Late"],
        index=["Early", "Mid", "Late"].index(st.session_state.preferred_start),
        key="pref_start",
        horizontal=True,
    )
with pref_col2:
    st.session_state.minimize_gaps = st.checkbox(
        "Minimize gaps between classes",
        value=st.session_state.minimize_gaps,
        key="pref_gaps",
    )

st.divider()

# ── CTA: Find My GE Courses ───────────────────────────────────────
if st.session_state.completed_categories is None and not st.session_state.manual_completed:
    st.warning("Upload your degree audit PDF or use Manual Entry before running the optimizer.")
else:
    # Persist blackout as list of (day, start, end) for Results page
    st.session_state.blackout_slots = _blackout_slots_from_cells(st.session_state.blackout_cells)

if st.button("Find My GE Courses →", type="primary", key="goto_results"):
    if st.session_state.completed_categories is None and not st.session_state.manual_completed:
        st.error("Please upload a PDF or use Manual Entry first.")
    else:
        st.session_state.setup_done = True
        st.session_state.blackout_slots = _blackout_slots_from_cells(st.session_state.blackout_cells)
        st.switch_page("pages/2_Results.py")
