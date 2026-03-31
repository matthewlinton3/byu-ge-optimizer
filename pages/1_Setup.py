"""
BYU GE Optimizer — Setup page (page 1).
Dark-theme hero, input tabs (MyMap CAS / PDF / Manual), blackout grid, preferences, CTA.
"""
import os

import streamlit as st

from styles import inject_styles
from scraper import GE_CATEGORIES
from pdf_parser import parse_degree_audit, HAS_PDFPLUMBER
from ge_requirements import GE_REQUIREMENTS, is_category_complete
from pathways import get_remaining_requirements
from cas_auth import cas_login_url, cas_validate_ticket
from degreeworks_scraper import scrape_degreeworks_sync
from calendar_component import blackout_calendar as _blackout_calendar

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


def _service_url() -> str:
    """Build the CAS service_url pointing back to this page."""
    base = os.environ.get(
        "APP_BASE_URL",
        "https://byu-ge-optimizer-production.up.railway.app",
    ).rstrip("/")
    return f"{base}/Setup"


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

tab_mymap, tab_pdf, tab_manual = st.tabs(
    ["🔗 Log in to MyMap", "📄 Upload PDF", "✏️ Manual Entry"]
)

# ── Tab 1: MyMap — CAS OAuth redirect flow ────────────────────────
with tab_mymap:

    service_url = _service_url()
    ticket = st.query_params.get("ticket")

    # ── Case A: CAS just redirected back with a ticket ────────────
    if ticket:
        with st.spinner("Verifying BYU login..."):
            validated = cas_validate_ticket(ticket, service_url)

        if not validated:
            st.error("BYU login failed or ticket expired. Please try again.")
            st.query_params.clear()
        else:
            net_id = validated["user"]
            st.success(f"Authenticated as **{net_id}** — loading your degree audit…")

            with st.spinner("Loading DegreeWorks degree audit..."):
                try:
                    import requests as _req
                    sess = _req.Session()
                    # Exchange the CAS ticket for DegreeWorks session cookies
                    sess.get(
                        f"https://degreeworks.byu.edu?ticket={ticket}",
                        allow_redirects=True,
                        timeout=15,
                    )
                    cas_cookies = [
                        {
                            "name": c.name,
                            "value": c.value,
                            "domain": c.domain or ".byu.edu",
                            "path": c.path or "/",
                        }
                        for c in sess.cookies
                    ]
                    dw_data = scrape_degreeworks_sync(cas_cookies)
                    st.session_state.dw_debug = {
                        k: v for k, v in dw_data.items() if k != "raw_html"
                    }

                    courses_taken = set(dw_data.get("courses_taken") or [])
                    completed = (
                        set(dw_data.get("completed_ge") or [])
                        | _completed_from_courses(courses_taken)
                    )
                    remaining = set(GE_CATEGORIES.keys()) - completed

                    st.session_state.completed_categories = completed
                    st.session_state.remaining_categories = remaining
                    st.session_state.courses_taken = courses_taken
                    st.session_state.net_id = net_id
                    st.session_state.data_source = "mymap"
                    st.session_state.manual_override = False
                    if courses_taken:
                        st.session_state.pathway_state = get_remaining_requirements(
                            courses_taken, completed
                        )

                    st.success(
                        f"Loaded! **{len(courses_taken)}** courses detected, "
                        f"**{len(completed)}** GE categories complete."
                    )
                    # Clear the one-time ticket from the URL
                    st.query_params.clear()

                except Exception as exc:
                    st.error(f"Could not load DegreeWorks: {exc}")
                    st.caption(
                        "Try again, or use **Upload PDF** / **Manual Entry** instead."
                    )
                    st.query_params.clear()

    # ── Case B: Already authenticated this session ─────────────────
    elif st.session_state.get("data_source") == "mymap":
        uid = st.session_state.get("net_id", "BYU user")
        n_done = len(st.session_state.get("completed_categories") or set())
        st.success(
            f"Connected as **{uid}** &mdash; **{n_done}** GE categories complete."
        )
        if st.button("Disconnect", key="mymap_disconnect"):
            for k in ["completed_categories", "remaining_categories", "courses_taken",
                      "net_id", "data_source", "pathway_state", "dw_debug",
                      "results", "uncovered"]:
                st.session_state[k] = None
            st.rerun()

    # ── Case C: Not yet connected — show link button ───────────────
    else:
        col_c = st.columns([1, 2, 1])
        with col_c[1]:
            if hasattr(st, "html"):
                st.html("""
<div style="text-align:center; padding: 1.5rem 0 0.75rem;">
  <div style="color:#8892A4; font-size:0.9rem; line-height:1.6; margin-bottom:1.5rem;">
    Sign in with your BYU account. Duo two-factor authentication works normally
    &mdash; you complete it on BYU&rsquo;s own login page, not here.
  </div>
</div>
""")
            login_url = cas_login_url(service_url)
            try:
                st.link_button(
                    "Connect MyMap via BYU Login",
                    login_url,
                    use_container_width=True,
                )
            except AttributeError:
                st.markdown(
                    f'<div style="text-align:center; margin-bottom:1rem;">'
                    f'<a href="{login_url}" target="_self" style="'
                    f'display:inline-block; background:#0062B8; color:#fff; '
                    f'padding:0.6rem 1.8rem; border-radius:8px; font-weight:600; '
                    f'text-decoration:none; font-size:0.95rem;">Connect MyMap via BYU Login</a>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            if hasattr(st, "html"):
                st.html("""
<div style="text-align:center; margin-top:1rem; color:#5A6478; font-size:0.75rem;">
  You&rsquo;ll be redirected to BYU&rsquo;s secure login page.
  Your credentials never touch this server.
</div>
""")

    # Debug expander (always rendered if debug data exists)
    if st.session_state.get("dw_debug"):
        with st.expander("Debug — DegreeWorks parse details", expanded=False):
            st.json(st.session_state.dw_debug)

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

# ── Step 2: Blackout times ─────────────────────────────────────────
st.markdown("""
<div class="byu-step-header">
  <div class="byu-step-num">2</div>
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

# ── Step 3: Preferences ────────────────────────────────────────────
st.markdown("""
<div class="byu-step-header">
  <div class="byu-step-num">3</div>
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
