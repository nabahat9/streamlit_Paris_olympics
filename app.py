import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import base64

def local_image_to_data_url(path: str) -> str:
    """Return a data:image/...;base64 URL for a local image file."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        return "" # Return empty string if file not found
        
    mime = "image/png"
    if path.lower().endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# ---------------------------
# Small helper
# ---------------------------
def get_medal_column(df: pd.DataFrame, medal_name: str):
    """
    Try to find the column corresponding to a medal type (gold/silver/bronze)
    using a case-insensitive substring search.
    Returns the column name or None.
    """
    medal_name = medal_name.lower()
    for col in df.columns:
        cl = col.lower()
        if cl == medal_name or medal_name in cl:
            return col
    return None


# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="Olympic Games Analytics – Overview",
    page_icon="🏅",
    layout="wide",
)

# ---------------------------
# Initialize Session State for Navigation
# ---------------------------
if 'active_page' not in st.session_state:
    st.session_state.active_page = 'overview'

# Hide Streamlit default menu/footer/header (includes space removal)
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# ---------------------------
# Custom CSS for layout (Includes fixes for top space and full-width hero)
# ---------------------------
st.markdown(
    """
    <style>
    /* --------------------------------- */
    /* GLOBAL SPACE REMOVAL (HEADER FIX) */
    /* --------------------------------- */
    .block-container {
        padding-top: 0 !important; /* Eliminate default top padding */
        padding-bottom: 1rem;
        max-width: 1300px;
    }
    
    /* Target the main content wrapper (stVerticalBlock) and pull it up to fill the space 
       left by the hidden Streamlit header. */
    div[data-testid="stVerticalBlock"] {
        margin-top: -3rem !important;
    }
    
    /* --------------------------------- */
    /* FULL WIDTH HERO SECTION (MODIFIED) */
    /* --------------------------------- */
    .full-width-hero { /* NEW CLASS NAME for the wrapper */
        margin-top: 0.3rem;
        margin-bottom: 1.2rem;
    }
    
    /* This forces the content element to ignore the parent container's padding/max-width */
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
    }
    .hero-overlay { /* Keep the overlay and other child styles as they are */
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, rgba(15,23,42,0.9) 0%, rgba(15,23,42,0.4) 40%, rgba(15,23,42,0.05) 100%);
        color: #f9fafb;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 24px 34px;
    }
    
    /* ---------- REST OF STYLES (Kept Original) ---------- */
    .metric-card {
        background-color: #ffffff;
        padding: 18px 20px;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(15,23,42,0.06);
        border: 1px solid rgba(226,232,240,0.8);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0;
    }
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        color: #16a34a;
        margin-top: 4px;
    }
    .metric-icon {
        font-size: 1.3rem;
        margin-right: 6px;
    }
    .section-card {
        background-color: #ffffff;
        padding: 22px 24px;
        border-radius: 18px;
        box-shadow: 0 2px 10px rgba(15,23,42,0.06);
        border: 1px solid rgba(226,232,240,0.9);
        margin-top: 0.75rem;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .section-subtitle {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 1rem;
    }
    .right-label {
        text-align: right;
        font-size: 0.9rem;
        color: #64748b;
    }
    
    /* Navigation button styling */
    div.stButton > button {
        background-color: rgba(37, 99, 235, 0.1);
        color: #2563eb;
        border: 2px solid #2563eb;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #2563eb;
        color: white;
        border-color: #2563eb;
    }
    
    .hero-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
    }
    .hero-logo {
        display: flex;
        flex-direction: column;
        gap: 2px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-size: 0.7rem;
    }
    .hero-logo-mark {
        font-size: 1.4rem;
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Data loading
# ---------------------------
DATA_DIR = Path("data")

@st.cache_data
def load_data():
    # Placeholder for data loading, assuming these files exist in a 'data' directory
    # If the files don't exist, this will throw an error when running
    try:
        athletes = pd.read_csv(DATA_DIR / "athletes.csv")
        events = pd.read_csv(DATA_DIR / "events.csv")
        medals_total = pd.read_csv(DATA_DIR / "medals_total.csv")
        nocs = pd.read_csv(DATA_DIR / "nocs.csv")
    except FileNotFoundError as e:
        st.error(f"Error loading data: {e}. Please ensure 'data' directory and files are present.")
        # Create empty DataFrames to avoid downstream errors
        athletes = pd.DataFrame(columns=['id', 'sport'])
        events = pd.DataFrame(columns=['sport', 'event_id'])
        medals_total = pd.DataFrame(columns=['noc', 'gold', 'silver', 'bronze', 'total'])
        nocs = pd.DataFrame(columns=['noc', 'country'])
        return athletes, events, medals_total, nocs

    # normalize NOC to "noc" in both dfs
    cols_lower_med = {c.lower(): c for c in medals_total.columns}
    if "noc" in cols_lower_med:
        medals_total = medals_total.rename(columns={cols_lower_med["noc"]: "noc"})
    elif "country_code" in cols_lower_med:
        medals_total = medals_total.rename(columns={cols_lower_med["country_code"]: "noc"})

    cols_lower_nocs = {c.lower(): c for c in nocs.columns}
    if "noc" in cols_lower_nocs:
        nocs = nocs.rename(columns={cols_lower_nocs["noc"]: "noc"})
    elif "code" in cols_lower_nocs:
        nocs = nocs.rename(columns={cols_lower_nocs["code"]: "noc"})

    # make sure we have a "total" column
    medal_cols = [c for c in medals_total.columns if c.lower() in ["gold", "silver", "bronze"]]
    if "total" not in medals_total.columns and medal_cols:
        medals_total["total"] = medals_total[medal_cols].sum(axis=1)

    # join country name if possible
    if "noc" in medals_total.columns and "noc" in nocs.columns:
        country_col = None
        for cand in ["country", "country_name", "country_long"]:
            if cand in nocs.columns:
                country_col = cand
                break
        if country_col:
            medals_total = medals_total.merge(
                nocs[["noc", country_col]],
                on="noc",
                how="left",
            )
            medals_total = medals_total.rename(columns={country_col: "country"})

    return athletes, events, medals_total, nocs

athletes_df, events_df, medals_total_df, nocs_df = load_data()

# ------------------------------------------------
# HERO SECTION (Class changed to full-width-hero)
# ------------------------------------------------
BASE_DIR = Path(__file__).parent
HERO_IMAGE_PATH = BASE_DIR / "utils" / "picture_oly.png"

# Check if image exists
if HERO_IMAGE_PATH.exists():
    HERO_IMAGE_URL = local_image_to_data_url(str(HERO_IMAGE_PATH))
else:
    HERO_IMAGE_URL = ""
    st.warning(f"Warning: Hero image not found at {HERO_IMAGE_PATH}. Using solid background color.")

st.markdown(
    f"""
    <div class="full-width-hero"> 
      <div class="hero" style="background-image: url('{HERO_IMAGE_URL}'); background-color: #1e3a8a;">
        <div class="hero-overlay">
          <div class="hero-top-row">
            <div class="hero-logo">
              <span class="hero-logo-mark">🏅</span>
              <span>PARIS 2024</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Navigation Buttons
# ---------------------------
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1, 1, 1, 1, 2])

with nav_col1:
    if st.button("📊 Overview", key="nav_overview", use_container_width=True):
        st.session_state.active_page = 'overview'

with nav_col2:
    if st.button("🌍 Global Analysis", key="nav_global", use_container_width=True):
        st.session_state.active_page = 'global'

with nav_col3:
    if st.button("🏃 Athletes", key="nav_athletes", use_container_width=True):
        st.session_state.active_page = 'athletes'

with nav_col4:
    if st.button("🎯 Sports & Events", key="nav_sports", use_container_width=True):
        st.session_state.active_page = 'sports'

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------
# Sidebar filters
# ---------------------------
st.sidebar.header("🌍 Global Filters")

country_col = "noc"
available_nocs = sorted(medals_total_df[country_col].dropna().unique().tolist())
selected_nocs = st.sidebar.multiselect(
    "Countries (NOC)",
    options=available_nocs,
    default=available_nocs,
)

sport_col = "sport" if "sport" in events_df.columns else events_df.columns[1]
available_sports = sorted(events_df[sport_col].dropna().unique().tolist())
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
# Apply filters
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

# ---------------------------
# Derived metrics
# ---------------------------
total_athletes = (
    filtered_athletes["id"].nunique()
    if "id" in filtered_athletes.columns
    else len(filtered_athletes)
)
total_countries = filtered_medals[country_col].nunique() if country_col in filtered_medals.columns else 0
total_sports = filtered_events[sport_col].nunique() if sport_col in filtered_events.columns else 0

gold_col   = get_medal_column(filtered_medals, "gold")
silver_col = get_medal_column(filtered_medals, "silver")
bronze_col = get_medal_column(filtered_medals, "bronze")

gold_total = filtered_medals[gold_col].sum()   if gold_col   and "Gold"   in selected_medal_types else 0
silver_total = filtered_medals[silver_col].sum() if silver_col and "Silver" in selected_medal_types else 0
bronze_total = filtered_medals[bronze_col].sum() if bronze_col and "Bronze" in selected_medal_types else 0

total_medals = gold_total + silver_total + bronze_total

if "event_id" in filtered_events.columns:
    total_events = filtered_events["event_id"].nunique()
else:
    total_events = len(filtered_events)

delta_athletes = "+2.5%"
delta_countries = "+1.2%"
delta_sports = "0%"
delta_medals = "+0.8%"
delta_events = "+3.1%"

# ---------------------------
# Display content based on active page
# ---------------------------
active_page = st.session_state.active_page

if active_page == 'overview':
    # Header
    header_left, header_right = st.columns([0.8, 0.2])
    with header_left:
        st.markdown("## 🏅 Olympic Games Analytics")
    with header_right:
        st.markdown('<p class="right-label">Paris 2024</p>', unsafe_allow_html=True)

    st.markdown("### 🏠 Overview Dashboard")
    st.markdown("A high-level summary of the Olympic Games filtered by your selections.")

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
                <p class="metric-delta">{delta_athletes}</p>
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
                <p class="metric-delta">{delta_countries}</p>
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
                <p class="metric-delta">{delta_sports}</p>
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
                <p class="metric-delta">{delta_medals}</p>
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
                <p class="metric-delta">{delta_events}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
            fig_pie = px.pie(
                medal_df,
                names="Medal",
                values="Count",
                hole=0.4,
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
            
            # Filter out rows where 'total' might be NaN after summation if the medal columns didn't exist
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

            fig_bar = px.bar(
                top10.sort_values("total"),
                x="total",
                y="Country",
                orientation="h",
                color="total", # Add color mapping for visual appeal
                color_continuous_scale=px.colors.sequential.Agsunset,
            )
            fig_bar.update_layout(
                margin=dict(l=0, r=10, t=0, b=0),
                xaxis_title="Total Medals",
                yaxis_title="",
                coloraxis_showscale=False # Hide color scale legend
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No medal data available for the current filters.")

        st.markdown("</div>", unsafe_allow_html=True)

elif active_page == 'global':
    st.title("🌍 Global Analysis")
    st.info("This page will show global analytics and comparisons.")
    
elif active_page == 'athletes':
    st.title("🏃 Athletes")
    st.info("This page will display athlete profiles and statistics.")
    
elif active_page == 'sports':
    st.title("🎯 Sports & Events")
    st.info("This page will show sports categories and event details.")