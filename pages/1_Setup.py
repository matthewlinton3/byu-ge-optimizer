"""
BYU GE Optimizer — Setup page (page 1).
Hero, PDF upload, blackout times grid, preferences, CTA to Results.
"""

import streamlit as st
from styles import inject_styles
from scraper import GE_CATEGORIES
from pdf_parser import parse_degree_audit, HAS_PDFPLUMBER
from ge_requirements import GE_REQUIREMENTS, is_category_complete
from pathways import get_remaining_requirements

inject_styles()

# ── Session state defaults ───────────────────────────────────────
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri"]
SLOTS_7AM_9PM = 28  # 7:00–9:00 pm = 28 half-hour slots

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
    ("blackout_cells", set()),
    ("blackout_slots", []),
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
    return [
        (day, 7.0 + slot * 0.5, 7.0 + (slot + 1) * 0.5)
        for (day, slot) in cells
    ]


# ── Hero ──────────────────────────────────────────────────────────
# Use div.byu-hero-title (NOT <h1>) so Streamlit's heading color
# overrides can't touch it. The hero CSS forces color: #FFFFFF.
st.markdown("""
<div class="byu-hero">
  <div class="byu-hero-title">BYU GE Optimizer</div>
  <div class="byu-hero-desc">
    Find the minimum number of courses to finish your General Education
    requirements&mdash;with professor ratings and a schedule that fits your life.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Step 1: Import degree audit ───────────────────────────────────
st.markdown("""
<div class="byu-step">
  <div class="byu-step-num">1</div>
  <div class="byu-step-label">Import your degree audit</div>
</div>
""", unsafe_allow_html=True)

col_upload = st.columns([1, 3, 1])
with col_upload[1]:
    st.markdown(
        '<div class="byu-privacy-note">&#128274; Your PDF is processed in-memory only and never stored or shared.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("How to get your MyMap degree audit PDF", expanded=False):
        st.markdown("""
1. Go to [mymap.byu.edu](https://mymap.byu.edu) and log in.
2. Open **Degree Audit** from the sidebar.
3. In your browser use **Print &rarr; Save as PDF**.
4. Upload the saved PDF below.
        """)
    uploaded_pdf = st.file_uploader(
        "Upload BYU MyMap Degree Audit PDF",
        type=["pdf"],
        help="MyMap > Degree Audit > Print > Save as PDF",
        key="setup_pdf_upload",
    )

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

# Manual entry
with st.expander("Manual Entry — check off completed GE categories", expanded=st.session_state.manual_override):
    st.caption("Check every requirement you have already completed.")
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
        n_done = len(manual_selected)
        n_rem = len(st.session_state.remaining_categories)
        st.success(f"**{n_done}** complete, **{n_rem}** remaining.")
        st.rerun()

# Progress pills when we have data
if st.session_state.completed_categories is not None and st.session_state.data_source:
    _none_span = '<span style="color:#aaa;font-size:0.85rem;">None</span>'
    done_html = "".join(
        f'<span class="byu-pill byu-pill-done">&#10003; {cat}</span>'
        for cat in sorted(st.session_state.completed_categories)
    )
    rem = st.session_state.remaining_categories or set()
    rem_html = "".join(
        f'<span class="byu-pill byu-pill-remaining">{cat}</span>' for cat in sorted(rem)
    )
    st.markdown(f"""
<div style="margin:1.5rem 0 0.5rem">
  <p class="byu-progress-title">Completed</p>
  <div class="byu-card" style="padding:1rem 1.25rem">{done_html or _none_span}</div>
  <p class="byu-progress-title" style="margin-top:0.75rem">Remaining</p>
  <div class="byu-card" style="padding:1rem 1.25rem">{rem_html or _none_span}</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Step 2: Blackout times ─────────────────────────────────────────
st.markdown("""
<div class="byu-step">
  <div class="byu-step-num">2</div>
  <div class="byu-step-label">When are you unavailable?</div>
</div>
""", unsafe_allow_html=True)
st.caption("Click a slot to block it. Blocked times will be excluded from recommended sections.")

blackout_cells = set(st.session_state.blackout_cells)
qf1, qf2, qf3 = st.columns(3)
with qf1:
    if st.button("Block mornings before 9am", key="qf_mornings"):
        for d in range(5):
            for s in range(4):
                blackout_cells.add((d, s))
        st.session_state.blackout_cells = blackout_cells
        st.rerun()
with qf2:
    if st.button("Block evenings after 6pm", key="qf_evenings"):
        for d in range(5):
            for s in range(22, 28):
                blackout_cells.add((d, s))
        st.session_state.blackout_cells = blackout_cells
        st.rerun()
with qf3:
    if st.button("Clear all blackout times", key="qf_clear"):
        st.session_state.blackout_cells = set()
        st.rerun()


def _time_label(slot: int) -> str:
    h = 7 + slot // 2
    m = (slot % 2) * 30
    if h < 12:
        return f"{h}:{m:02d}am"
    if h == 12:
        return f"12:{m:02d}pm"
    return f"{h - 12}:{m:02d}pm"


new_blackout_cells = set()
for slot in range(SLOTS_7AM_9PM):
    cols = st.columns([1] + [1] * 5)
    with cols[0]:
        st.caption(_time_label(slot))
    for day in range(5):
        with cols[day + 1]:
            if st.checkbox(
                DAY_NAMES[day][0],
                value=(day, slot) in blackout_cells,
                key=f"bo_{day}_{slot}",
                label_visibility="collapsed",
            ):
                new_blackout_cells.add((day, slot))
st.session_state.blackout_cells = new_blackout_cells

st.divider()

# ── Step 3: Preferences ────────────────────────────────────────────
st.markdown("""
<div class="byu-step">
  <div class="byu-step-num">3</div>
  <div class="byu-step-label">Preferences</div>
</div>
""", unsafe_allow_html=True)

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

# ── CTA ────────────────────────────────────────────────────────────
if st.session_state.completed_categories is None and not st.session_state.manual_completed:
    st.warning("Upload your degree audit PDF or use Manual Entry before running the optimizer.")
else:
    st.session_state.blackout_slots = _blackout_slots_from_cells(st.session_state.blackout_cells)

if st.button("Find My GE Courses", type="primary", key="goto_results"):
    if st.session_state.completed_categories is None and not st.session_state.manual_completed:
        st.error("Please upload a PDF or use Manual Entry first.")
    else:
        st.session_state.setup_done = True
        st.session_state.blackout_slots = _blackout_slots_from_cells(st.session_state.blackout_cells)
        st.switch_page("pages/2_Results.py")
