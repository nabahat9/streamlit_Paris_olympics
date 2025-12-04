import pandas as pd
import streamlit as st

@st.cache_data
def load_athletes():
    return pd.read_csv("data/athletes.csv")

@st.cache_data
def load_medals_total():
    return pd.read_csv("data/medals_total.csv")

@st.cache_data
def load_events():
    return pd.read_csv("data/events.csv")

athletes = load_athletes()
medals_total = load_medals_total()
events = load_events()
