import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import base64

# Import shared utilities
from utils import (
    apply_custom_css, 
    render_navbar, 
    load_data, 
    get_medal_column,
    local_image_to_data_url
)

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="Olympic Games Analytics – Overview",
    page_icon="🏅",
    layout="wide",
)

# Apply custom CSS
apply_custom_css()

# Render navbar with 'overview' as active page
render_navbar(current_page="overview")

# ---------------------------
# Data loading
# ---------------------------
# NOTE: Assuming load_data() function is defined in utils.py and works correctly.
athletes_df, events_df, medals_total_df, nocs_df = load_data()

# ---------------------------
# HERO SECTION
# ---------------------------
BASE_DIR = Path(__file__).parent
HERO_IMAGE_PATH = BASE_DIR / "utils" / "picture_oly.png"

if HERO_IMAGE_PATH.exists():
    HERO_IMAGE_URL = local_image_to_data_url(str(HERO_IMAGE_PATH))
else:
    HERO_IMAGE_URL = ""

# Hero CSS specific to homepage (Now includes black color for section titles)
st.markdown(
    """
    <style>
    .full-width-hero { 
        margin-top: -9rem; 
        margin-bottom: 2.5rem;
    }
    
    .full-width-hero > div { 
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-right: calc(-50vw + 50%);
        box-shadow: 0 18px 45px rgba(15,23,42,0.35); 
    }
    
    .hero {
        width: 100%;
        position: relative;
        height: 90vh;
        overflow: hidden;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        z-index: 1; 
    }
    .hero-overlay { 
        width:600px;
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, rgba(15,23,42,0.9) 0%, rgba(15,23,42,0.4) 40%, rgba(15,23,42,0.05) 100%);
        color: #f9fafb;
        display: flex;
        flex-direction: column;
        justify-content: flex-start; 
        padding: 24px 34px;
        padding-top: 7rem; 
    }

    .hero-top-row {
        margin-top: 300px; 
        display: flex;
        flex-direction: column;
        justify-content: flex-start; 
        align-items: flex-start;
        font-size: 0.9rem;
        gap: 0.5rem; 
    }
    
    /* NEW: Set section title color to black */
    .section-card .section-title { 
        color: #000000 !important;
    }
    .section-card{
        margin:30px
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        color: #F5F5F5D6;
    }
    .hero-description {
        font-size: 1.4rem;
        font-weight: 500;
        margin-bottom: 0.4rem;
        color: #F5F5F5D6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="full-width-hero"> 
      <div class="hero" style="background-image: url('{HERO_IMAGE_URL}'); background-color: #1e3a8a;">
        <div class="hero-overlay">
          <div class="hero-top-row">
            <div class="hero-title">
                Paris 2024
            </div>
            <div class="hero-description">
                Explore the space where discipline powers every ambition, and follow the milestones that forge true champions.
            </div>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Sidebar filters
# ---------------------------
st.sidebar.header("🌍 Global Filters")

country_col = "noc"
if not medals_total_df.empty and country_col in medals_total_df.columns:
    available_nocs = sorted(medals_total_df[country_col].dropna().unique().tolist())
else:
    available_nocs = []
selected_nocs = st.sidebar.multiselect(
    "Countries (NOC)",
    options=available_nocs,
    default=available_nocs,
)

sport_col = "sport" if "sport" in events_df.columns else events_df.columns[1] if not events_df.empty and len(events_df.columns) > 1 else 'sport'
if not events_df.empty and sport_col in events_df.columns:
    available_sports = sorted(events_df[sport_col].dropna().unique().tolist())
else:
    available_sports = []
selected_sports = st.sidebar.multiselect(
    "Sports",
    options=available_sports,
    default=available_sports,
)

medal_options = ["Gold", "Silver", "Bronze"]
selected_medal_types = st.sidebar.multiselect(
    "Medal types",
    options=medal_options,
    default=medal_options,
)

# ---------------------------
# Apply filters & Derived metrics
# ---------------------------
filtered_medals = medals_total_df[
    medals_total_df[country_col].isin(selected_nocs)
] if selected_nocs and not medals_total_df.empty else medals_total_df.copy()

filtered_events = events_df[
    events_df[sport_col].isin(selected_sports)
] if selected_sports and not events_df.empty else events_df.copy()

if sport_col in athletes_df.columns:
    filtered_athletes = athletes_df[
        athletes_df[sport_col].isin(selected_sports)
    ] if selected_sports and not athletes_df.empty else athletes_df.copy()
else:
    filtered_athletes = athletes_df.copy()

total_athletes = (
    filtered_athletes["id"].nunique()
    if "id" in filtered_athletes.columns
    else len(filtered_athletes)
)
total_countries = filtered_medals[country_col].nunique() if country_col in filtered_medals.columns else 0
total_sports = filtered_events[sport_col].nunique() if sport_col in filtered_events.columns else 0

gold_col = get_medal_column(filtered_medals, "gold")
silver_col = get_medal_column(filtered_medals, "silver")
bronze_col = get_medal_column(filtered_medals, "bronze")

gold_total = filtered_medals[gold_col].sum() if gold_col and "Gold" in selected_medal_types else 0
silver_total = filtered_medals[silver_col].sum() if silver_col and "Silver" in selected_medal_types else 0
bronze_total = filtered_medals[bronze_col].sum() if bronze_col and "Bronze" in selected_medal_types else 0

total_medals = gold_total + silver_total + bronze_total

if "event_id" in filtered_events.columns:
    total_events = filtered_events["event_id"].nunique()
else:
    total_events = len(filtered_events)

# ---------------------------
# REMOVED: Static delta variables have been deleted as requested.
# ---------------------------

# ---------------------------
# Overview Dashboard Content
# ---------------------------
header_left, header_right = st.columns([0.8, 0.2])
with header_left:
    st.markdown("## 🏅 Olympic Games Analytics")
with header_right:
    st.markdown('<p class="right-label">Paris 2024</p>', unsafe_allow_html=True)

st.markdown("### 🏠 Overview Dashboard")

st.markdown("""
    <div style="color: #64748b; font-size: 1.0rem; font-weight: 400; margin-bottom: 2rem;">
        A high-level summary of the Olympic Games .
    </div>
    """, unsafe_allow_html=True)

# KPI row
kpi_cols = st.columns(5)

with kpi_cols[0]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="metric-icon">🏃‍♀️</span> Total Athletes
            </div>
            <p class="metric-value">{total_athletes:,}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[1]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="metric-icon">🌍</span> Total Countries
            </div>
            <p class="metric-value">{total_countries:,}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[2]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="metric-icon">🎯</span> Total Sports
            </div>
            <p class="metric-value">{total_sports:,}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[3]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="metric-icon">🥇</span> Total Medals
            </div>
            <p class="metric-value">{int(total_medals):,}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[4]:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                <span class="metric-icon">🏟️</span> Total Events
            </div>
            <p class="metric-value">{total_events:,}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Second row: donut + bar
left_col, right_col = st.columns(2)

with left_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                🥇 Global Medal Distribution
            </div>
            <div class="section-subtitle">
                Gold / Silver / Bronze split
            </div>
        """,
        unsafe_allow_html=True,
    )

    medal_data = []
    if gold_col and "Gold" in selected_medal_types:
        medal_data.append(("Gold", gold_total))
    if silver_col and "Silver" in selected_medal_types:
        medal_data.append(("Silver", silver_total))
    if bronze_col and "Bronze" in selected_medal_types:
        medal_data.append(("Bronze", bronze_total))

    if medal_data:
        medal_df = pd.DataFrame(medal_data, columns=["Medal", "Count"])
        # Set specific colors for medals
        color_map = {'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
        
        fig_pie = px.pie(
            medal_df,
            names="Medal",
            values="Count",
            hole=0.4,
            color="Medal",
            color_discrete_map=color_map # Use the custom color map
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Select at least one medal type in the sidebar to see this chart.")

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">
                🏆 Top 10 Medal Standings
            </div>
            <div class="section-subtitle">
                Countries ranked by total medals
            </div>
        """,
        unsafe_allow_html=True,
    )

    if not filtered_medals.empty and country_col in filtered_medals.columns:
        top10 = filtered_medals.copy()

        if "total" not in top10.columns:
            top10["total"] = 0
            if gold_col:
                top10["total"] += top10[gold_col]
            if silver_col:
                top10["total"] += top10[silver_col]
            if bronze_col:
                top10["total"] += top10[bronze_col]
        
        top10 = top10.dropna(subset=['total'])

        top10 = (
            top10.groupby(country_col, as_index=False)["total"].sum()
            .sort_values("total", ascending=False)
            .head(10)
        )

        if "country" in filtered_medals.columns:
            label_series = (
                filtered_medals
                .drop_duplicates(subset=[country_col])
                .set_index(country_col)["country"]
            )
            top10["Country"] = top10[country_col].map(label_series).fillna(top10[country_col])
        else:
            top10["Country"] = top10[country_col]
        maroon_scale = ["#693001", '#F7E7E7']
        fig_bar = px.bar(
            top10.sort_values("total"),
            x="total",
            y="Country",
            orientation="h",
            color="total", 
            color_continuous_scale=maroon_scale,
        )
        fig_bar.update_layout(
            margin=dict(l=0, r=10, t=0, b=0),
            xaxis_title="Total Medals",
            yaxis_title="",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No medal data available for the current filters.")

    st.markdown("</div>", unsafe_allow_html=True)