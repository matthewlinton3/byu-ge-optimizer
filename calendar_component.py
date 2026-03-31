"""
Blackout calendar Streamlit component.
Declared here (not inside a page file) so Streamlit's frame inspection works.
"""
import os
import streamlit.components.v1 as components

_COMPONENT_DIR = os.path.join(os.path.dirname(__file__), "components", "blackout_calendar")
blackout_calendar = components.declare_component("blackout_calendar", path=_COMPONENT_DIR)
