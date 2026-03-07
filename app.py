"""
BYU GE Optimizer — Streamlit Web App
"""

import streamlit as st
import pandas as pd
from scraper import scrape_catalog_for_ge, GE_CATEGORIES, init_db
from optimizer import optimize
from rmp import enrich_with_rmp

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="BYU GE Optimizer",
    page_icon="🎓",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .metric-card {
        background: #f0f4ff;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .double-dip-badge {
        background: #ffd700;
        color: #333;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .covered-pill {
        background: #d4edda;
        color: #155724;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.8rem;
        margin: 2px;
        display: inline-block;
    }
    .uncovered-pill {
        background: #f8d7da;
        color: #721c24;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.8rem;
        margin: 2px;
        display: inline-block;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎓 BYU GE Optimizer</h1>
    <p style="color: #666; font-size: 1.1rem;">
        Find the <strong>fewest courses</strong> that fulfill all your GE requirements —
        sorted by RateMyProfessors ratings.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Sidebar controls ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://www.byu.edu/static/images/BYU_monogram.svg", width=80)
    st.title("⚙️ Options")

    use_ilp = st.toggle("Use ILP Optimization", value=True,
                        help="Integer Linear Programming finds the true minimum. Greedy is faster but may not be optimal.")
    skip_rmp = st.toggle("Skip RMP Ratings", value=False,
                         help="Skip RateMyProfessors lookup (faster, but no professor ratings)")
    refresh = st.toggle("Refresh Data", value=False,
                        help="Re-scrape BYU catalog and RMP. Slow — only use if data seems outdated.")

    st.divider()
    run_btn = st.button("🚀 Run Optimizer", type="primary", use_container_width=True)

    st.divider()
    st.caption("Built with Python · PuLP · Streamlit")
    st.caption("Data: BYU Catalog · RateMyProfessors")


# ── Session state ─────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "uncovered" not in st.session_state:
    st.session_state.uncovered = set()


# ── Run optimizer ────────────────────────────────────────────────
def run_optimizer(use_ilp, skip_rmp, refresh):
    init_db()

    with st.status("⚙️ Running optimizer...", expanded=True) as status:
        st.write("📚 Loading BYU GE course data...")
        courses = scrape_catalog_for_ge(refresh=refresh)
        st.write(f"✅ Loaded {len(courses)} GE courses")

        st.write("🧮 Optimizing course selection...")
        selected, uncovered = optimize(courses, use_ilp=use_ilp)
        st.write(f"✅ Selected {len(selected)} courses covering {len(GE_CATEGORIES) - len(uncovered)}/{len(GE_CATEGORIES)} GE categories")

        if not skip_rmp:
            st.write("⭐ Fetching RateMyProfessors ratings...")
            selected = enrich_with_rmp(selected, refresh=refresh)
            st.write("✅ Professor ratings loaded")

        status.update(label="✅ Optimization complete!", state="complete")

    return selected, uncovered


if run_btn:
    selected, uncovered = run_optimizer(use_ilp, skip_rmp, refresh)
    st.session_state.results = selected
    st.session_state.uncovered = uncovered


# ── Results ───────────────────────────────────────────────────────
if st.session_state.results:
    selected = st.session_state.results
    uncovered = st.session_state.uncovered
    covered = set(GE_CATEGORIES.keys()) - uncovered
    total_credits = sum(c.get("credit_hours", 3) for c in selected)
    double_dippers = [c for c in selected if len(c.get("ge_categories", [])) > 1]

    # ── Metrics row ──────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📚 Courses Needed", len(selected))
    col2.metric("🎯 Credits", f"~{total_credits}")
    col3.metric("✅ GE Categories", f"{len(covered)}/{len(GE_CATEGORIES)}")
    col4.metric("⚡ Double-Dippers", len(double_dippers))

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📋 Recommended Courses", "📊 GE Coverage", "⚡ Double-Dippers"])

    with tab1:
        st.subheader("Recommended Course List")
        st.caption("Sorted by: most GE categories fulfilled → highest professor rating")

        # Build DataFrame
        rows = []
        for c in selected:
            profs = c.get("professors", [])
            top = profs[0] if profs else None
            cats = c.get("ge_categories", [])

            rows.append({
                "Course": c["course_code"],
                "Name": c["course_name"],
                "Credits": c.get("credit_hours", 3),
                "GE Categories": ", ".join(cats),
                "# Categories": len(cats),
                "Top Professor": top["name"] if top else "N/A",
                "Rating": round(top["rating"], 1) if top and top.get("rating") else None,
                "Difficulty": round(top["difficulty"], 1) if top and top.get("difficulty") else None,
                "Would Take Again": f"{top['would_take_again']:.0f}%" if top and top.get("would_take_again", -1) >= 0 else "N/A",
            })

        df = pd.DataFrame(rows)

        # Color rating column
        def color_rating(val):
            if val is None:
                return "color: gray"
            if val >= 4.0:
                return "color: green; font-weight: bold"
            elif val >= 3.0:
                return "color: orange"
            return "color: red"

        def color_difficulty(val):
            if val is None:
                return "color: gray"
            if val <= 2.5:
                return "color: green"
            elif val <= 3.5:
                return "color: orange"
            return "color: red; font-weight: bold"

        styled = df.style.applymap(color_rating, subset=["Rating"]) \
                         .applymap(color_difficulty, subset=["Difficulty"]) \
                         .highlight_max(subset=["# Categories"], color="#fff3cd")

        st.dataframe(styled, use_container_width=True, hide_index=True)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download as CSV",
            data=csv,
            file_name="byu_ge_optimizer_results.csv",
            mime="text/csv",
        )

    with tab2:
        st.subheader("GE Requirement Coverage")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### ✅ Covered")
            for cat in sorted(covered):
                courses_for_cat = [c for c in selected if cat in c.get("ge_categories", [])]
                course_codes = ", ".join(c["course_code"] for c in courses_for_cat)
                st.markdown(
                    f'<span class="covered-pill">✓ {cat}</span> '
                    f'<span style="color:#666; font-size:0.8rem;">→ {course_codes}</span>',
                    unsafe_allow_html=True
                )

        with col_b:
            if uncovered:
                st.markdown("### ❌ Not Covered")
                for cat in sorted(uncovered):
                    st.markdown(
                        f'<span class="uncovered-pill">✗ {cat}</span>',
                        unsafe_allow_html=True
                    )
                st.warning("These categories have no matching courses in the database. You may need to fill them manually.")
            else:
                st.success("🎉 All GE categories are covered!")

        # Progress bar
        st.divider()
        progress = len(covered) / len(GE_CATEGORIES)
        st.markdown(f"**Overall GE Completion: {len(covered)}/{len(GE_CATEGORIES)} categories**")
        st.progress(progress)

    with tab3:
        st.subheader("⚡ Double-Dipping Courses")
        st.caption("These courses satisfy multiple GE requirements — take these first!")

        if double_dippers:
            for c in sorted(double_dippers, key=lambda x: -len(x.get("ge_categories", []))):
                cats = c.get("ge_categories", [])
                profs = c.get("professors", [])
                top = profs[0] if profs else None

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### `{c['course_code']}` — {c['course_name']}")
                        st.markdown(" · ".join(
                            f'<span class="covered-pill">{cat}</span>' for cat in cats
                        ), unsafe_allow_html=True)
                    with col2:
                        st.metric("GE Categories", len(cats))
                        if top and top.get("rating"):
                            st.metric("RMP Rating", f"{top['rating']:.1f} / 5")
        else:
            st.info("No double-dipping courses found in the current selection.")

else:
    # Landing state
    st.markdown("""
    <div style="text-align:center; padding: 3rem; color: #888;">
        <h3>👈 Press <strong>Run Optimizer</strong> in the sidebar to get started</h3>
        <p>The optimizer will find the fewest BYU courses needed to fulfill all your GE requirements,<br>
        ranked by RateMyProfessors ratings so you get the best professors too.</p>
    </div>
    """, unsafe_allow_html=True)
