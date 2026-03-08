"""
BYU GE Optimizer — Shared styles.
Inject at top of app so CSS applies to all content. Must use unsafe_allow_html=True.
"""

import streamlit as st

BYU_CSS = """
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

/* Locked courses section */
.byu-locked-section {
    background: #E8F5E9;
    border: 1px solid #C8E6C9;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.byu-locked-section .course-title { font-weight: 600; color: var(--byu-navy); font-size: 1.05rem; }
.byu-locked-section .course-code { color: var(--byu-royal); font-weight: 600; }

/* Schedule calendar grid */
.sched-grid { display: grid; grid-template-columns: 60px repeat(5, 1fr); grid-template-rows: auto; font-family: 'IBM Plex Sans', sans-serif; font-size: 0.75rem; border: 1px solid var(--byu-border); border-radius: 8px; overflow: hidden; }
.sched-cell { border-right: 1px solid var(--byu-border); border-bottom: 1px solid var(--byu-border); padding: 4px 6px; min-height: 24px; }
.sched-cell.time { background: var(--byu-gray); font-weight: 600; color: var(--byu-text-muted); }
.sched-cell.day { background: var(--byu-gray); font-weight: 600; color: var(--byu-navy); text-align: center; }
.sched-block { border-radius: 4px; padding: 6px 8px; color: #fff; font-weight: 500; overflow: hidden; }
.sched-block .code { font-weight: 700; }
.sched-block .prof, .sched-block .room { opacity: 0.95; font-size: 0.7rem; }

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

/* Blackout grid — weekly availability */
.byu-blackout-grid { display: grid; grid-template-columns: 48px repeat(5, 1fr); font-family: 'IBM Plex Sans', sans-serif; font-size: 0.7rem; border: 1px solid var(--byu-border); border-radius: 8px; overflow: hidden; }
.byu-blackout-cell { border-right: 1px solid var(--byu-border); border-bottom: 1px solid var(--byu-border); min-height: 22px; padding: 2px; }
.byu-blackout-cell.time { background: var(--byu-gray); font-weight: 600; color: var(--byu-text-muted); }
.byu-blackout-cell.day { background: var(--byu-gray); font-weight: 600; color: var(--byu-navy); text-align: center; }
.byu-blackout-cell.blocked { background: var(--byu-navy); opacity: 0.85; cursor: pointer; }
.byu-blackout-cell.available { background: #E8F5E9; cursor: pointer; }
.byu-blackout-cell.blocked:hover { opacity: 1; }
.byu-blackout-cell.available:hover { background: #C8E6C9; }
</style>
"""


def inject_styles():
    """Inject BYU CSS and fonts. Must be called at top of app before any other content. Uses unsafe_allow_html=True so styles apply."""
    st.markdown(BYU_CSS, unsafe_allow_html=True)
