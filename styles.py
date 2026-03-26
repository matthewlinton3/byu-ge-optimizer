"""
BYU GE Optimizer — Shared styles (dark theme).

inject_styles() must be called at the top of every page.
CSS is injected via st.html() (Streamlit 1.37+) to avoid markdown stripping <style> tags.
"""

import streamlit as st

_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans'
    ':ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">'
)

_CSS = """
/* ── Color variables ──────────────────────────────────────────── */
:root {
    --bg-base:        #0F1117;
    --bg-card:        #1A1F2E;
    --bg-elevated:    #242B3D;
    --border:         #2D3548;
    --byu-navy:       #002E5D;
    --byu-blue:       #0062B8;
    --byu-blue-hover: #0074DB;
    --text-primary:   #F0F4FF;
    --text-secondary: #8892A4;
    --text-hint:      #5A6478;
    --success:        #22C55E;
    --warning:        #F59E0B;
    --error:          #EF4444;
    --pill-bg:        #1E2D4A;
    --radius:         12px;
    --shadow-sm:      0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.25);
    --shadow-md:      0 4px 12px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.3);
}

/* ── Page background ──────────────────────────────────────────── */
.stApp, [data-testid="stAppViewContainer"], html, body {
    background: #0F1117 !important;
    color: #F0F4FF !important;
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}
.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem !important;
    max-width: 1060px !important;
    background: transparent !important;
}

/* ── Hide ALL Streamlit chrome ─────────────────────────────────── */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}
header[data-testid="stHeader"] { background: #0F1117 !important; }

/* ── Default text ─────────────────────────────────────────────── */
body, p, li, span, label, .stMarkdown,
[data-testid="stMarkdownContainer"],
[data-testid="stCaptionContainer"],
.stCaption {
    color: #F0F4FF !important;
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
}

/* ── Headings ─────────────────────────────────────────────────── */
h1, h2, h3, h4,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

/* ── Inputs ───────────────────────────────────────────────────── */
input, textarea,
[data-testid="stTextInput"] input,
.stTextInput input {
    background: #242B3D !important;
    color: #F0F4FF !important;
    border: 1px solid #2D3548 !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
input:focus, textarea:focus {
    border-color: #0062B8 !important;
    box-shadow: 0 0 0 3px rgba(0,98,184,0.2) !important;
    outline: none !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ── Tabs ─────────────────────────────────────────────────────── */
[data-testid="stTabs"],
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid #2D3548 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"],
.stTabs [data-baseweb="tab"] {
    color: #8892A4 !important;
    background: transparent !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"],
.stTabs [aria-selected="true"] {
    color: #F0F4FF !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: var(--byu-blue) !important; }

/* ── Buttons ──────────────────────────────────────────────────── */
.stButton button,
button[data-testid="baseButton-primary"],
.stFormSubmitButton button {
    background: #0062B8 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: background 0.15s !important;
    letter-spacing: 0.01em;
}
.stButton button:hover,
button[data-testid="baseButton-primary"]:hover,
.stFormSubmitButton button:hover {
    background: #0074DB !important;
    color: #fff !important;
}
.stButton > button:not([data-testid="baseButton-primary"]) {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    border: 1.5px solid var(--border) !important;
}
.stButton > button:not([data-testid="baseButton-primary"]):hover {
    border-color: var(--byu-blue) !important;
}

/* ── File uploader ────────────────────────────────────────────── */
[data-testid="stFileUploadDropzone"],
[data-testid="stFileUploader"] section {
    background: #1A1F2E !important;
    border: 2px dashed #2D3548 !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploadDropzone"]:hover,
[data-testid="stFileUploader"] section:hover {
    border-color: #0062B8 !important;
    background: #1E253A !important;
}
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"] {
    border-color: var(--byu-blue) !important;
    color: var(--byu-blue) !important;
    background: transparent !important;
}

/* ── Expanders ────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #1A1F2E !important;
    border: 1px solid #2D3548 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: #F0F4FF !important;
    font-weight: 500 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Alerts ───────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 8px !important; }
[data-testid="stInfo"] {
    background: #0D1F3C !important;
    border: 1px solid #1E3A5F !important;
    border-radius: 8px !important;
}
[data-testid="stSuccess"] {
    background: #0A2518 !important;
    border: 1px solid #14532D !important;
    border-radius: 8px !important;
}
[data-testid="stWarning"] {
    background: #2A1F09 !important;
    border: 1px solid #78350F !important;
    border-radius: 8px !important;
}
[data-testid="stError"] {
    background: #2A0A0A !important;
    border: 1px solid #7F1D1D !important;
    border-radius: 8px !important;
}

/* ── Metrics ──────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #1A1F2E;
    border: 1px solid #2D3548;
    border-radius: 10px;
    padding: 1rem 1.25rem;
}
[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] {
    color: #F0F4FF !important;
    font-weight: 700 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 2rem !important;
}
[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] {
    color: #8892A4 !important;
    text-transform: uppercase;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Checkboxes & radio buttons ───────────────────────────────── */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p,
[data-testid="stRadio"] label,
[data-testid="stRadio"] p {
    color: #F0F4FF !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Selectbox ────────────────────────────────────────────────── */
[data-testid="stSelectbox"] select,
[data-testid="stSelectbox"] div {
    background: #242B3D !important;
    color: #F0F4FF !important;
}

/* ── Toggle ───────────────────────────────────────────────────── */
[data-testid="stToggle"] label,
[data-testid="stToggle"] p { color: #F0F4FF !important; }
[data-testid="stToggle"][aria-checked="true"],
[role="switch"][aria-checked="true"] { background: var(--byu-blue) !important; }

/* ── Progress bar ─────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div {
    background: var(--bg-elevated) !important;
    border-radius: 4px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: var(--byu-blue) !important;
    border-radius: 4px !important;
}

/* ── Dividers ─────────────────────────────────────────────────── */
hr { border-color: #2D3548 !important; margin: 1.5rem 0 !important; }

/* ── Status box ───────────────────────────────────────────────── */
[data-testid="stStatusWidget"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Container borders ────────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--border) !important;
    border-left: 4px solid var(--byu-blue) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-card) !important;
}

/* ── Top nav bar ──────────────────────────────────────────────── */
.byu-topnav {
    position: sticky;
    top: 0;
    z-index: 999;
    background: #002E5D;
    border-bottom: 1px solid #0062B8;
    padding: 0.75rem 2rem;
    margin: -1rem -5rem 1.5rem -5rem;
}
.byu-topnav-inner { display: flex; align-items: center; gap: 1rem; }
.byu-topnav-logo {
    color: #fff;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    font-family: 'IBM Plex Sans', sans-serif;
}
.byu-topnav-sub {
    color: rgba(255,255,255,0.55);
    font-size: 0.85rem;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Hero ─────────────────────────────────────────────────────── */
.byu-hero {
    background: linear-gradient(135deg, #0D1B35 0%, #1A2744 100%);
    border: 1px solid #2D3548;
    border-radius: 16px;
    padding: 3rem 2.5rem;
    margin-bottom: 2.5rem;
    text-align: center;
}
.byu-hero-eyebrow {
    color: #0062B8;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    font-family: 'IBM Plex Sans', sans-serif;
}
.byu-hero-title {
    color: #F0F4FF !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    margin: 0 0 1rem 0 !important;
    line-height: 1.2;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.byu-hero-sub {
    color: #8892A4 !important;
    font-size: 1rem;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Step headers ─────────────────────────────────────────────── */
.byu-step-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0 1rem 0;
    padding-bottom: 1rem;
    border-bottom: 1px solid #2D3548;
}
.byu-step-num {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #0062B8;
    color: #fff;
    font-weight: 700;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-family: 'IBM Plex Sans', sans-serif;
}
.byu-step-title {
    color: #F0F4FF !important;
    font-size: 1.2rem;
    font-weight: 600;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.byu-step-desc {
    color: #8892A4 !important;
    font-size: 0.85rem;
    margin-top: 0.15rem;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Privacy note ─────────────────────────────────────────────── */
.byu-privacy-note {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.8rem;
    color: var(--text-secondary) !important;
    margin-bottom: 1rem;
    justify-content: center;
}

/* ── MyMap login notices ──────────────────────────────────────── */
.byu-security-notice {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    background: #0A2518;
    border: 1px solid #14532D;
    border-left: 4px solid #22C55E;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 1.25rem;
    font-family: 'IBM Plex Sans', sans-serif;
}
.byu-security-notice .sec-icon { font-size: 1.25rem; flex-shrink: 0; line-height: 1.3; }
.byu-security-notice .sec-text { font-size: 0.82rem; color: #4ADE80 !important; line-height: 1.5; }
.byu-security-notice .sec-text strong { color: #86EFAC !important; font-weight: 600; }
.byu-duo-notice {
    background: #2A1F09;
    border: 1px solid #78350F;
    border-left: 4px solid #F97316;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-top: 1rem;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    color: #FCD34D !important;
    line-height: 1.55;
}

/* ── GE progress pills ────────────────────────────────────────── */
.byu-progress-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--text-secondary) !important;
    margin-bottom: 0.5rem;
}
.byu-pill {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 100px;
    font-size: 0.775rem;
    font-weight: 500;
    margin: 2px 3px 2px 0;
    font-family: 'IBM Plex Sans', sans-serif;
    letter-spacing: 0.01em;
}
.byu-pill-done      { background: #0A2518; color: #4ADE80; border: 1px solid #14532D; }
.byu-pill-remaining { background: #0D1F3C; color: #60A5FA; border: 1px solid #1E3A5F; }
.byu-pill-uncovered { background: #2A0A0A; color: #F87171; border: 1px solid #7F1D1D; }

/* ── Cards (generic) ─────────────────────────────────────────── */
.byu-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}

/* ── Course cards (dark) ──────────────────────────────────────── */
.course-card {
    background: #1A1F2E;
    border: 1px solid #2D3548;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.15s, transform 0.15s;
}
.course-card:hover { border-color: #0062B8; transform: translateY(-2px); }
.course-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.35rem;
}
.course-code {
    color: #F0F4FF;
    font-weight: 700;
    font-size: 1rem;
    font-family: 'IBM Plex Sans', sans-serif;
}
.rmp-badge {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
}
.rmp-good { background: #14532D; color: #4ADE80; }
.rmp-mid  { background: #78350F; color: #FBBF24; }
.rmp-bad  { background: #450A0A; color: #F87171; }
.rmp-none { background: #1E2535; color: #5A6478; }
.course-name {
    color: #8892A4;
    font-size: 0.85rem;
    margin-bottom: 0.75rem;
    font-family: 'IBM Plex Sans', sans-serif;
}
.ge-pills { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.25rem; }
.ge-pill {
    background: #1E2D4A;
    color: #60A5FA;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    border: 1px solid #2D4A7A;
    font-family: 'IBM Plex Sans', sans-serif;
}
.prof-row {
    margin-top: 0.65rem;
    padding-top: 0.65rem;
    border-top: 1px solid #2D3548;
    font-size: 0.82rem;
    color: #8892A4;
    font-family: 'IBM Plex Sans', sans-serif;
}
.prof-name { font-weight: 600; color: #C8D0E0; }
.stars { color: #F59E0B; font-weight: 600; }

/* ── Locked course section ────────────────────────────────────── */
.byu-locked-section {
    background: #0A2518;
    border: 1px solid #14532D;
    border-left: 4px solid #22C55E;
    border-radius: var(--radius);
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.75rem;
    font-family: 'IBM Plex Sans', sans-serif;
    color: #F0F4FF !important;
}

/* ── Schedule calendar (legacy) ───────────────────────────────── */
.sched-grid {
    display: grid;
    grid-template-columns: 60px repeat(5, 1fr);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.75rem;
    border: 1px solid #2D3548;
    border-radius: 8px;
    overflow: hidden;
}
.sched-cell {
    border-right: 1px solid #2D3548;
    border-bottom: 1px solid #2D3548;
    padding: 4px 6px;
    min-height: 24px;
    background: #0F1117;
}
.sched-cell.time { background: #12161F; font-weight: 600; color: #5A6478; }
.sched-cell.day  { background: #002E5D; font-weight: 600; color: #FFFFFF; text-align: center; }
.sched-block { border-radius: 4px; padding: 5px 7px; color: #fff; font-weight: 500; overflow: hidden; font-size: 0.72rem; }
.sched-block .code { font-weight: 700; }
"""

_TOPNAV_HTML = """
<div class="byu-topnav">
  <div class="byu-topnav-inner">
    <span class="byu-topnav-logo">GE Optimizer</span>
    <span class="byu-topnav-sub">BYU General Education Planner</span>
  </div>
</div>
"""


def inject_styles() -> None:
    """Inject dark-theme CSS, Google Fonts, and the top nav into the current page."""
    style_block = f"<style>{_CSS}</style>"
    payload = _FONTS + style_block + _TOPNAV_HTML
    if hasattr(st, "html"):
        st.html(payload)
    else:
        st.markdown(payload, unsafe_allow_html=True)
