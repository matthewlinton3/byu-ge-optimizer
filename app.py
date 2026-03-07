"""
BYU GE Optimizer — Streamlit Web App
BYU brand UI: IBM Plex Sans, navy #002E5D, royal blue #0062B8.
"""

import streamlit as st
import pandas as pd
from scraper import scrape_catalog_for_ge, GE_CATEGORIES, init_db
from optimizer import optimize
from rmp import enrich_with_rmp
from pdf_parser import parse_degree_audit, HAS_PDFPLUMBER
from pathways import get_remaining_requirements
from ge_requirements import GE_REQUIREMENTS, is_category_complete

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="BYU GE Optimizer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── BYU Brand Design System ─────────────────────────────────────
# IBM Plex Sans, navy #002E5D, royal blue #0062B8, white, #F5F5F5 cards, #333333 body
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
    --byu-navy: #002E5D;
    --byu-royal: #0062B8;
    --byu-white: #FFFFFF;
    --byu-gray: #F5F5F5;
    --byu-text: #333333;
    --byu-text-muted: #666666;
    --byu-border: #E0E0E0;
}
html, body, .stApp { background-color: var(--byu-white) !important; }
.main .block-container {
    padding-top: 0;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* Typography — IBM Plex Sans */
h1, h2, h3, h4, p, li, span, label, .stCaption,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3,
[data-testid="stCaptionContainer"] {
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}
h1, h2, h3, h4,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
    color: var(--byu-text) !important;
    font-weight: 600 !important;
}
p, li, span, label, .stCaption { color: var(--byu-text) !important; }

