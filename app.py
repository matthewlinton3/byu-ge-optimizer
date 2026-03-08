"""
BYU GE Optimizer — Streamlit entry point.
Sets page config and redirects to the Setup page.

NOTE: Do NOT call inject_styles() here. Calling st.markdown() before
st.switch_page() causes Streamlit to render the CSS string as visible
text content before the redirect fires. Each page injects its own styles.
"""

import streamlit as st

st.set_page_config(
    page_title="BYU GE Optimizer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.switch_page("pages/1_Setup.py")
