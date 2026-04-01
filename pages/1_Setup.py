"""
BYU GE Optimizer — Setup page (page 1).
Dark-theme hero, input tabs (MyMap CAS / PDF / Manual), blackout grid, preferences, CTA.
"""
import streamlit as st

from styles import inject_styles
from scraper import GE_CATEGORIES
from pdf_parser import parse_degree_audit, HAS_PDFPLUMBER
from ge_requirements import GE_REQUIREMENTS, is_category_complete
from pathways import get_remaining_requirements
from calendar_component import blackout_calendar as _blackout_calendar
from major_scraper import get_major_options_for_ui
from major_requirements import MajorSolver

inject_styles()

# ── Session state defaults ───────────────────────────────────────

for key, default in [
    ("courses_taken", set()),
    ("completed_categories", None),
    ("remaining_categories", None),
    ("pathway_state", None),
    ("data_source", None),
    ("net_id", None),
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
    ("dw_debug", None),
    ("major_slug", None),
    ("major_state", None),
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
st.markdown("""
<div class="byu-hero">
  <div class="byu-hero-eyebrow">BYU General Education</div>
  <div class="byu-hero-title">Find your shortest path to graduation</div>
  <div class="byu-hero-sub">
    Connect your BYU account or upload your degree audit &mdash; we&rsquo;ll find
    the minimum courses to complete all 13 GE requirements, ranked by professor ratings.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Step 1: Import degree audit ───────────────────────────────────
st.markdown("""
<div class="byu-step-header">
  <div class="byu-step-num">1</div>
  <div>
    <div class="byu-step-title">Import your degree audit</div>
    <div class="byu-step-desc">Tell us what you&rsquo;ve taken so far</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab_pdf, tab_manual = st.tabs(["📄 Upload PDF", "✏️ Manual Entry"])

# ── Tab 1: PDF upload ─────────────────────────────────────────────

# ── Tab 2: Upload PDF ──────────────────────────────────────────────
with tab_pdf:
    col_upload = st.columns([1, 3, 1])
    with col_upload[1]:
        st.markdown(
            '<div class="byu-privacy-note">'
            '&#128274; Your PDF is processed in-memory only and never stored or shared.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
**How to get your degree audit PDF:**
1. Open **[mymap.byu.edu](https://mymap.byu.edu)** in a new tab and log in with your BYU NetID.
2. Click **Degree Audit** in the sidebar.
3. Press **Ctrl/Cmd+P → Save as PDF** in your browser.
4. Upload that PDF here.
""")
        uploaded_pdf = st.file_uploader(
            "Upload BYU MyMap Degree Audit PDF",
            type=["pdf"],
            help="MyMap > Degree Audit > Print > Save as PDF",
            key="setup_pdf_upload",
        )

    if uploaded_pdf is not None:
        if not HAS_PDFPLUMBER:
            st.error("pdfplumber is not installed. Use Manual Entry instead.")
            st.session_state.manual_override = True
        else:
            with st.spinner("Parsing PDF..."):
                parse_result = parse_degree_audit(uploaded_pdf)
            if parse_result["error"]:
                st.warning(
                    f"Could not fully parse PDF: {parse_result['error']}. "
                    "Use Manual Entry instead."
                )
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
                    st.session_state.pathway_state = get_remaining_requirements(
                        courses_taken, completed
                    )
                st.success(
                    f"PDF parsed ({parse_result['parse_confidence']} confidence). "
                    f"**{len(completed)}** GE categories complete, "
                    f"**{len(courses_taken)}** courses detected."
                )

# ── Tab 3: Manual Entry ────────────────────────────────────────────
with tab_manual:
    st.caption("Check every GE requirement you have already completed.")
    all_cats = sorted(GE_CATEGORIES.keys())
    default_checked = sorted(
        st.session_state.completed_categories
        or st.session_state.manual_completed
        or set()
    )
    manual_cols = st.columns(2)
    manual_selected: set = set()
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
        st.success(
            f"**{len(manual_selected)}** complete, "
            f"**{len(st.session_state.remaining_categories)}** remaining."
        )
        st.rerun()

# ── Progress pills ─────────────────────────────────────────────────
if st.session_state.completed_categories is not None and st.session_state.data_source:
    _none_span = '<span style="color:#5A6478;font-size:0.85rem;">None</span>'
    done_html = "".join(
        f'<span class="byu-pill byu-pill-done">&#10003; {cat}</span>'
        for cat in sorted(st.session_state.completed_categories)
    )
    rem = st.session_state.remaining_categories or set()
    rem_html = "".join(
        f'<span class="byu-pill byu-pill-remaining">{cat}</span>'
        for cat in sorted(rem)
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

# ── Major selection ────────────────────────────────────────────────
st.markdown("""
<div class="byu-step-header">
  <div class="byu-step-num">2</div>
  <div>
    <div class="byu-step-title">Select your major <span style="font-weight:400;font-size:0.85em;opacity:0.7">(optional)</span></div>
    <div class="byu-step-desc">Finds courses that satisfy both your major requirements and GE credits</div>
  </div>
</div>
""", unsafe_allow_html=True)

_major_options = get_major_options_for_ui()
_major_labels = ["— No major selected —"] + [name for name, slug, college in _major_options]
_major_slugs  = [None] + [slug for name, slug, college in _major_options]
_current_slug_idx = _major_slugs.index(st.session_state.major_slug) if st.session_state.major_slug in _major_slugs else 0
_selected_label = st.selectbox("Your major", options=_major_labels, index=_current_slug_idx, key="major_select")
_new_slug = _major_slugs[_major_labels.index(_selected_label)]
if _new_slug != st.session_state.major_slug:
    st.session_state.major_slug = _new_slug
    st.session_state.major_state = None
    st.session_state.results = None

if st.session_state.major_slug:
    _solver = MajorSolver()
    _taken = st.session_state.get("courses_taken") or set()
    _mstate = _solver.solve(st.session_state.major_slug, _taken)
    st.session_state.major_state = _mstate
    st.progress(_mstate.completion_pct, text=f"{int(_mstate.completion_pct * 100)}% of major requirements complete")
    _mcol1, _mcol2 = st.columns(2)
    with _mcol1:
        st.markdown("**Completed**")
        for gs in _mstate.completed_groups:
            st.markdown(f'<span class="byu-pill byu-pill-done">&#10003; {gs.group.group_name}</span>', unsafe_allow_html=True)
        if not _mstate.completed_groups:
            st.caption("None yet")
    with _mcol2:
        st.markdown("**Still needed**")
        for gs in _mstate.remaining_groups:
            still = f" ({gs.courses_still_needed} more)" if gs.courses_still_needed > 1 else ""
            st.markdown(f'<span class="byu-pill byu-pill-remaining">{gs.group.group_name}{still}</span>', unsafe_allow_html=True)
        if not _mstate.remaining_groups:
            st.success("All major requirements complete!")

st.divider()

# ── Step 4: Blackout times ─────────────────────────────────────────
st.markdown("""
<div class="byu-step-header">
  <div class="byu-step-num">4</div>
  <div>
    <div class="byu-step-title">When are you unavailable?</div>
    <div class="byu-step-desc">Blocked slots are excluded from recommended sections</div>
  </div>
</div>
""", unsafe_allow_html=True)

_current_selected = [list(cell) for cell in st.session_state.blackout_cells]
raw = _blackout_calendar(selected=_current_selected, key="blackout_cal", default=_current_selected)
if raw is not None:
    new_cells = set(tuple(pair) for pair in raw)
    if new_cells != st.session_state.blackout_cells:
        st.session_state.blackout_cells = new_cells

st.divider()

# ── Step 5: Preferences ────────────────────────────────────────────
st.markdown("""
<div class="byu-step-header">
  <div class="byu-step-num">5</div>
  <div>
    <div class="byu-step-title">Preferences</div>
    <div class="byu-step-desc">Tune the optimizer to your schedule</div>
  </div>
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
    st.warning(
        "Connect to MyMap, upload your degree audit PDF, or use Manual Entry "
        "before running the optimizer."
    )
else:
    st.session_state.blackout_slots = _blackout_slots_from_cells(st.session_state.blackout_cells)

if st.button("Find My GE Courses", type="primary", key="goto_results"):
    if st.session_state.completed_categories is None and not st.session_state.manual_completed:
        st.error("Please connect to MyMap, upload a PDF, or use Manual Entry first.")
    else:
        st.session_state.setup_done = True
        st.session_state.blackout_slots = _blackout_slots_from_cells(
            st.session_state.blackout_cells
        )
        st.switch_page("pages/2_Results.py")
