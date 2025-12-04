import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* This is the key line → removes the sidebar entirely */
    section[data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)
# Title
st.title("🏅 My First Streamlit App")
# Set page to wide mode so cards stay in one row
st.set_page_config(layout="wide")