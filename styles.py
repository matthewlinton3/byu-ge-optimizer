"""
BYU GE Optimizer — Shared styles.

inject_styles() must be called at the top of every page.

Implementation note: CSS must NOT be pre-wrapped in <style> tags inside the
string constant. inject_styles() wraps it in <style> tags itself and injects
via st.html() (Streamlit 1.37+) so Streamlit never touches it as markdown.
Passing a <style> block through st.markdown() causes Streamlit's markdown
renderer to strip the <style> wrapper, leaving raw CSS rules as visible text.
"""

import streamlit as st

# Google Fonts — injected separately as a plain <link> block.
_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans'
    ':ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">'
)

# Pure CSS rules only — NO <style> wrapper, NO <link> tags.
_CSS = """
/* ── Variables ────────────────────────────────────────────────── */
:root {
    --byu-navy:        #002E5D;
    --byu-royal:       #0062B8;
    --byu-royal-dark:  #004C8C;
    --byu-white:       #FFFFFF;
    --byu-off-white:   #F8F9FB;
    --byu-gray:        #F2F4F7;
    --byu-gray-mid:    #E4E7EC;
    --byu-text:        #1A2332;
    --byu-text-muted:  #5A6778;
    --byu-border:      #D8DCE3;
    --shadow-sm:       0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:       0 4px 12px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06);
    --radius:          12px;
}

/* ── Reset / base ─────────────────────────────────────────────── */
html, body, .stApp {
    background-color: var(--byu-off-white) !important;
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}
.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem !important;
    max-width: 1060px !important;
}

/* ── Sidebar: hide nav list & collapse button ─────────────────── */
/* Only hide the auto-generated page links — keep sidebar for Results options */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"] {
    display: none !important;
}
/* Hide the sidebar collapse arrow on Setup page (no sidebar content there) */
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ── Sidebar: style the Options panel (Results page) ─────────── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
    background: var(--byu-gray) !important;
    border-right: 1px solid var(--byu-border) !important;
}
section[data-testid="stSidebar"] * { color: var(--byu-text) !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--byu-navy) !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
section[data-testid="stSidebar"] [data-testid="stToggle"][aria-checked="true"],
section[data-testid="stSidebar"] [role="switch"][aria-checked="true"] {
    background: var(--byu-royal) !important;
}

/* ── Top nav bar ──────────────────────────────────────────────── */
.byu-topnav {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: var(--byu-navy);
    padding: 0.75rem 2rem;
    margin: 0 -5rem 0 -5rem;   /* bleed past block-container padding */
    margin-bottom: 0;
}
.byu-topnav-logo {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.01em;
}
.byu-topnav-logo span {
    color: rgba(255,255,255,0.55);
    font-weight: 400;
    margin-left: 0.4rem;
    font-size: 0.9rem;
}

/* ── Hero ─────────────────────────────────────────────────────── */
.byu-hero {
    background: linear-gradient(135deg, #002E5D 0%, #004080 100%);
    padding: 3.5rem 2rem 3rem;
    margin: 0 -5rem 2.5rem;
    text-align: center;
}
/* Use div.byu-hero-title NOT h1 so Streamlit heading overrides don't apply */
.byu-hero-title {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 2.25rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin: 0 0 0.75rem 0 !important;
    letter-spacing: -0.025em;
    line-height: 1.15;
}
.byu-hero-desc {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.05rem !important;
    color: rgba(255, 255, 255, 0.88) !important;
    max-width: 540px;
    margin: 0 auto !important;
    line-height: 1.6;
    font-weight: 400;
}
/* Safety net: kill any Streamlit heading override that bleeds into the hero */
.byu-hero h1, .byu-hero h2, .byu-hero h3,
.byu-hero p, .byu-hero span, .byu-hero * {
    color: #FFFFFF !important;
}

/* ── Section step headers ─────────────────────────────────────── */
.byu-step {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin: 2rem 0 1rem;
}
.byu-step-num {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--byu-navy);
    color: #FFFFFF;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}
.byu-step-label {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: var(--byu-text) !important;
    margin: 0 !important;
}

/* ── Cards ────────────────────────────────────────────────────── */
.byu-card {
    background: var(--byu-white);
    border: 1px solid var(--byu-border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}
.byu-card-upload {
    max-width: 580px;
    margin-left: auto;
    margin-right: auto;
    text-align: center;
    background: var(--byu-white);
    border: 2px dashed var(--byu-gray-mid);
    border-radius: var(--radius);
    padding: 2rem 1.5rem;
}
.byu-privacy-note {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.8rem;
    color: var(--byu-text-muted);
    margin-bottom: 1rem;
    justify-content: center;
}

/* ── Course result cards ──────────────────────────────────────── */
.byu-course-card {
    background: var(--byu-white);
    border: 1px solid var(--byu-border);
    border-left: 4px solid var(--byu-royal);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.85rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.15s ease;
}
.byu-course-card:hover { box-shadow: var(--shadow-md); }
.course-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 600;
    color: var(--byu-navy);
    font-size: 1.05rem;
    margin-bottom: 0.4rem;
}
.course-code { color: var(--byu-royal); font-weight: 700; }
.ge-pills { margin: 0.5rem 0 0.25rem; }
.prof-row {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--byu-gray-mid);
    font-size: 0.875rem;
    color: var(--byu-text);
    font-family: 'IBM Plex Sans', sans-serif;
}
.prof-name { font-weight: 600; color: var(--byu-text); }
.stars { color: #F59E0B; font-weight: 600; }

/* ── GE progress pills ────────────────────────────────────────── */
.byu-progress-section { margin: 1.25rem 0; }
.byu-progress-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--byu-text-muted);
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
.byu-pill-done     { background: #DCFCE7; color: #15803D; border: 1px solid #BBF7D0; }
.byu-pill-remaining { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
.byu-pill-uncovered { background: #FEE2E2; color: #B91C1C; border: 1px solid #FECACA; }

/* ── Locked course section ────────────────────────────────────── */
.byu-locked-section {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-left: 4px solid #22C55E;
    border-radius: var(--radius);
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.75rem;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── CTA button — make primary buttons large and navy ─────────── */
button[data-testid="baseButton-primary"],
.stFormSubmitButton button {
    background: var(--byu-navy) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 0.01em;
}
button[data-testid="baseButton-primary"]:hover,
.stFormSubmitButton button:hover {
    background: var(--byu-royal) !important;
    color: #FFFFFF !important;
}
/* Secondary buttons */
.stButton > button:not([data-testid="baseButton-primary"]) {
    background: var(--byu-white) !important;
    color: var(--byu-navy) !important;
    border: 1.5px solid var(--byu-gray-mid) !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
}
.stButton > button:hover:not([data-testid="baseButton-primary"]) {
    border-color: var(--byu-navy) !important;
    color: var(--byu-navy) !important;
}

/* ── Typography overrides ─────────────────────────────────────── */
h1, h2, h3, h4,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
    color: var(--byu-text) !important;
    font-weight: 600 !important;
}
p, li, .stCaption,
[data-testid="stCaptionContainer"] {
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
    color: var(--byu-text) !important;
}

/* ── Tabs ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid var(--byu-border) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--byu-text-muted) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--byu-navy) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: var(--byu-royal) !important; }

/* ── File uploader ────────────────────────────────────────────── */
[data-testid="stFileUploader"] section {
    border: 2px dashed var(--byu-gray-mid) !important;
    border-radius: var(--radius) !important;
    background: var(--byu-off-white) !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--byu-royal) !important;
    background: #EFF6FF !important;
}
[data-testid="stFileUploader"] [data-testid="baseButton-secondary"] {
    border-color: var(--byu-royal) !important;
    color: var(--byu-royal) !important;
}

/* ── Inputs ───────────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    border: 1px solid var(--byu-border) !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    background: var(--byu-white) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--byu-royal) !important;
    box-shadow: 0 0 0 3px rgba(0,98,184,0.12) !important;
}

/* ── Metrics ──────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--byu-white);
    border: 1px solid var(--byu-border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow-sm);
}
div[data-testid="stMetricValue"] {
    color: var(--byu-navy) !important;
    font-weight: 700 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.6rem !important;
}
div[data-testid="stMetricLabel"] {
    color: var(--byu-text-muted) !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Expanders ────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--byu-border) !important;
    border-radius: var(--radius) !important;
    background: var(--byu-white) !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    color: var(--byu-text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── Alerts ───────────────────────────────────────────────────── */
[data-testid="stInfo"] {
    background: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 8px !important;
}
[data-testid="stSuccess"] {
    background: #F0FDF4 !important;
    border: 1px solid #BBF7D0 !important;
    border-radius: 8px !important;
}
[data-testid="stWarning"] {
    background: #FFFBEB !important;
    border: 1px solid #FDE68A !important;
    border-radius: 8px !important;
}
[data-testid="stError"] {
    background: #FFF1F2 !important;
    border: 1px solid #FECDD3 !important;
    border-radius: 8px !important;
}

/* ── Progress bar ─────────────────────────────────────────────── */
[data-testid="stProgressBar"] > div > div {
    background: var(--byu-royal) !important;
    border-radius: 4px !important;
}

/* ── Dividers ─────────────────────────────────────────────────── */
hr {
    border-color: var(--byu-border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Container borders ────────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--byu-border) !important;
    border-left: 4px solid var(--byu-royal) !important;
    border-radius: var(--radius) !important;
    background: var(--byu-white) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Schedule calendar grid ───────────────────────────────────── */
.sched-grid {
    display: grid;
    grid-template-columns: 60px repeat(5, 1fr);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.75rem;
    border: 1px solid var(--byu-border);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}
.sched-cell {
    border-right: 1px solid var(--byu-border);
    border-bottom: 1px solid var(--byu-border);
    padding: 4px 6px;
    min-height: 24px;
    background: var(--byu-white);
}
.sched-cell.time { background: var(--byu-gray); font-weight: 600; color: var(--byu-text-muted); }
.sched-cell.day  { background: var(--byu-navy); font-weight: 600; color: #FFFFFF; text-align: center; }
.sched-block { border-radius: 4px; padding: 5px 7px; color: #fff; font-weight: 500; overflow: hidden; font-size: 0.72rem; }
.sched-block .code { font-weight: 700; }

/* ── Blackout grid ────────────────────────────────────────────── */
.byu-blackout-grid {
    display: grid;
    grid-template-columns: 48px repeat(5, 1fr);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.7rem;
    border: 1px solid var(--byu-border);
    border-radius: 8px;
    overflow: hidden;
}
.byu-blackout-cell { border-right: 1px solid var(--byu-border); border-bottom: 1px solid var(--byu-border); min-height: 22px; padding: 2px; }
.byu-blackout-cell.time    { background: var(--byu-gray); font-weight: 600; color: var(--byu-text-muted); }
.byu-blackout-cell.day     { background: var(--byu-gray); font-weight: 600; color: var(--byu-navy); text-align: center; }
.byu-blackout-cell.blocked  { background: var(--byu-navy); opacity: 0.85; cursor: pointer; }
.byu-blackout-cell.available { background: #F0FDF4; cursor: pointer; }
.byu-blackout-cell.blocked:hover  { opacity: 1; }
.byu-blackout-cell.available:hover { background: #DCFCE7; }

/* ── Streamlit toolbar / main menu (hide deploy button etc.) ──── */
[data-testid="stToolbar"], header[data-testid="stHeader"] {
    background: var(--byu-navy) !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
"""

_TOPNAV_HTML = """
<div class="byu-topnav">
  <span class="byu-topnav-logo">
    &#127891; BYU GE Optimizer
    <span>— find your shortest path to graduation</span>
  </span>
</div>
"""


def inject_styles() -> None:
    """
    Inject BYU CSS, Google Fonts, and the top nav bar into the current page.

    Uses st.html() (Streamlit 1.37+) for the style block — the only reliable
    way to inject <style> without markdown processing stripping the tags.
    Falls back to st.markdown(unsafe_allow_html=True) for older versions.
    """
    style_block = f"<style>{_CSS}</style>"
    payload = _FONTS + style_block + _TOPNAV_HTML
    if hasattr(st, "html"):
        st.html(payload)
    else:
        st.markdown(payload, unsafe_allow_html=True)
