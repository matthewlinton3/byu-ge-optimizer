"""
BYU GE Optimizer — Streamlit entry point.
Sets page config and redirects to the Setup page.
"""

import streamlit as st
from styles import inject_styles

st.set_page_config(
    page_title="BYU GE Optimizer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

st.switch_page("pages/1_Setup.py")
