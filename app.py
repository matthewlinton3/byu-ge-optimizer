"""
BYU GE Optimizer — Streamlit Web App
"""

import streamlit as st
import pandas as pd
from scraper import scrape_catalog_for_ge, GE_CATEGORIES, init_db
from optimizer import optimize
from rmp import enrich_with_rmp
from pdf_parser import parse_degree_audit, HAS_PDFPLUMBER
from pathways import get_remaining_requirements, PATHWAYS

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="BYU GE Optimizer",
    page_icon="🎓",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header { text-align: center; padding: 1rem 0 0.5rem 0; }
    .covered-pill {
        background: #d4edda; color: #155724;
        border-radius: 12px; padding: 2px 10px;
        font-size: 0.82rem; margin: 2px; display: inline-block;
    }
    .uncovered-pill {
        background: #f8d7da; color: #721c24;
        border-radius: 12px; padding: 2px 10px;
        font-size: 0.82rem; margin: 2px; display: inline-block;
    }
    .already-done-pill {
        background: #cce5ff; color: #004085;
        border-radius: 12px; padding: 2px 10px;
        font-size: 0.82rem; margin: 2px; display: inline-block;
    }
    div[data-testid="stMetricValue"] { font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎓 BYU GE Optimizer</h1>
    <p style="color: #666; font-size: 1.1rem;">
        Upload your MyMap degree audit to skip completed GEs —
        then find the <strong>fewest remaining courses</strong> sorted by RMP ratings.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

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
    ("courses_taken", set()),       # individual course codes parsed from PDF
    ("pathway_state", None),        # output of get_remaining_requirements()
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════════
# STEP 1 — Degree Audit Upload
# ════════════════════════════════════════════════════════════════
st.markdown("## Step 1 — Upload Your Degree Audit (Optional)")
st.caption("Upload your BYU MyMap PDF to automatically skip GE requirements you've already completed.")

upload_col, info_col = st.columns([2, 1])

with upload_col:
    uploaded_pdf = st.file_uploader(
        "Upload BYU MyMap Degree Audit PDF",
        type=["pdf"],
        help="Download from MyMap → Degree Audit → Save as PDF"
    )
    with st.expander("❓ How do I get this PDF?"):
        st.markdown("""
**Step 1** — Go to [mymap.byu.edu](https://mymap.byu.edu) and log in with your **NetID**.

**Step 2** — Click on your **Degree Audit** or **Academic Plan** from the dashboard.

**Step 3** — Look for a **Print** or **Export** button in the top-right corner of the audit page.

**Step 4** — When the print dialog opens, change the destination to **"Save as PDF"** and click Save.

**Step 5** — Upload that PDF file using the button above.

---
🔒 **Your privacy is protected.** Your PDF is processed locally and is never stored, uploaded to a server, or shared with anyone.
        """)

with info_col:
    st.info(
        "**Tip:** The degree audit shows which GE requirements you've already "
        "satisfied so the optimizer only recommends courses you actually still need."
    )

# ── Parse uploaded PDF ───────────────────────────────────────────
if uploaded_pdf is not None:
    if not HAS_PDFPLUMBER:
        st.error("⚠️ pdfplumber is not installed on this server. Please use manual selection below.")
        st.session_state.manual_override = True
    else:
        with st.spinner("📄 Parsing your degree audit PDF..."):
            parse_result = parse_degree_audit(uploaded_pdf)

        if parse_result["error"]:
            st.warning(f"⚠️ Could not fully parse PDF: {parse_result['error']}")
            st.session_state.pdf_parse_error = parse_result["error"]
            st.session_state.manual_override = True

        elif parse_result["parse_confidence"] == "low":
            st.warning(
                "⚠️ Your PDF was read but doesn't look like a standard BYU MyMap degree audit "
                "(low confidence). Please verify the results below or use manual selection."
            )
            st.session_state.pdf_completed   = parse_result["completed"]
            st.session_state.pdf_remaining   = parse_result["remaining"]
            st.session_state.pdf_confidence  = parse_result["parse_confidence"]
            st.session_state.manual_override = True

        else:
            st.session_state.pdf_completed   = parse_result["completed"]
            st.session_state.pdf_remaining   = parse_result["remaining"]
            st.session_state.pdf_confidence  = parse_result["parse_confidence"]
            st.session_state.manual_override = False

            # Store individual courses taken for pathway-aware optimization
            courses_taken = parse_result.get("courses_taken", set())
            st.session_state.courses_taken = courses_taken

            # Run pathway analysis to detect partial completions
            if courses_taken:
                pathway_state = get_remaining_requirements(
                    courses_taken, parse_result["completed"]
                )
                st.session_state.pathway_state = pathway_state

            st.success(
                f"✅ PDF parsed successfully "
                f"({'high' if parse_result['parse_confidence'] == 'high' else 'medium'} confidence). "
                f"Found **{len(parse_result['completed'])}** completed GE categories"
                + (f" and **{len(courses_taken)}** individual courses." if courses_taken else ".")
            )

# ── PDF results summary ──────────────────────────────────────────
if st.session_state.pdf_completed is not None and not st.session_state.manual_override:
    completed_from_pdf = st.session_state.pdf_completed
    remaining_from_pdf = st.session_state.pdf_remaining

    st.markdown("### 📋 Degree Audit Summary")
    sum_col1, sum_col2 = st.columns(2)

    with sum_col1:
        st.markdown("**✅ Already Completed:**")
        if completed_from_pdf:
            for cat in sorted(completed_from_pdf):
                st.markdown(f'<span class="already-done-pill">✓ {cat}</span>', unsafe_allow_html=True)
        else:
            st.caption("None detected as complete")

    with sum_col2:
        st.markdown("**📌 Still Needed:**")
        if remaining_from_pdf:
            for cat in sorted(remaining_from_pdf):
                st.markdown(f'<span class="uncovered-pill">→ {cat}</span>', unsafe_allow_html=True)
        else:
            st.success("🎉 All GE requirements appear to be complete!")

    st.divider()

# ── Manual fallback / override ────────────────────────────────────
show_manual = (
    st.session_state.manual_override or
    uploaded_pdf is None or
    st.checkbox("✏️ Manually adjust detected completions", value=False)
)

if show_manual:
    if st.session_state.manual_override and uploaded_pdf is not None:
        st.markdown("### ✏️ Manual GE Selection (fallback)")
        st.caption("The PDF could not be reliably parsed. Please check off the GE categories you've already completed:")
    else:
        st.markdown("### ✏️ Manually Select Completed GEs")
        st.caption("Check any GE requirements you've already completed:")

    all_cats       = sorted(GE_CATEGORIES.keys())
    default_checked = sorted(st.session_state.pdf_completed or st.session_state.manual_completed)

    manual_cols    = st.columns(2)
    manual_selected = set()
    for i, cat in enumerate(all_cats):
        col     = manual_cols[i % 2]
        already = cat in default_checked
        checked = col.checkbox(cat, value=already, key=f"manual_{cat}")
        if checked:
            manual_selected.add(cat)

    st.session_state.manual_completed = manual_selected
    st.session_state.pdf_completed    = manual_selected
    st.session_state.pdf_remaining    = set(GE_CATEGORIES.keys()) - manual_selected

    remaining_count = len(st.session_state.pdf_remaining)
    st.info(f"**{len(manual_selected)}** categories marked complete → optimizing for **{remaining_count}** remaining.")

st.divider()


# ════════════════════════════════════════════════════════════════
# STEP 2 — Optimizer Options + Run
# ════════════════════════════════════════════════════════════════
st.markdown("## Step 2 — Run the Optimizer")

with st.sidebar:
    st.title("⚙️ Options")
    use_ilp  = st.toggle("Use ILP Optimization", value=True,
                         help="Finds the true minimum number of courses. Greedy is faster but not always optimal.")
    skip_rmp = st.toggle("Skip RMP Ratings", value=False,
                         help="Skip RateMyProfessors lookup (faster, but no professor data)")
    refresh  = st.toggle("Refresh Data", value=False,
                         help="Re-scrape BYU catalog. Slow — only use if data seems outdated.")
    st.divider()
    st.caption("Built with Python · PuLP · Streamlit")
    st.caption("Data: BYU Catalog · RateMyProfessors")

run_btn = st.button("🚀 Run Optimizer", type="primary")


# ── Run optimizer ─────────────────────────────────────────────────
def run_optimizer(use_ilp, skip_rmp, refresh, remaining_requirements, courses_taken):
    init_db()
    with st.status("⚙️ Running optimizer...", expanded=True) as status:
        st.write("📚 Loading BYU GE course data...")
        courses = scrape_catalog_for_ge(refresh=refresh)
        st.write(f"✅ Loaded {len(courses)} GE courses")

        if courses_taken:
            st.write(f"🔍 Using pathway-aware optimization ({len(courses_taken)} courses already taken detected)...")
        target_count = len(remaining_requirements) if remaining_requirements else len(GE_CATEGORIES)
        st.write(f"🧮 Optimizing for {target_count} remaining GE categories...")
        selected, uncovered = optimize(
            courses,
            use_ilp=use_ilp,
            remaining_requirements=remaining_requirements,
            courses_taken=courses_taken or None,
        )
        st.write(f"✅ Selected {len(selected)} courses")

        if not skip_rmp:
            st.write("⭐ Fetching RateMyProfessors ratings...")
            selected = enrich_with_rmp(selected, refresh=refresh)
            st.write("✅ Professor ratings loaded")

        status.update(label="✅ Optimization complete!", state="complete")

    return selected, uncovered


if run_btn:
    remaining     = st.session_state.pdf_remaining
    courses_taken = st.session_state.courses_taken
    selected, uncovered = run_optimizer(use_ilp, skip_rmp, refresh, remaining, courses_taken)
    st.session_state.results   = selected
    st.session_state.uncovered = uncovered


# ════════════════════════════════════════════════════════════════
# STEP 3 — Results
# ════════════════════════════════════════════════════════════════
if st.session_state.results is not None:
    selected     = st.session_state.results
    uncovered    = st.session_state.uncovered
    already_done = st.session_state.pdf_completed or set()

    all_cats             = set(GE_CATEGORIES.keys())
    covered_by_optimizer = all_cats - uncovered - already_done
    total_credits        = sum(c.get("credit_hours", 3) for c in selected)
    double_dippers       = [c for c in selected if len(c.get("ge_categories", [])) > 1]

    st.divider()
    st.markdown("## Results")

    # ── Pathway partial-completion notice ────────────────────────
    pathway_state = st.session_state.get("pathway_state")
    if pathway_state and pathway_state.get("partial"):
        with st.expander("⚡ Partial Requirements Detected — Pathway Shortcuts Applied", expanded=True):
            st.caption(
                "The optimizer found courses you've already started and chose the "
                "cheapest pathway to complete each one."
            )
            for cat, state in pathway_state["partial"].items():
                taken_str = ", ".join(state["already_taken"]) or "none"
                needed    = state["courses_remaining"]
                pathway   = state["pathway"]["description"]
                st.markdown(
                    f"**{cat}** — You've taken `{taken_str}`. "
                    f"Pathway: _{pathway}_. **{needed} more course(s) needed.**"
                )

    # ── Metrics ──────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("📚 Courses to Take",    len(selected))
    m2.metric("🎯 Estimated Credits",  f"~{total_credits}")
    m3.metric("✅ Already Done",        len(already_done))
    m4.metric("📌 Categories Covered", len(covered_by_optimizer))
    m5.metric("⚡ Double-Dippers",     len(double_dippers))

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📋 Recommended Courses", "📊 Full GE Map", "⚡ Double-Dippers"])

    # ── Tab 1: Course Table ───────────────────────────────────────
    with tab1:
        st.subheader("Recommended Courses")
        if already_done:
            st.caption(
                f"Showing only courses for your **{len(st.session_state.pdf_remaining or all_cats)}** "
                f"remaining GE categories — {len(already_done)} already-completed categories excluded."
            )

        rows = []
        for c in selected:
            profs = c.get("professors", [])
            top   = profs[0] if profs else None
            cats  = c.get("ge_categories", [])
            rows.append({
                "Course":           c["course_code"],
                "Name":             c["course_name"],
                "Credits":          c.get("credit_hours", 3),
                "GE Categories":    ", ".join(cats),
                "# Categories":     len(cats),
                "Top Professor":    top["name"] if top else "N/A",
                "Rating":           round(top["rating"], 1)          if top and top.get("rating")                  else None,
                "Difficulty":       round(top["difficulty"], 1)      if top and top.get("difficulty")              else None,
                "Would Take Again": f"{top['would_take_again']:.0f}%" if top and top.get("would_take_again",-1)>=0 else "N/A",
            })

        df = pd.DataFrame(rows)

        def color_rating(val):
            if val is None: return "color: gray"
            if val >= 4.0:  return "color: green; font-weight: bold"
            if val >= 3.0:  return "color: orange"
            return "color: red"

        def color_difficulty(val):
            if val is None: return "color: gray"
            if val <= 2.5:  return "color: green"
            if val <= 3.5:  return "color: orange"
            return "color: red; font-weight: bold"

        styled = (df.style
                    .applymap(color_rating,     subset=["Rating"])
                    .applymap(color_difficulty, subset=["Difficulty"])
                    .highlight_max(subset=["# Categories"], color="#fff3cd"))

        st.dataframe(styled, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download as CSV", data=df.to_csv(index=False),
            file_name="byu_ge_optimizer_results.csv", mime="text/csv"
        )

    # ── Tab 2: Full GE Map ────────────────────────────────────────
    with tab2:
        st.subheader("Full GE Requirement Map")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("### ✅ Already Completed")
            if already_done:
                for cat in sorted(already_done):
                    st.markdown(f'<span class="already-done-pill">✓ {cat}</span>', unsafe_allow_html=True)
            else:
                st.caption("None (no PDF uploaded or no completions detected)")

        with col_b:
            st.markdown("### 📋 Covered by Optimizer")
            for cat in sorted(covered_by_optimizer):
                courses_for = [c for c in selected if cat in c.get("ge_categories", [])]
                codes = ", ".join(c["course_code"] for c in courses_for)
                st.markdown(
                    f'<span class="covered-pill">✓ {cat}</span> '
                    f'<span style="color:#666;font-size:0.78rem;">→ {codes}</span>',
                    unsafe_allow_html=True
                )

        with col_c:
            st.markdown("### ❌ Still Uncovered")
            if uncovered:
                for cat in sorted(uncovered):
                    st.markdown(f'<span class="uncovered-pill">✗ {cat}</span>', unsafe_allow_html=True)
                st.warning("No courses found in the database for these categories.")
            else:
                st.success("🎉 All remaining requirements are covered!")

        st.divider()
        total_done = len(already_done) + len(covered_by_optimizer)
        st.markdown(f"**Overall GE Progress: {total_done}/{len(all_cats)} categories**")
        st.progress(total_done / len(all_cats))

    # ── Tab 3: Double-Dippers ─────────────────────────────────────
    with tab3:
        st.subheader("⚡ Double-Dipping Courses")
        st.caption("These courses satisfy multiple GE requirements simultaneously — prioritize these!")

        if double_dippers:
            for c in sorted(double_dippers, key=lambda x: -len(x.get("ge_categories", []))):
                cats  = c.get("ge_categories", [])
                profs = c.get("professors", [])
                top   = profs[0] if profs else None
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### `{c['course_code']}` — {c['course_name']}")
                        st.markdown(
                            " · ".join(f'<span class="covered-pill">{cat}</span>' for cat in cats),
                            unsafe_allow_html=True
                        )
                    with col2:
                        st.metric("GE Categories", len(cats))
                        if top and top.get("rating"):
                            st.metric("RMP Rating", f"{top['rating']:.1f} / 5")
        else:
            st.info("No double-dipping courses in the current selection.")

else:
    st.markdown("""
    <div style="text-align:center; padding: 2rem; color: #888;">
        <h3>👆 Upload your degree audit (optional) then press <strong>Run Optimizer</strong></h3>
        <p>The optimizer finds the fewest BYU courses to complete your remaining GE requirements,<br>
        ranked by RateMyProfessors so you get the best professors.</p>
    </div>
    """, unsafe_allow_html=True)