/* Hero — navy background */
.byu-hero {
    background: var(--byu-navy);
    color: var(--byu-white);
    padding: 2.5rem 1.5rem;
    margin: -1rem -1rem 1.5rem -1rem;
    border-radius: 0;
    text-align: center;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.byu-hero h1 {
    color: var(--byu-white) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.5rem 0 !important;
    letter-spacing: -0.02em;
}
.byu-hero .byu-hero-desc {
    color: rgba(255,255,255,0.9);
    font-size: 1rem;
    font-weight: 400;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Cards — light gray background */
.byu-card {
    background: var(--byu-gray);
    border: 1px solid var(--byu-border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.byu-card-upload {
    max-width: 560px;
    margin-left: auto;
    margin-right: auto;
    text-align: center;
}

/* Course result cards */
.byu-course-card {
    background: var(--byu-white);
    border: 1px solid var(--byu-border);
    border-left: 4px solid var(--byu-royal);
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.byu-course-card .course-title { font-weight: 600; color: var(--byu-navy); font-size: 1.05rem; }
.byu-course-card .course-code { color: var(--byu-royal); font-weight: 600; }
.byu-course-card .ge-pills { margin: 0.5rem 0; }
.byu-course-card .prof-row { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #eee; font-size: 0.9rem; color: var(--byu-text); }
.byu-course-card .prof-name { font-weight: 500; }
.byu-course-card .stars { color: #f5a623; }

/* Progress tracker */
.byu-progress-section { margin: 1.5rem 0; }
.byu-progress-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--byu-text-muted); margin-bottom: 0.5rem; }
.byu-pill { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500; margin: 3px 4px 3px 0; font-family: 'IBM Plex Sans', sans-serif; }
.byu-pill-done { background: #E8F4EA; color: #1B5E20; }
.byu-pill-remaining { background: #E3F2FD; color: var(--byu-navy); }
.byu-pill-uncovered { background: #FFEBEE; color: #B71C1C; }

/* Buttons — royal blue primary */
button[data-testid="baseButton-primary"],
.stFormSubmitButton button {
    background: var(--byu-royal) !important;
    color: var(--byu-white) !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
}
button[data-testid="baseButton-primary"]:hover,
.stFormSubmitButton button:hover {
    background: #004C8C !important;
    color: var(--byu-white) !important;
}
.stButton > button:not([data-testid="baseButton-primary"]) {
    background: var(--byu-white) !important;
    color: var(--byu-navy) !important;
    border: 1.5px solid var(--byu-navy) !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stButton > button:hover:not([data-testid="baseButton-primary"]) {
    background: var(--byu-navy) !important;
    color: var(--byu-white) !important;
}

/* Sidebar — navy accent */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
    background: var(--byu-gray) !important;
}
section[data-testid="stSidebar"] * { color: var(--byu-text) !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: var(--byu-navy) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
section[data-testid="stSidebar"] [data-testid="stToggle"][aria-checked="true"],
section[data-testid="stSidebar"] [role="switch"][aria-checked="true"] { background: var(--byu-royal) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid var(--byu-border) !important; }
.stTabs [data-baseweb="tab"] {
    color: var(--byu-text-muted) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--byu-navy) !important;
    border-bottom: 2px solid var(--byu-royal) !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: var(--byu-royal) !important; }

/* Inputs */
.stTextInput input, .stTextArea textarea {
    border: 1px solid var(--byu-border) !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--byu-royal) !important;
    box-shadow: 0 0 0 2px rgba(0,98,184,0.15) !important;
}

/* File uploader */
[data-testid="stFileUploader"] > div {
    border: 2px dashed var(--byu-border) !important;
    border-radius: 12px !important;
    background: var(--byu-white) !important;
}
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"] {
    border-color: var(--byu-royal) !important;
    color: var(--byu-royal) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--byu-gray);
    border: 1px solid var(--byu-border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
}
div[data-testid="stMetricValue"] { color: var(--byu-navy) !important; font-weight: 600 !important; font-family: 'IBM Plex Sans', sans-serif !important; }
div[data-testid="stMetricLabel"] { color: var(--byu-text-muted) !important; font-size: 0.7rem !important; text-transform: uppercase; letter-spacing: 0.06em; }

/* Expanders */
[data-testid="stExpander"] {
    border: 1px solid var(--byu-border) !important;
    border-radius: 10px !important;
    background: var(--byu-gray) !important;
}
[data-testid="stExpander"] summary { font-weight: 500 !important; color: var(--byu-text) !important; }

/* Alerts — subtle BYU tint */
[data-testid="stInfo"] {
    background: #E3F2FD !important;
    border: 1px solid #BBDEFB !important;
    border-radius: 8px !important;
    color: var(--byu-navy) !important;
}
[data-testid="stSuccess"] { background: #E8F5E9 !important; border: 1px solid #C8E6C9 !important; border-radius: 8px !important; }
[data-testid="stWarning"] { background: #FFF8E1 !important; border: 1px solid #FFECB3 !important; border-radius: 8px !important; }
[data-testid="stError"] { background: #FFEBEE !important; border: 1px solid #FFCDD2 !important; border-radius: 8px !important; }

/* Progress bar */
[data-testid="stProgressBar"] > div > div { background: var(--byu-royal) !important; border-radius: 4px !important; }

/* Dividers */
hr { border-color: var(--byu-border) !important; margin: 1.25rem 0 !important; }

/* Vertical block border (containers with border) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--byu-border) !important;
    border-left: 4px solid var(--byu-royal) !important;
    border-radius: 10px !important;
    background: var(--byu-white) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero section ──────────────────────────────────────────────────
st.markdown("""
<div class="byu-hero">
    <h1>BYU GE Optimizer</h1>
    <p class="byu-hero-desc">Find the minimum number of courses to finish your General Education requirements—with professor ratings to choose the best classes.</p>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────
for key, default in [
    ("results", None),
    ("uncovered", set()),
    ("pdf_completed", None),
    ("pdf_remaining", None),
    ("pdf_parse_error", None),
    ("pdf_confidence", None),
    ("manual_override", False),
    ("manual_completed", set()),
    ("courses_taken", set()),
    ("pathway_state", None),
    ("data_source", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def _completed_from_courses(courses_taken: set) -> set:
    """Return GE categories completed (American Heritage needs 2 courses; Religion needs 14 credit hours)."""
    return {cat for cat in GE_REQUIREMENTS if is_category_complete(cat, courses_taken)}


# ════════════════════════════════════════════════════════════════
# STEP 1 — Import Degree Audit (centered card)
# ════════════════════════════════════════════════════════════════
st.markdown("## Step 1 — Import Your Degree Audit")

input_tab1, input_tab2 = st.tabs(["📄 Upload PDF", "✏️ Manual Entry"])

with input_tab1:
    st.markdown('<div class="byu-card byu-card-upload">', unsafe_allow_html=True)
    col_upload = st.columns([1, 2, 1])
    with col_upload[1]:
        st.info("🔒 Your PDF is processed in-memory only and never stored or shared.")
        with st.expander("How to get your MyMap degree audit PDF", expanded=False):
            st.markdown("""
1. Go to [mymap.byu.edu](https://mymap.byu.edu) and log in.
2. Open **Degree Audit** from the sidebar.
3. Use **Print → Save as PDF** in your browser.
4. Upload the saved PDF below.
            """)
        uploaded_pdf = st.file_uploader(
            "Upload BYU MyMap Degree Audit PDF",
            type=["pdf"],
            help="MyMap → Degree Audit → Save as PDF"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_pdf is not None:
        if not HAS_PDFPLUMBER:
            st.error("pdfplumber is not installed. Use Manual Entry instead.")
            st.session_state.manual_override = True
        else:
            with st.spinner("Parsing PDF..."):
                parse_result = parse_degree_audit(uploaded_pdf)

            if parse_result["error"]:
                st.warning(f"Could not fully parse PDF: {parse_result['error']}. Use Manual Entry.")
                st.session_state.manual_override = True
            elif parse_result["parse_confidence"] == "low":
                st.warning("Low confidence parse — verify below or use Manual Entry.")
                st.session_state.pdf_completed = parse_result["completed"]
                st.session_state.pdf_remaining = parse_result["remaining"]
                st.session_state.manual_override = True
            else:
                courses_taken = parse_result.get("courses_taken", set())
                completed = _completed_from_courses(courses_taken)
                remaining = set(GE_CATEGORIES.keys()) - completed
                st.session_state.pdf_completed = completed
                st.session_state.pdf_remaining = remaining
                st.session_state.pdf_confidence = parse_result["parse_confidence"]
                st.session_state.courses_taken = courses_taken
                st.session_state.manual_override = False
                st.session_state.data_source = "pdf"
                if courses_taken:
                    st.session_state.pathway_state = get_remaining_requirements(courses_taken, completed)
                st.success(f"PDF parsed ({parse_result['parse_confidence']} confidence). **{len(completed)}** completed, **{len(courses_taken)}** courses detected.")

    # Progress tracker: completed vs remaining (pills)
    if (
        st.session_state.pdf_completed is not None
        and not st.session_state.manual_override
        and st.session_state.data_source == "pdf"
    ):
        st.markdown('<div class="byu-progress-section">', unsafe_allow_html=True)
        st.markdown('<p class="byu-progress-title">Completed</p>', unsafe_allow_html=True)
        done_html = "".join(
            f'<span class="byu-pill byu-pill-done">✓ {cat}</span>'
            for cat in sorted(st.session_state.pdf_completed)
        )
        fallback = '<span style="color:#888;">None</span>'
        st.markdown(f'<div class="byu-card">{done_html or fallback}</div>', unsafe_allow_html=True)
        st.markdown('<p class="byu-progress-title">Remaining</p>', unsafe_allow_html=True)
        rem = st.session_state.pdf_remaining or set()
        rem_html = "".join(
            f'<span class="byu-pill byu-pill-remaining">{cat}</span>'
            for cat in sorted(rem)
        )
        st.markdown(f'<div class="byu-card">{rem_html or fallback}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with input_tab2:
    with st.container():
        st.markdown("### Manually select completed GE categories")
        st.caption("Check every requirement you've already completed.")
        all_cats = sorted(GE_CATEGORIES.keys())
        default_checked = sorted(st.session_state.pdf_completed or st.session_state.manual_completed)
        manual_cols = st.columns(2)
        manual_selected = set()
        for i, cat in enumerate(all_cats):
            col = manual_cols[i % 2]
            if col.checkbox(cat, value=(cat in default_checked), key=f"manual_{cat}"):
                manual_selected.add(cat)
        if st.button("Apply Manual Selection"):
            st.session_state.manual_completed = manual_selected
            st.session_state.pdf_completed = manual_selected
            st.session_state.pdf_remaining = set(GE_CATEGORIES.keys()) - manual_selected
            st.session_state.data_source = "manual"
            st.session_state.manual_override = False
            st.success(f"**{len(manual_selected)}** complete → **{len(st.session_state.pdf_remaining)}** remaining.")

if st.session_state.manual_override:
    st.warning("Could not fully parse your PDF. Use the **Manual Entry** tab, then run the optimizer.")

st.divider()


# ════════════════════════════════════════════════════════════════
# STEP 2 — Run Optimizer
# ════════════════════════════════════════════════════════════════
st.markdown("## Step 2 — Run the Optimizer")

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
    )
    st.divider()
    st.caption("BYU Catalog · RateMyProfessors")

with st.expander("🔍 Debug: What the optimizer will see", expanded=False):
    _completed = st.session_state.pdf_completed or set()
    _remaining = st.session_state.pdf_remaining or set(GE_CATEGORIES.keys())
    _taken = st.session_state.courses_taken or set()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption("**Completed:** " + (", ".join(sorted(_completed)) if _completed else "None"))
    with c2:
        st.caption("**Remaining:** " + ", ".join(sorted(_remaining)))
    with c3:
        st.caption("**Courses taken:** " + (", ".join(sorted(_taken)) if _taken else "None"))
    st.caption(f"Source: {st.session_state.data_source or 'none'} · {len(_completed)} done · {len(_remaining)} remaining")
    if st.session_state.data_source is None:
        st.warning("No data yet — upload a PDF or use Manual Entry.")

run_btn = st.button("Run Optimizer", type="primary")


def run_optimizer(use_ilp, skip_rmp, refresh, remaining_requirements, courses_taken):
    init_db()
    with st.status("Running optimizer...", expanded=True) as status:
        st.write("Loading BYU GE course data...")
        courses = scrape_catalog_for_ge(refresh=refresh)
        st.write(f"Loaded {len(courses)} GE courses")
        target_count = len(remaining_requirements) if remaining_requirements else len(GE_CATEGORIES)
        st.write(f"Optimizing for {target_count} remaining categories...")
        selected, uncovered = optimize(
            courses,
            use_ilp=use_ilp,
            remaining_requirements=remaining_requirements,
            courses_taken=courses_taken or None,
        )
        st.write(f"Selected {len(selected)} courses")
        if not skip_rmp:
            st.write("Fetching RateMyProfessors ratings...")
            selected = enrich_with_rmp(selected, refresh=refresh)
            st.write("Ratings loaded")
        status.update(label="Optimization complete", state="complete")
    return selected, uncovered


if run_btn:
    remaining = st.session_state.pdf_remaining
    courses_taken = st.session_state.courses_taken
    selected, uncovered = run_optimizer(use_ilp, skip_rmp, refresh, remaining, courses_taken)
    st.session_state.results = selected
    st.session_state.uncovered = uncovered


# ════════════════════════════════════════════════════════════════
# STEP 3 — Results (cards, progress tracker, no raw dataframe)
# Sort runs on session_state.results (already enriched by run_optimizer when
# RMP not skipped). Use -1 for missing rating and 99 for missing difficulty
# so courses without RMP data fall to the bottom.
# ════════════════════════════════════════════════════════════════
def _rating_for_sort(c):
    v = c.get("rmp_rating")
    return v if v is not None else -1

def _difficulty_for_sort(c):
    v = c.get("rmp_difficulty")
    return v if v is not None else 99

if st.session_state.results is not None:
    selected = list(st.session_state.results)
    uncovered = st.session_state.uncovered
    already_done = st.session_state.pdf_completed or set()

    num_cats = lambda c: len(c.get("ge_categories", []))
    # Canonical order: GE categories desc, then RMP rating desc, then difficulty asc.
    if sort_priority == "Best Professor":
        selected.sort(key=lambda c: (-_rating_for_sort(c), -num_cats(c), _difficulty_for_sort(c)))
    elif sort_priority == "Easiest Classes":
        selected.sort(key=lambda c: (_difficulty_for_sort(c), -_rating_for_sort(c), -num_cats(c)))
    elif sort_priority == "Fewest Classes":
        selected.sort(key=lambda c: (-num_cats(c), -_rating_for_sort(c), _difficulty_for_sort(c)))
    else:
        # Balanced (default): double-dippers first, then best rating, then easiest.
        selected.sort(key=lambda c: (-num_cats(c), -_rating_for_sort(c), _difficulty_for_sort(c)))

    all_cats = set(GE_CATEGORIES.keys())
    covered_by_optimizer = all_cats - uncovered - already_done
    total_credits = sum(c.get("credit_hours", 3) for c in selected)
    double_dippers = [c for c in selected if len(c.get("ge_categories_all", c.get("ge_categories", []))) > 1]

    st.divider()
    st.markdown("## Results")

    # Progress tracker: completed | covered by optimizer | still uncovered
    st.markdown("### GE progress")
    prog_col1, prog_col2, prog_col3 = st.columns(3)
    with prog_col1:
        st.markdown("**Completed**")
        done_pills = "".join(
            f'<span class="byu-pill byu-pill-done">✓ {cat}</span>'
            for cat in sorted(already_done)
        )
        st.markdown(f'<div class="ge-pills">{done_pills or "—"}</div>', unsafe_allow_html=True)
    with prog_col2:
        st.markdown("**Covered by recommendations**")
        cov_pills = "".join(
            f'<span class="byu-pill byu-pill-remaining">{cat}</span>'
            for cat in sorted(covered_by_optimizer)
        )
        st.markdown(f'<div class="ge-pills">{cov_pills or "—"}</div>', unsafe_allow_html=True)
    with prog_col3:
        st.markdown("**Still uncovered**")
        unc_pills = "".join(
            f'<span class="byu-pill byu-pill-uncovered">{cat}</span>'
            for cat in sorted(uncovered)
        )
        st.markdown(f'<div class="ge-pills">{unc_pills or "None"}</div>', unsafe_allow_html=True)

    total_done = len(already_done) + len(covered_by_optimizer)
    st.progress(total_done / len(all_cats))
    st.caption(f"Overall: {total_done}/{len(all_cats)} categories")

    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Courses to take", len(selected))
    m2.metric("Est. credits", f"~{total_credits}")
    m3.metric("Already done", len(already_done))
    m4.metric("Covered", len(covered_by_optimizer))
    m5.metric("Double-dippers", len(double_dippers))

    st.divider()

    tab1, tab2, tab3 = st.tabs(["Recommended courses", "Full GE map", "Double-dippers"])

    # Tab 1: Course cards (no dataframe)
    with tab1:
        st.caption(f"Sorted by: **{sort_priority}**")
        for c in selected:
            cats = c.get("ge_categories", [])
            cats_display = ", ".join(cats)
            profs = c.get("professors", [])
            ge_pills_html = "".join(
                f'<span class="byu-pill byu-pill-remaining">{cat}</span>'
                for cat in cats
            )
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
                    prof_rows.append('<div class="prof-row">' + " · ".join(p for p in parts if p) + "</div>")
            else:
                prof_rows.append('<div class="prof-row">No professor ratings yet</div>')
            card_html = f"""
            <div class="byu-course-card">
                <div class="course-title"><span class="course-code">{c['course_code']}</span> — {c['course_name']}</div>
                <div class="ge-pills">{ge_pills_html}</div>
                {"".join(prof_rows)}
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

        with st.expander("Column guide", expanded=False):
            st.markdown("| Column | Meaning |\n|--------|--------|\n| Professor | Current instructors; RMP rating, difficulty, would-take-again %. |\n| GE categories | Remaining requirements this course fulfills. |")

        # CSV export
        rows = []
        for c in selected:
            profs = c.get("professors", [])
            cats = c.get("ge_categories", [])
            if profs:
                for p in profs:
                    rows.append({
                        "Course": c["course_code"],
                        "Name": c["course_name"],
                        "GE Categories": ", ".join(cats),
                        "Professor": p.get("name", ""),
                        "Rating": round(p["rating"], 1) if p.get("rating") else None,
                        "Difficulty": round(p["difficulty"], 1) if p.get("difficulty") else None,
                        "Would Take Again": f"{p['would_take_again']:.0f}%" if p.get("would_take_again") is not None and p["would_take_again"] >= 0 else "—",
                    })
            else:
                rows.append({
                    "Course": c["course_code"],
                    "Name": c["course_name"],
                    "GE Categories": ", ".join(cats),
                    "Professor": "—",
                    "Rating": None,
                    "Difficulty": None,
                    "Would Take Again": "—",
                })
        df_export = pd.DataFrame(rows)
        st.download_button("Download CSV", data=df_export.to_csv(index=False), file_name="byu_ge_optimizer_results.csv", mime="text/csv")

    # Tab 2: Full GE map
    with tab2:
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("**Completed**")
            for cat in sorted(already_done):
                st.markdown(f'<span class="byu-pill byu-pill-done">✓ {cat}</span>', unsafe_allow_html=True)
        with col_b:
            st.markdown("**Covered by optimizer**")
            for cat in sorted(covered_by_optimizer):
                courses_for = [c for c in selected if cat in c.get("ge_categories", [])]
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

    # Tab 3: Double-dippers
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

    # Debug expander (collapsed)
    with st.expander("🔍 Debug: What triggered each GE completion", expanded=False):
        taken = st.session_state.courses_taken or set()
        st.caption("Completions use course code cross-reference only.")
        for cat in sorted(already_done):
            triggering = sorted(c for c in taken if c in GE_REQUIREMENTS.get(cat, []))
            if triggering:
                st.success(f"**{cat}** — {', '.join(triggering)}")
            else:
                st.warning(f"**{cat}** — no matching course in GE list")
        unmatched = sorted(c for c in taken if not any(c in codes for codes in GE_REQUIREMENTS.values()))
        if unmatched:
            st.caption("Courses not in any GE category: " + ", ".join(unmatched))

    pathway_state = st.session_state.get("pathway_state")
    if pathway_state and pathway_state.get("partial"):
        with st.expander("Partial requirements — pathway shortcuts applied", expanded=False):
            for cat, state in pathway_state["partial"].items():
                taken_str = ", ".join(state.already_taken) or "none"
                st.markdown(f"**{cat}** — Taken: `{taken_str}`. **{state.courses_remaining}** more needed.")

else:
    st.markdown("""
    <div style="text-align:center; padding: 2.5rem; color: #666; font-family: 'IBM Plex Sans', sans-serif;">
        <p><strong>Upload your degree audit PDF</strong> (or use Manual Entry), then click <strong>Run Optimizer</strong>.</p>
        <p>The optimizer finds the fewest BYU courses to complete your remaining GE requirements, with RateMyProfessors ratings.</p>
    </div>
    """, unsafe_allow_html=True)
