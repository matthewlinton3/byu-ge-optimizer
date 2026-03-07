"""
BYU GE Optimizer — Streamlit Web App
"""

import base64
import time

import streamlit as st
import pandas as pd
from scraper import scrape_catalog_for_ge, GE_CATEGORIES, init_db
from optimizer import optimize
from rmp import enrich_with_rmp
from pdf_parser import parse_degree_audit, HAS_PDFPLUMBER
from pathways import get_remaining_requirements, PATHWAYS
from mymap_scraper import login_and_scrape, format_debug_report
try:
    from mymap_browser_login import (
        browser_login_and_scrape,
        HAS_SELENIUM,
        IS_RAILWAY,
        create_driver,
        navigate_to_login,
        fill_cas_credentials,
        detect_login_state,
        take_screenshot_base64,
        scrape_from_driver,
    )
except Exception:
    import os as _os
    HAS_SELENIUM = False
    IS_RAILWAY   = bool(_os.environ.get("RAILWAY_ENVIRONMENT"))
    def browser_login_and_scrape(**_):
        return {"success": False, "error": "Browser login unavailable", "debug": {}}

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="BYU GE Optimizer",
    page_icon="🎓",
    layout="wide",
)

# ── Design System ────────────────────────────────────────────────
# Palette: Cream #FAFAF8 | Charcoal #1A1A1A | Coral #E8673A
# Type:    Georgia (headings) + system-ui (body)
st.markdown("""
<style>
/* ════════════════════════════════════════════════════════════════
   Base & Background
   ════════════════════════════════════════════════════════════════ */
html, body, .stApp { background-color: #FAFAF8 !important; }
.main .block-container {
    background-color: #FAFAF8;
    padding-top: 1rem;
    padding-bottom: 4rem;
    max-width: 1200px;
}

/* ════════════════════════════════════════════════════════════════
   Typography
   ════════════════════════════════════════════════════════════════ */
h1, h2, h3, h4,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
    font-family: Georgia, 'Times New Roman', 'Book Antiqua', serif !important;
    color: #1A1A1A !important;
    font-weight: normal !important;
    letter-spacing: -0.015em;
}
p, li, span, label, .stCaption, [data-testid="stCaptionContainer"] {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ════════════════════════════════════════════════════════════════
   Custom Header
   ════════════════════════════════════════════════════════════════ */
.ge-header { text-align: center; padding: 1.75rem 0 1.25rem 0; }
.ge-logo   { margin-bottom: 0.9rem; line-height: 0; }
.ge-title  {
    font-family: Georgia, serif !important;
    font-size: 2.3rem !important;
    font-weight: normal !important;
    color: #1A1A1A !important;
    letter-spacing: -0.03em;
    margin: 0 0 0.45rem 0 !important;
    line-height: 1.1 !important;
}
.ge-subtitle {
    font-size: 1rem;
    color: #6A6A62;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.65;
    font-family: system-ui, sans-serif;
    font-weight: 400;
}

/* ════════════════════════════════════════════════════════════════
   Sidebar — dark charcoal
   ════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
    background-color: #1A1A1A !important;
}
/* All text inside sidebar inherits light color */
section[data-testid="stSidebar"] * { color: #C0BFB6 !important; }

/* Headings in sidebar: label-style */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: system-ui, sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #666660 !important;
    margin-bottom: 0.75rem;
}
section[data-testid="stSidebar"] hr { border-color: #2C2C2C !important; }
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #505048 !important;
}
/* Sidebar toggle: coral when on */
section[data-testid="stSidebar"] [data-testid="stToggle"] [aria-checked="true"],
section[data-testid="stSidebar"] [role="switch"][aria-checked="true"] {
    background-color: #E8673A !important;
}
/* Sidebar radio active label */
section[data-testid="stSidebar"] [data-testid="stRadio"] [data-checked="true"] span,
section[data-testid="stSidebar"] .stRadio label[data-active="true"] {
    color: #E8673A !important;
}

/* ════════════════════════════════════════════════════════════════
   Buttons
   ════════════════════════════════════════════════════════════════ */
/* Primary — coral fill */
button[data-testid="baseButton-primary"],
.stFormSubmitButton button {
    background-color: #E8673A !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: system-ui, sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
    box-shadow: 0 1px 4px rgba(232,103,58,0.28) !important;
    transition: background-color 0.15s ease, box-shadow 0.15s ease !important;
}
button[data-testid="baseButton-primary"]:hover,
.stFormSubmitButton button:hover {
    background-color: #D45A2F !important;
    box-shadow: 0 3px 8px rgba(232,103,58,0.36) !important;
}
/* Secondary — charcoal outline */
button[data-testid="baseButton-secondary"],
.stButton > button,
.stDownloadButton button {
    background-color: transparent !important;
    color: #1A1A1A !important;
    border: 1.5px solid #D4D3CB !important;
    border-radius: 8px !important;
    font-family: system-ui, sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
button[data-testid="baseButton-secondary"]:hover,
.stButton > button:hover,
.stDownloadButton button:hover {
    background-color: #1A1A1A !important;
    color: #FAFAF8 !important;
    border-color: #1A1A1A !important;
}

/* ════════════════════════════════════════════════════════════════
   Tabs
   ════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid #E0DFD8 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #8A8A80 !important;
    border-bottom: 2px solid transparent !important;
    font-family: system-ui, sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.1rem !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #1A1A1A !important; }
.stTabs [aria-selected="true"] {
    color: #1A1A1A !important;
    border-bottom: 2px solid #E8673A !important;
    background-color: transparent !important;
}
/* Kill default Streamlit tab highlight */
.stTabs [data-baseweb="tab-highlight"] { background-color: #E8673A !important; }

/* ════════════════════════════════════════════════════════════════
   Metrics
   ════════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E4E3DC;
    border-radius: 10px;
    padding: 1rem 1.25rem;
}
div[data-testid="stMetricValue"] {
    font-family: Georgia, serif !important;
    font-size: 1.9rem !important;
    color: #1A1A1A !important;
    font-weight: normal !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    color: #8A8A80 !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-family: system-ui, sans-serif !important;
}

/* ════════════════════════════════════════════════════════════════
   Form inputs
   ════════════════════════════════════════════════════════════════ */
.stTextInput input, .stTextArea textarea {
    background-color: white !important;
    border: 1px solid #E0DFD8 !important;
    border-radius: 8px !important;
    color: #1A1A1A !important;
    font-family: system-ui, sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #E8673A !important;
    box-shadow: 0 0 0 2px rgba(232,103,58,0.12) !important;
}

/* ════════════════════════════════════════════════════════════════
   Expanders
   ════════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    border: 1px solid #E4E3DC !important;
    border-radius: 10px !important;
    background-color: white !important;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    font-family: system-ui, sans-serif !important;
    font-weight: 500 !important;
    color: #1A1A1A !important;
    padding: 0.7rem 1rem !important;
}

/* ════════════════════════════════════════════════════════════════
   Cards (st.container with border=True)
   ════════════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #E4E3DC !important;
    border-left: 3px solid #E8673A !important;
    border-radius: 10px !important;
    background-color: white !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
}

/* ════════════════════════════════════════════════════════════════
   Alerts
   ════════════════════════════════════════════════════════════════ */
[data-testid="stInfo"] {
    background-color: #FEF6F2 !important;
    border: 1px solid #F5C9B5 !important;
    border-radius: 8px !important;
    color: #7A3520 !important;
}
[data-testid="stWarning"] {
    background-color: #FFFBF0 !important;
    border: 1px solid #EDD97B !important;
    border-radius: 8px !important;
}
[data-testid="stSuccess"] {
    background-color: #F0FAF4 !important;
    border: 1px solid #A8D5B5 !important;
    border-radius: 8px !important;
}
[data-testid="stError"] {
    background-color: #FFF5F5 !important;
    border: 1px solid #FFAAAA !important;
    border-radius: 8px !important;
}

/* ════════════════════════════════════════════════════════════════
   Progress bar
   ════════════════════════════════════════════════════════════════ */
[data-testid="stProgressBar"] > div {
    background-color: #E8E7E0 !important;
    border-radius: 4px !important;
}
[data-testid="stProgressBar"] > div > div {
    background-color: #E8673A !important;
    border-radius: 4px !important;
}

/* ════════════════════════════════════════════════════════════════
   File uploader
   ════════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] > div {
    border: 2px dashed #D0CFC8 !important;
    border-radius: 10px !important;
    background-color: white !important;
}
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"] {
    border-color: #E8673A !important;
    color: #E8673A !important;
}

/* ════════════════════════════════════════════════════════════════
   Dataframe & Status
   ════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #E4E3DC !important;
}
[data-testid="stStatusWidget"] {
    background-color: white !important;
    border: 1px solid #E4E3DC !important;
    border-radius: 10px !important;
}
[data-testid="stCode"] {
    border-radius: 8px !important;
    border: 1px solid #E4E3DC !important;
}

/* ════════════════════════════════════════════════════════════════
   Dividers & Scrollbar
   ════════════════════════════════════════════════════════════════ */
hr { border-color: #E4E3DC !important; margin: 1.5rem 0 !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #F0EFE9; }
::-webkit-scrollbar-thumb { background: #C8C7C0; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #E8673A; }

/* ════════════════════════════════════════════════════════════════
   Semantic Pills
   ════════════════════════════════════════════════════════════════ */
.covered-pill {
    background: #E8F5EE; color: #1B6B3A;
    border-radius: 6px; padding: 3px 10px;
    font-size: 0.8rem; font-weight: 500; margin: 2px;
    display: inline-block;
    font-family: system-ui, sans-serif;
}
.uncovered-pill {
    background: #FDE8E4; color: #B33000;
    border-radius: 6px; padding: 3px 10px;
    font-size: 0.8rem; font-weight: 500; margin: 2px;
    display: inline-block;
    font-family: system-ui, sans-serif;
}
.already-done-pill {
    background: #F0EFE9; color: #4A4A42;
    border-radius: 6px; padding: 3px 10px;
    font-size: 0.8rem; font-weight: 500; margin: 2px;
    display: inline-block;
    font-family: system-ui, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ── Header — geometric SVG logo + serif title ─────────────────────
st.markdown("""
<div class="ge-header">
    <div class="ge-logo">
        <svg width="60" height="42" viewBox="0 0 60 42" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="21" r="18" fill="#E8673A" opacity="0.93"/>
            <circle cx="40" cy="21" r="18" fill="#1A1A1A" opacity="0.88"/>
        </svg>
    </div>
    <div class="ge-title">BYU GE Optimizer</div>
    <p class="ge-subtitle">Find the minimum courses to finish your General Education requirements, ranked by professor quality.</p>
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
    ("courses_taken", set()),       # individual course codes parsed from PDF or MyMap
    ("pathway_state", None),        # output of get_remaining_requirements()
    ("mymap_scrape_result", None),  # raw result dict from mymap_scraper
    ("mymap_debug_report", None),   # formatted debug text
    ("mymap_login_error", None),
    ("data_source", None),          # "mymap" | "pdf" | "manual"
    # Railway headless login phases
    ("railway_login_phase", "idle"),   # "idle"|"login_form"|"duo"
    ("railway_screenshot", None),      # base64 PNG of current browser view
    # Note: railway_driver (WebDriver instance) is NOT pre-initialized here
    # because it cannot be default-constructed. Use st.session_state.get().
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════════
# STEP 1 — Import Degree Audit from MyMap
# ════════════════════════════════════════════════════════════════
st.markdown("## Step 1 — Import Your Degree Audit")

# ── Privacy notice (always visible) ──────────────────────────────
st.info(
    "🔒 **Privacy** — The recommended browser login opens mymap.byu.edu directly in Chrome: "
    "your credentials never pass through this app. "
    "The direct-login fallback sends credentials only to BYU's CAS server and discards them immediately. "
    "Nothing is stored, logged, or written to disk."
)

# ── Tabs: MyMap Login | PDF Upload | Manual ──────────────────────
input_tab1, input_tab2, input_tab3 = st.tabs(
    ["🔑 Log in to MyMap (Recommended)", "📄 Upload PDF", "✏️ Manual Entry"]
)

# ── Shared helper: clean up Railway headless driver ───────────────────────────
def _cleanup_railway_session():
    """Quit any open Railway headless driver and reset session state."""
    driver = st.session_state.pop("railway_driver", None)
    if driver is not None:
        try:
            driver.quit()
        except Exception:
            pass
    st.session_state.railway_login_phase = "idle"
    st.session_state.railway_screenshot  = None


# ── Shared helper: process a MyMap scrape result into session state ──────────
def _apply_mymap_result(scrape_result: dict):
    """Store a scrape result dict into session state and render success/error."""
    debug_report = format_debug_report(scrape_result)
    st.session_state.mymap_scrape_result = scrape_result
    st.session_state.mymap_debug_report  = debug_report

    if scrape_result["success"]:
        completed     = scrape_result["ge_completed"]
        remaining     = scrape_result["ge_remaining"]
        courses_taken = scrape_result["completed_courses"] | scrape_result["in_progress_courses"]

        st.session_state.pdf_completed   = completed
        st.session_state.pdf_remaining   = remaining or (set(GE_CATEGORIES.keys()) - completed)
        st.session_state.courses_taken   = courses_taken
        st.session_state.manual_override = False
        st.session_state.data_source     = "mymap"

        if courses_taken:
            st.session_state.pathway_state = get_remaining_requirements(courses_taken, completed)

        st.success(
            f"✅ MyMap imported successfully! "
            f"Found **{len(completed)}** completed GE categories "
            f"and **{len(courses_taken)}** individual courses."
        )
    else:
        st.session_state.mymap_login_error = scrape_result.get("error")
        dbg = scrape_result.get("debug", {})
        if dbg.get("duo_detected"):
            st.error(
                "⚠️ **Duo 2FA Detected** — The direct login cannot complete MFA. "
                "Use the **Open Browser** button above (it lets you complete Duo yourself), "
                "or try the **Upload PDF** / **Manual Entry** tab."
            )
        else:
            st.error(
                f"❌ Failed: {scrape_result.get('error', 'Unknown error')}  \n"
                "Please try the browser login, or use the PDF/Manual tab."
            )


# ── Tab 1: MyMap Login ────────────────────────────────────────────
with input_tab1:

    if IS_RAILWAY:
        # ══════════════════════════════════════════════════════════════════
        # RAILWAY MODE — Headless Chrome with visual step-by-step Streamlit UI
        # ══════════════════════════════════════════════════════════════════
        phase = st.session_state.get("railway_login_phase", "idle")

        # Stale driver cleanup on session reset
        if phase == "idle" and st.session_state.get("railway_driver") is not None:
            try:
                st.session_state.railway_driver.quit()
            except Exception:
                pass
            del st.session_state["railway_driver"]

        # ── Phase: idle — start button ────────────────────────────────
        if phase == "idle":
            st.markdown("### Log In to MyMap")
            st.caption(
                "Click below to open a secure headless browser session. "
                "You can enter your credentials and complete Duo 2FA entirely within this page."
            )
            if st.button("🌐 Start Secure Browser Login", type="primary", key="railway_start_btn"):
                st.session_state.mymap_scrape_result = None
                st.session_state.mymap_debug_report  = None
                with st.spinner("Opening secure browser and loading BYU login page..."):
                    try:
                        _driver = create_driver(headless=True)
                        _shot   = navigate_to_login(_driver)
                        st.session_state.railway_driver      = _driver
                        st.session_state.railway_screenshot  = _shot
                        st.session_state.railway_login_phase = "login_form"
                    except Exception as _e:
                        st.error(f"❌ Failed to launch browser: {_e}")
                        st.stop()
                st.rerun()

        # ── Phase: login_form — show screenshot + credential form ─────
        elif phase == "login_form":
            st.markdown("### Enter Your BYU Credentials")
            st.caption(
                "The browser has loaded the BYU login page (shown below). "
                "Enter your NetID and password — the app will fill them in for you."
            )
            _shot = st.session_state.get("railway_screenshot", "")
            if _shot:
                st.markdown(
                    f'<img src="data:image/png;base64,{_shot}" '
                    f'style="width:100%;border-radius:8px;border:1px solid #E4E3DC;margin-bottom:1rem;" />',
                    unsafe_allow_html=True,
                )
                st.caption("↑ Current browser view — BYU CAS Login Page")

            with st.form("railway_creds_form"):
                _netid    = st.text_input("BYU NetID", placeholder="e.g. jsmith123")
                _password = st.text_input("BYU Password", type="password")
                _submit   = st.form_submit_button("🔑 Fill In & Log In", type="primary")

            if st.button("✕ Cancel", key="railway_cancel_creds"):
                _cleanup_railway_session()
                st.rerun()

            if _submit:
                if not _netid or not _password:
                    st.error("Please enter both your NetID and password.")
                else:
                    _driver = st.session_state.get("railway_driver")
                    if not _driver:
                        st.error("Browser session lost — please restart.")
                        st.session_state.railway_login_phase = "idle"
                        st.rerun()

                    with st.spinner("Filling credentials and logging in..."):
                        try:
                            fill_cas_credentials(_driver, _netid, _password)
                        except Exception as _e:
                            st.error(f"❌ Could not fill credentials: {_e}")
                            _cleanup_railway_session()
                            st.stop()

                    _state = detect_login_state(_driver)
                    _shot  = take_screenshot_base64(_driver)
                    st.session_state.railway_screenshot = _shot

                    if _state == "logged_in":
                        with st.spinner("Session captured — scraping degree audit..."):
                            _result = scrape_from_driver(_driver)
                        _cleanup_railway_session()
                        _apply_mymap_result(_result)

                    elif _state == "duo":
                        st.session_state.railway_login_phase = "duo"
                        st.rerun()

                    else:
                        st.error(
                            f"Login failed or unexpected page (detected: **{_state}**).  \n"
                            "Please check your credentials and try again."
                        )
                        st.session_state.railway_login_phase = "login_form"
                        st.rerun()

        # ── Phase: duo — show Duo screenshot + approval flow ──────────
        elif phase == "duo":
            st.markdown("### Duo 2FA — Approve on Your Phone")
            st.caption(
                "The browser reached the Duo authentication step (shown below). "
                "Check your phone for a push notification and approve it, then click **Continue** here."
            )
            _shot = st.session_state.get("railway_screenshot", "")
            if _shot:
                st.markdown(
                    f'<img src="data:image/png;base64,{_shot}" '
                    f'style="width:100%;border-radius:8px;border:1px solid #E4E3DC;margin-bottom:1rem;" />',
                    unsafe_allow_html=True,
                )
                st.caption("↑ Current browser view — Duo 2FA")

            st.info(
                "📱 **Check your phone** for a Duo push notification and approve it, "
                "then click **Continue** below."
            )

            _duo_c1, _duo_c2, _duo_c3 = st.columns([3, 2, 1])

            with _duo_c1:
                if st.button("✅ I've approved — Continue", type="primary", key="railway_duo_continue"):
                    _driver = st.session_state.get("railway_driver")
                    if not _driver:
                        st.error("Browser session lost — please restart.")
                        _cleanup_railway_session()
                        st.rerun()

                    with st.spinner("Checking login status..."):
                        time.sleep(2)
                        _state = detect_login_state(_driver)
                        _shot  = take_screenshot_base64(_driver)
                    st.session_state.railway_screenshot = _shot

                    if _state == "logged_in":
                        with st.spinner("Session captured — scraping degree audit..."):
                            _result = scrape_from_driver(_driver)
                        _cleanup_railway_session()
                        _apply_mymap_result(_result)
                    else:
                        st.warning(
                            "Duo approval not yet detected. "
                            "Please approve on your phone, then click Continue again."
                        )
                        st.rerun()

            with _duo_c2:
                if st.button("🔄 Refresh Screenshot", key="railway_duo_refresh"):
                    _driver = st.session_state.get("railway_driver")
                    if _driver:
                        st.session_state.railway_screenshot = take_screenshot_base64(_driver)
                    st.rerun()

            with _duo_c3:
                if st.button("✕ Cancel", key="railway_duo_cancel"):
                    _cleanup_railway_session()
                    st.rerun()

    else:
        # ══════════════════════════════════════════════════════════════════
        # LOCAL MODE — Visible browser window the user interacts with
        # ══════════════════════════════════════════════════════════════════

        # ── Primary: Open a real Chrome window ───────────────────────────
        st.markdown("### Open a Browser Window to Log In")
        st.caption(
            "Click below. A Chrome window will open pointing to mymap.byu.edu. "
            "Log in normally — including Duo 2FA — then return to this tab. "
            "The app automatically captures your session. "
            "**Your credentials never pass through this app.**"
        )

        if not HAS_SELENIUM:
            st.warning(
                "⚠️ Browser login requires `selenium` and `webdriver-manager`. "
                "Run: `pip install selenium webdriver-manager`  \n"
                "Or use the direct login or PDF/Manual tab below."
            )
        else:
            if st.button("🌐 Open Browser & Log In to MyMap", type="primary", key="browser_login_btn"):
                st.session_state.mymap_scrape_result = None
                st.session_state.mymap_debug_report  = None
                st.session_state.mymap_login_error   = None

                with st.spinner(
                    "🌐 Browser window open — log in (including Duo 2FA), "
                    "then return here. Waiting up to 3 minutes..."
                ):
                    scrape_result = browser_login_and_scrape(timeout_seconds=180)

                _apply_mymap_result(scrape_result)

        st.divider()

        # ── Fallback: Direct credential POST ─────────────────────────────
        with st.expander(
            "Or log in directly (no browser — Duo 2FA not supported)",
            expanded=not HAS_SELENIUM,
        ):
            st.caption(
                "Submits credentials directly to BYU's CAS server. "
                "**Cannot complete Duo 2FA** — use the browser option above if you have 2FA enabled."
            )

            with st.form("mymap_login_form"):
                netid_input    = st.text_input("BYU NetID", placeholder="e.g. jsmith123")
                password_input = st.text_input("BYU Password", type="password")
                login_btn      = st.form_submit_button("🔑 Log in & Import", type="primary")

            if login_btn:
                if not netid_input or not password_input:
                    st.error("Please enter both your NetID and password.")
                else:
                    st.session_state.mymap_scrape_result = None
                    st.session_state.mymap_debug_report  = None
                    st.session_state.mymap_login_error   = None

                    with st.spinner("🔐 Logging into MyMap and scraping degree audit..."):
                        scrape_result = login_and_scrape(netid_input, password_input)

                    _apply_mymap_result(scrape_result)

    # ── Debug output (shown after any successful scrape, both modes) ──────────
    if st.session_state.mymap_debug_report:
        result = st.session_state.mymap_scrape_result
        with st.expander("🔍 Full Debug Output — Verify Accuracy Before Optimizing", expanded=True):
            st.caption(
                "Review everything the scraper found below. "
                "If any GE category status looks wrong, switch to the **Manual Entry** tab to correct it."
            )
            st.code(st.session_state.mymap_debug_report, language=None)

        if result and result.get("raw_requirements"):
            st.markdown("#### 📋 Detected GE Status")
            req_col1, req_col2 = st.columns(2)
            items = list(result["raw_requirements"].items())
            for i, (cat, info) in enumerate(items):
                col  = req_col1 if i % 2 == 0 else req_col2
                icon = {"completed": "✅", "in_progress": "🔄", "remaining": "❌"}.get(
                    info["status"], "❓"
                )
                col.markdown(f"{icon} **{cat}** — _{info['status']}_")

# ── Tab 2: PDF Upload ─────────────────────────────────────────────
with input_tab2:
    st.markdown("### Upload a BYU MyMap Degree Audit PDF")
    st.caption("Export your degree audit from MyMap as a PDF and upload it here.")

    with st.expander("❓ How do I export the PDF?"):
        st.markdown("""
**Step 1** — Go to [mymap.byu.edu](https://mymap.byu.edu) and log in.

**Step 2** — Click **Degree Audit** or **Academic Plan** from the dashboard.

**Step 3** — Click **Print** or **Export**, change destination to **Save as PDF**, click Save.

**Step 4** — Upload the saved PDF below.

---
🔒 Your PDF is processed locally and never stored or shared.
        """)

    uploaded_pdf = st.file_uploader(
        "Upload BYU MyMap Degree Audit PDF",
        type=["pdf"],
        help="Download from MyMap → Degree Audit → Save as PDF"
    )

    if uploaded_pdf is not None:
        if not HAS_PDFPLUMBER:
            st.error("⚠️ pdfplumber is not installed. Please use Manual Entry instead.")
            st.session_state.manual_override = True
        else:
            with st.spinner("📄 Parsing PDF..."):
                parse_result = parse_degree_audit(uploaded_pdf)

            if parse_result["error"]:
                st.warning(f"⚠️ Could not fully parse PDF: {parse_result['error']}")
                st.session_state.manual_override = True

            elif parse_result["parse_confidence"] == "low":
                st.warning("⚠️ Low confidence parse — please verify below or use Manual Entry.")
                st.session_state.pdf_completed   = parse_result["completed"]
                st.session_state.pdf_remaining   = parse_result["remaining"]
                st.session_state.manual_override = True

            else:
                completed     = parse_result["completed"]
                courses_taken = parse_result.get("courses_taken", set())
                st.session_state.pdf_completed   = completed
                st.session_state.pdf_remaining   = parse_result["remaining"]
                st.session_state.pdf_confidence  = parse_result["parse_confidence"]
                st.session_state.courses_taken   = courses_taken
                st.session_state.manual_override = False
                st.session_state.data_source     = "pdf"

                if courses_taken:
                    st.session_state.pathway_state = get_remaining_requirements(courses_taken, completed)

                st.success(
                    f"✅ PDF parsed ({parse_result['parse_confidence']} confidence). "
                    f"Found **{len(completed)}** completed categories"
                    + (f" and **{len(courses_taken)}** individual courses." if courses_taken else ".")
                )

    # Show PDF summary if available and this is the active data source
    if (
        st.session_state.pdf_completed is not None
        and not st.session_state.manual_override
        and st.session_state.data_source == "pdf"
    ):
        sum_col1, sum_col2 = st.columns(2)
        with sum_col1:
            st.markdown("**✅ Completed:**")
            for cat in sorted(st.session_state.pdf_completed):
                st.markdown(f'<span class="already-done-pill">✓ {cat}</span>', unsafe_allow_html=True)
        with sum_col2:
            st.markdown("**📌 Remaining:**")
            for cat in sorted(st.session_state.pdf_remaining or []):
                st.markdown(f'<span class="uncovered-pill">→ {cat}</span>', unsafe_allow_html=True)

# ── Tab 3: Manual Entry ───────────────────────────────────────────
with input_tab3:
    st.markdown("### Manually Select Completed GE Categories")
    st.caption("Check off every GE requirement you've already completed:")

    all_cats        = sorted(GE_CATEGORIES.keys())
    default_checked = sorted(st.session_state.pdf_completed or st.session_state.manual_completed)

    manual_cols     = st.columns(2)
    manual_selected = set()
    for i, cat in enumerate(all_cats):
        col     = manual_cols[i % 2]
        already = cat in default_checked
        if col.checkbox(cat, value=already, key=f"manual_{cat}"):
            manual_selected.add(cat)

    if st.button("Apply Manual Selection"):
        st.session_state.manual_completed = manual_selected
        st.session_state.pdf_completed    = manual_selected
        st.session_state.pdf_remaining    = set(GE_CATEGORIES.keys()) - manual_selected
        st.session_state.data_source      = "manual"
        st.session_state.manual_override  = False
        remaining_count = len(st.session_state.pdf_remaining)
        st.success(
            f"**{len(manual_selected)}** categories marked complete → "
            f"optimizing for **{remaining_count}** remaining."
        )

# ── Global fallback notice ────────────────────────────────────────
if st.session_state.manual_override:
    st.warning(
        "⚠️ The automatic import couldn't fully determine your completions. "
        "Please use the **Manual Entry** tab to select what you've completed, "
        "then run the optimizer."
    )

st.divider()


# ════════════════════════════════════════════════════════════════
# STEP 2 — Optimizer Options + Run
# ════════════════════════════════════════════════════════════════
st.markdown("## Step 2 — Run the Optimizer")

with st.sidebar:
    st.markdown("### Optimizer")
    use_ilp  = st.toggle("ILP Optimization", value=True,
                         help="Finds the true minimum number of courses. Greedy is faster but not always optimal.")
    skip_rmp = st.toggle("Skip RMP Ratings", value=False,
                         help="Skip RateMyProfessors lookup (faster, but no professor data)")
    refresh  = st.toggle("Refresh Catalog", value=False,
                         help="Re-scrape BYU catalog. Slow — only use if data seems outdated.")
    st.divider()
    st.markdown("### Sort Priority")
    sort_priority = st.radio(
        "",
        options=["Balanced", "Fewest Classes", "Best Professor", "Easiest Classes"],
        index=0,
        label_visibility="collapsed",
        help=(
            "**Balanced** — Double-dippers first, then highest RMP rating, then lowest difficulty.\n\n"
            "**Fewest Classes** — Maximise GE categories covered per course.\n\n"
            "**Best Professor** — Highest RMP overall rating.\n\n"
            "**Easiest Classes** — Lowest RMP difficulty score."
        ),
    )
    st.divider()
    st.caption("Python · PuLP · Streamlit")
    st.caption("BYU Catalog · RateMyProfessors")

with st.expander("🔍 Debug: What the Optimizer Will See", expanded=False):
    _completed  = st.session_state.pdf_completed or set()
    _remaining  = st.session_state.pdf_remaining or set(GE_CATEGORIES.keys())
    _taken      = st.session_state.courses_taken or set()
    _debug_cols = st.columns(3)
    with _debug_cols[0]:
        st.markdown("**✅ Completed (skipped):**")
        if _completed:
            for _c in sorted(_completed):
                st.caption(f"✓ {_c}")
        else:
            st.caption("None — optimizing all 13 categories")
    with _debug_cols[1]:
        st.markdown("**📌 Remaining (optimizer targets):**")
        for _c in sorted(_remaining):
            st.caption(f"→ {_c}")
    with _debug_cols[2]:
        st.markdown("**📚 Individual courses taken:**")
        if _taken:
            for _c in sorted(_taken):
                st.caption(f"· {_c}")
        else:
            st.caption("None detected")
    st.caption(
        f"Source: **{st.session_state.data_source or 'none selected'}** · "
        f"{len(_completed)} completed · {len(_remaining)} remaining · "
        f"{len(_taken)} courses taken"
    )
    if st.session_state.data_source is None:
        st.warning("⚠️ No data source selected yet — go to Step 1 and log in, upload PDF, or select manually.")

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
    selected     = list(st.session_state.results)   # copy so we can re-sort for display
    uncovered    = st.session_state.uncovered
    already_done = st.session_state.pdf_completed or set()

    # ── Apply sort priority (dynamically, no need to re-run optimizer) ────────
    if sort_priority == "Best Professor":
        selected.sort(key=lambda c: -(c.get("rmp_rating") or 0))
    elif sort_priority == "Easiest Classes":
        selected.sort(key=lambda c: (
            (c.get("rmp_difficulty") or 0) == 0,   # push no-data courses to end
            c.get("rmp_difficulty") or 99,
        ))
    elif sort_priority == "Fewest Classes":
        selected.sort(key=lambda c: -len(c.get("ge_categories", [])))
    else:  # Balanced (default)
        selected.sort(key=lambda c: (
            -len(c.get("ge_categories", [])),       # most categories first
            -(c.get("rmp_rating") or 0),            # then highest RMP rating
            c.get("rmp_difficulty") or 99,          # then lowest difficulty
        ))

    all_cats             = set(GE_CATEGORIES.keys())
    covered_by_optimizer = all_cats - uncovered - already_done
    total_credits        = sum(c.get("credit_hours", 3) for c in selected)
    # Double-dippers: use ge_categories_all (original full list) so that courses
    # covering 2+ GE categories by design still show up even if one is already done.
    double_dippers       = [c for c in selected if len(c.get("ge_categories_all", c.get("ge_categories", []))) > 1]

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
                # state is a PathwayResult dataclass — use attribute access
                taken_str = ", ".join(state.already_taken) or "none"
                needed    = state.courses_remaining
                pathway   = state.pathway.description
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
        col_hdr, col_sort_label = st.columns([3, 1])
        with col_hdr:
            if already_done:
                st.caption(
                    f"Showing only courses for your **{len(st.session_state.pdf_remaining or all_cats)}** "
                    f"remaining GE categories — {len(already_done)} already-completed categories excluded."
                )
        with col_sort_label:
            st.caption(f"🏆 Sorted by: **{sort_priority}**")

        rows = []
        for c in selected:
            profs = c.get("professors", [])
            top   = profs[0] if profs else None
            cats  = c.get("ge_categories", [])

            has_rating     = top is not None and (top.get("rating") or 0) > 0
            has_difficulty = top is not None and (top.get("difficulty") or 0) > 0
            has_wta        = top is not None and (top.get("would_take_again") or -1) >= 0

            cats_all = c.get("ge_categories_all", cats)
            rows.append({
                "Course":           c["course_code"],
                "Name":             c["course_name"],
                "Credits":          c.get("credit_hours", 3),
                "GE Categories":    ", ".join(cats),
                "# Categories":     len(cats_all),  # total by design (incl. already-done)
                "Top Professor":    top["name"] if top else "No ratings yet",
                "Rating (/5)":      round(top["rating"], 1)          if has_rating     else None,
                "Difficulty (/5)":  round(top["difficulty"], 1)      if has_difficulty else None,
                "Would Take Again": f"{top['would_take_again']:.0f}%" if has_wta        else "—",
            })

        df = pd.DataFrame(rows)

        def color_rating(val):
            if pd.isna(val):  return "color: #B0AFA8; font-style: italic"
            if val >= 4.0:    return "color: #1B6B3A; font-weight: 600"
            if val >= 3.0:    return "color: #8A5A00"
            return "color: #B33000"

        def color_difficulty(val):
            if pd.isna(val):  return "color: #B0AFA8; font-style: italic"
            if val <= 2.5:    return "color: #1B6B3A"
            if val <= 3.5:    return "color: #8A5A00"
            return "color: #B33000; font-weight: 600"

        max_cats = int(df["# Categories"].max()) if not df.empty else 0

        def highlight_cat_count(val):
            if max_cats > 1 and val == max_cats:
                return "background-color: #FEF3EC; color: #B33000; font-weight: 600"
            return ""

        styled = (
            df.style
            .format({
                "Rating (/5)":     lambda v: f"{v:.1f}" if pd.notna(v) else "No ratings yet",
                "Difficulty (/5)": lambda v: f"{v:.1f}" if pd.notna(v) else "No ratings yet",
            })
            .applymap(color_rating,       subset=["Rating (/5)"])
            .applymap(color_difficulty,   subset=["Difficulty (/5)"])
            .applymap(highlight_cat_count, subset=["# Categories"])
        )

        st.dataframe(styled, use_container_width=True, hide_index=True)

        # ── Legend ────────────────────────────────────────────────
        with st.expander("ℹ️ Column Guide", expanded=False):
            st.markdown("""
| Column | Meaning |
|--------|---------|
| **Rating (/5)** | RMP overall professor rating (5 = best). Green ≥ 4.0, orange ≥ 3.0, red < 3.0 |
| **Difficulty (/5)** | RMP difficulty score (lower = easier). Green ≤ 2.5, orange ≤ 3.5, red > 3.5 |
| **Would Take Again** | % of students who would re-take this professor's class |
| **# Categories** | How many of your *remaining* GE requirements this course covers. Highlighted yellow = most categories per course |
| **Top Professor** | Highest-rated professor in that department on RateMyProfessors. Note: RMP doesn't filter by specific course section — this is the best-rated professor in the department, not necessarily who teaches *this* course number |
| **No ratings yet** | No RMP data found for professors in this department |
""")

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
            for c in sorted(double_dippers, key=lambda x: -len(x.get("ge_categories_all", x.get("ge_categories", [])))):
                cats_remaining = c.get("ge_categories", [])
                cats_all       = c.get("ge_categories_all", cats_remaining)
                cats_done      = [cat for cat in cats_all if cat not in cats_remaining]
                profs = c.get("professors", [])
                top   = profs[0] if profs else None
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### `{c['course_code']}` — {c['course_name']}")
                        remaining_pills = " · ".join(
                            f'<span class="covered-pill">{cat}</span>'
                            for cat in cats_remaining
                        )
                        done_pills = " · ".join(
                            f'<span class="already-done-pill">✓ {cat}</span>'
                            for cat in cats_done
                        )
                        display_pills = " · ".join(filter(None, [remaining_pills, done_pills]))
                        st.markdown(display_pills, unsafe_allow_html=True)
                        if cats_done:
                            st.caption(f"Blue = already satisfied · Green = still needed")
                    with col2:
                        st.metric("Covers (total)", len(cats_all))
                        st.metric("Still Needed", len(cats_remaining))
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
