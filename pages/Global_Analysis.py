# pages/global_analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import random # Imported for completeness, though not strictly used in this specific page logic

# ======================================================================
# 🚀 NAVBAR INTEGRATION (CRITICAL CHANGES HERE) 
# Assumes utils.py is in the parent directory (root)
try:
    from utils import apply_custom_css, render_navbar 
except ImportError as e:
    # Fallback if the utility file isn't found
    st.error(f"Import Error: Could not import utility functions (apply_custom_css, render_navbar) from the root directory. Error: {e}")
    # Define dummy functions to prevent immediate crash if import fails
    def apply_custom_css(): pass
    def render_navbar(current_page): pass
# ======================================================================

# ------------------------------------------------
# Define a consistent color scheme for medals
# ------------------------------------------------
MEDAL_COLOR_MAP = {
    "Gold": "#FFD700",   # Olympic Gold
    "Silver": "#C0C0C0", # Silver
    "Bronze": "#CD7F32", # Bronze
}
MEDAL_COLOR_LIST = [MEDAL_COLOR_MAP[m] for m in ["Gold", "Silver", "Bronze"]]

# ------------------------------------------------
# Small helpers
# ------------------------------------------------
def get_country_column(df: pd.DataFrame) -> str | None:
    for cand in ["country", "country_long", "country_name", "country_x", "country_y"]:
        if cand in df.columns:
            return cand
    return None

def get_medal_column(df: pd.DataFrame, medal_name: str):
    medal_name = medal_name.lower()
    for col in df.columns:
        cl = col.lower()
        # Handle columns like 'Gold Medal' matching 'gold'
        if cl == medal_name or medal_name in cl:
            return col
    return None

def get_total_column(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        cl = col.lower()
        if cl == "total" or "total" in cl:
            return col
    return None

def normalize_noc_column(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {c.lower(): c for c in df.columns}
    if "noc" in mapping:
        return df.rename(columns={mapping["noc"]: "noc"})
    if "country_code" in mapping:
        return df.rename(columns={mapping["country_code"]: "noc"})
    if "code" in mapping:
        return df.rename(columns={mapping["code"]: "noc"})
    return df

def add_continent_column(medals_total: pd.DataFrame, nocs: pd.DataFrame) -> pd.DataFrame:
    medals = medals_total.copy()
    # try continent/region from nocs
    for cand in ["continent", "region"]:
        if cand in nocs.columns:
            merged = medals.merge(
                nocs[["noc", cand]],
                on="noc",
                how="left",
            )
            merged = merged.rename(columns={cand: "continent"})
            merged["continent"] = merged["continent"].fillna("Other")
            return merged

    # try countries.csv
    data_dir = Path("data")
    countries_path = data_dir / "countries.csv"
    if countries_path.exists():
        try:
            countries = pd.read_csv(countries_path)
            countries = normalize_noc_column(countries)
            if "noc" in countries.columns:
                continent_col = None
                for c in ["continent", "region"]:
                    if c in countries.columns:
                        continent_col = c
                        break
                if continent_col:
                    merged = medals.merge(
                        countries[["noc", continent_col]],
                        on="noc",
                        how="left",
                    )
                    merged = merged.rename(columns={continent_col: "continent"})
                    merged["continent"] = merged["continent"].fillna("Other")
                    return merged
        except Exception as e:
            st.warning(f"Could not load or process countries.csv for continent mapping: {e}")

    # fallback
    medals["continent"] = "Other"
    return medals

# ------------------------------------------------
# Page config
# ------------------------------------------------
st.set_page_config(
    page_title="Olympic Games Analytics – Global Analysis",
    page_icon="🗺️",
    layout="wide",
)

# ======================================================================
# 🚀 APPLY NAVBAR AND CSS
apply_custom_css()
# Pass the unique identifier for this page to mark it active in the navbar
# Assuming the file is named global_analysis.py in the pages/ folder
render_navbar(current_page="Global_Analysis") 
# ======================================================================


# ------------------------------------------------
# Global CSS (Retaining your provided styling)
# ------------------------------------------------
st.markdown(
    """
    <style>
    /* Add top margin to prevent content from being hidden by fixed navbar */
    .stApp > header {
        margin-top: 4rem; 
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Treat inner vertical blocks as cards */
    section.main div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background-color: #1e293b;  /* dark card */
        padding: 22px 24px;
        border-radius: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #475569;
        margin-top: 0.75rem;
    }

    /* Titles inside those blocks (st.subheader -> h3) */
    section.main div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] h3 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.2rem !important;
        margin-top: 0rem !important;
        color: #f0f2f6 !important;
    }

    /* Section headings above cards */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #f0f2f6;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-subtitle {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }

    /* General headers & tabs */
    h2, h4, .stTabs [data-baseweb="tab-list"] button {
        color: #f0f2f6 !important;
    }

    .stTabs [data-baseweb="tab-list"] button {
        background-color: #334155;
        border-radius: 8px 8px 0 0;
        font-size: 1.0rem;
        font-weight: 600;
        padding: 10px 15px;
        border: 1px solid #475569;
        margin-right: 5px;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #27303e;
        border-bottom: 2px solid #0d47a1;
        color: #f0f2f6 !important;
        border-color: #0d47a1;
    }

    /* Plotly charts */
    .stPlotlyChart {
        background-color: transparent !important;
        min-height: 550px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------
# Data loading
# ------------------------------------------------
DATA_DIR = Path("data")

# Fallback functions for placeholder data if files are missing
def create_placeholder_data():
    import numpy as np
    st.warning("Using synthetic placeholder data as files are missing.")
    athletes = pd.DataFrame({'id': range(100), 'name': [f'Athlete {i}' for i in range(100)], 'noc': np.random.choice(['USA', 'CHN', 'JPN', 'GER', 'FRA', 'AUS'], 100)})
    events = pd.DataFrame({'sport': ['Swimming', 'Athletics', 'Gymnastics', 'Cycling'], 'event': [f'E{i}' for i in range(4)]})
    medals_total = pd.DataFrame({
        'NOC': ['USA', 'CHN', 'JPN', 'GER', 'FRA', 'AUS'], 
        'Gold': [40, 30, 20, 10, 8, 5], 
        'Silver': [30, 25, 15, 8, 7, 5], 
        'Bronze': [20, 20, 10, 5, 5, 4],
        'Total': [90, 75, 45, 23, 20, 14],
        'Country_Name': ['United States', 'China', 'Japan', 'Germany', 'France', 'Australia']
    })
    nocs = pd.DataFrame({'NOC': ['USA', 'CHN', 'JPN', 'GER', 'FRA', 'AUS'], 'Continent': ['North America', 'Asia', 'Asia', 'Europe', 'Europe', 'Oceania']})
    medalists = pd.DataFrame({
        'NOC': np.random.choice(['USA', 'CHN', 'JPN', 'GER', 'FRA', 'AUS'], 300),
        'Medal': np.random.choice(['Gold', 'Silver', 'Bronze'], 300),
        'Sport': np.random.choice(['Swimming', 'Athletics', 'Gymnastics', 'Cycling', 'Rowing', 'Fencing'], 300)
    })
    
    # Normalize for helper functions
    medals_total.rename(columns={'NOC': 'noc'}, inplace=True)
    nocs.rename(columns={'NOC': 'noc', 'Continent': 'continent'}, inplace=True)
    medalists.rename(columns={'NOC': 'noc', 'Medal': 'medal'}, inplace=True)

    return athletes, events, medals_total, nocs, medalists

@st.cache_data
def load_data():
    try:
        athletes = pd.read_csv(DATA_DIR / "athletes.csv")
        events = pd.read_csv(DATA_DIR / "events.csv")
        medals_total = pd.read_csv(DATA_DIR / "medals_total.csv")
        nocs = pd.read_csv(DATA_DIR / "nocs.csv")
        
        medals_total = normalize_noc_column(medals_total)
        nocs = normalize_noc_column(nocs)

        # Ensure 'Total' column exists
        medal_cols = [get_medal_column(medals_total, m) for m in ["gold", "silver", "bronze"] if get_medal_column(medals_total, m) is not None]
        if get_total_column(medals_total) is None and medal_cols:
            medals_total["total"] = medals_total[medal_cols].sum(axis=1)

        # Merge country name for choropleth hover data
        if "noc" in medals_total.columns and "noc" in nocs.columns:
            country_col = None
            for cand in ["country", "country_name", "country_long"]:
                if cand in nocs.columns:
                    country_col = cand
                    break
            if country_col:
                medals_total = medals_total.merge(
                    nocs[["noc", country_col]].drop_duplicates("noc"),
                    on="noc",
                    how="left",
                )
                medals_total = medals_total.rename(columns={country_col: "country"})

        medalists = None
        medalists_path = DATA_DIR / "medallists.csv"
        if medalists_path.exists():
            medalists = pd.read_csv(medalists_path)
            medalists = normalize_noc_column(medalists)
            
        medals_total = add_continent_column(medals_total, nocs)

        return athletes, events, medals_total, nocs, medalists
    
    except FileNotFoundError:
        return create_placeholder_data()

athletes_df, events_df, medals_total_df, nocs_df, medalists_df = load_data()

# ------------------------------------------------
# Sidebar – global filters
# ------------------------------------------------
st.sidebar.header("🌍 Global Filters")

country_col = "noc"
available_nocs = sorted(medals_total_df[country_col].dropna().unique().tolist())
selected_nocs = st.sidebar.multiselect(
    "Countries (NOC)",
    options=available_nocs,
    default=available_nocs,
)

sport_col_events = "sport" if "sport" in events_df.columns else events_df.columns[0] if not events_df.empty else "Sport"
available_sports = sorted(events_df[sport_col_events].dropna().unique().tolist())
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

# ------------------------------------------------
# Apply filters
# ------------------------------------------------
filtered_medals_total = medals_total_df[
    medals_total_df[country_col].isin(selected_nocs)
] if selected_nocs and not medals_total_df.empty else medals_total_df.copy()

filtered_medalists = None
if medalists_df is not None:
    filtered_medalists = medalists_df.copy()
    if selected_nocs and "noc" in filtered_medalists.columns:
        filtered_medalists = filtered_medalists[filtered_medalists["noc"].isin(selected_nocs)]
    
    sport_col_candidates = [c for c in filtered_medalists.columns if c.lower() in ["sport", "discipline", "event"]]
    if selected_sports and sport_col_candidates:
        sport_col_med = sport_col_candidates[0]
        filtered_medalists = filtered_medalists[
            filtered_medalists[sport_col_med].isin(selected_sports)
        ]
    
    # Filter medalists by selected medal type
    medal_col_med = get_medal_column(filtered_medalists, "medal")
    if medal_col_med:
        # Create a mapping from data column values (e.g., 'Gold Medal') to display names ('Gold')
        medal_value_map = {v.split()[0]: v.split()[0] for v in filtered_medalists[medal_col_med].unique()}
        
        # Determine the actual values in the data that match the user's selection
        valid_medal_values = [v for k, v in medal_value_map.items() if k in selected_medal_types]
        
        # Filter based on these values (often just 'Gold', 'Silver', 'Bronze')
        filtered_medalists = filtered_medalists[
            filtered_medalists[medal_col_med].astype(str).str.contains('|'.join(valid_medal_values), case=False, na=False)
        ]


# ------------------------------------------------
# Derived metrics (for completeness, though not displayed)
# ------------------------------------------------
total_countries = filtered_medals_total[country_col].nunique()
total_col = get_total_column(filtered_medals_total)
total_medals_global = filtered_medals_total[total_col].sum() if total_col else 0

gold_col = get_medal_column(filtered_medals_total, "gold")
silver_col = get_medal_column(filtered_medals_total, "silver")
bronze_col = get_medal_column(filtered_medals_total, "bronze")

gold_sum = filtered_medals_total[gold_col].sum() if gold_col else 0
silver_sum = filtered_medals_total[silver_col].sum() if silver_col else 0
bronze_sum = filtered_medals_total[bronze_col].sum() if bronze_col else 0

total_continents = filtered_medals_total["continent"].nunique()

# ------------------------------------------------
# Header
# ------------------------------------------------
st.markdown("## 🗺️ Global Medal Analysis")
st.markdown(
    "Explore global performance across countries, continents, and sports "
    "using maps, hierarchies, and comparative charts."
)
st.markdown("---")

# ------------------------------------------------
# Section 1: Geospatial + Top Countries
# ------------------------------------------------
st.markdown(
    '<div class="section-title">📊 Medal Distribution & Performance</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="section-subtitle">Visualize how medals are distributed globally and analyze the top performing nations.</p>',
    unsafe_allow_html=True,
)

map_col, bar_col = st.columns((1.1, 0.9))

with map_col:
    with st.container():
        st.subheader("🌐 World Medal Map")

        if not filtered_medals_total.empty and total_col:
            map_df = filtered_medals_total.copy()

            hover_col = "noc"
            for cand in ["country", "country_long", "country_x", "country_y"]:
                if cand in map_df.columns:
                    hover_col = cand
                    break

            fig_world = px.choropleth(
                map_df,
                locations="noc",
                color=total_col,
                hover_name=hover_col,
                color_continuous_scale="Viridis",
                projection="natural earth",
                title="Total Medals by Country" # Added title
            )
            fig_world.update_layout(
                margin=dict(l=0, r=0, t=30, b=0), # Adjusted top margin for plot title
                height=550,
                template="plotly_dark",
            )
            st.plotly_chart(fig_world, use_container_width=True)
        else:
            st.info("No medal data available for the current filters.")

with bar_col:
    with st.container():
        st.subheader("🏆 Top 20 Countries – Medal Breakdown")

        if not filtered_medals_total.empty and gold_col and silver_col and bronze_col:
            top = filtered_medals_total.copy()

            # Zero out unselected medal types before summing total for ranking
            for medal_name, col in zip(
                ["Gold", "Silver", "Bronze"],
                [gold_col, silver_col, bronze_col],
            ):
                if medal_name not in selected_medal_types and col:
                    top[col] = 0

            # Calculate ranking based on filtered medal types
            agg = top.groupby(country_col, as_index=False)[
                [gold_col, silver_col, bronze_col]
            ].sum()
            agg["total"] = agg[[gold_col, silver_col, bronze_col]].sum(axis=1)
            agg = agg.sort_values("total", ascending=False).head(20)

            # Map NOC to full country name for display
            label_col = get_country_column(filtered_medals_total)
            if label_col:
                label_series = (
                    filtered_medals_total
                    .drop_duplicates(subset=[country_col])
                    .set_index(country_col)[label_col]
                )
                agg["Country"] = agg[country_col].map(label_series).fillna(
                    agg[country_col]
                )
            else:
                agg["Country"] = agg[country_col]

            # Prepare for stacked bar chart (melt)
            plot_df = agg.melt(
                id_vars=["Country"],
                value_vars=[gold_col, silver_col, bronze_col],
                var_name="Medal",
                value_name="Count",
            )
            rename_map = {
                gold_col: "Gold",
                silver_col: "Silver",
                bronze_col: "Bronze",
            }
            plot_df["Medal"] = plot_df["Medal"].map(rename_map).fillna(
                plot_df["Medal"]
            )
            
            # Filter to only show selected medal types
            plot_df = plot_df[plot_df["Medal"].isin(selected_medal_types)]
            
            # Remove zero counts if all medal types are selected and we don't want to show empty bars
            plot_df = plot_df[plot_df['Count'] > 0] 

            fig_top = px.bar(
                plot_df,
                x="Count",
                y="Country",
                color="Medal",
                orientation="h",
                barmode="group",
                color_discrete_map=MEDAL_COLOR_MAP,
                category_orders={
                    "Country": agg["Country"].tolist()[::-1], # Order by total medal count
                    "Medal": ["Gold", "Silver", "Bronze"] # Consistent medal order
                },
                title="Top 20 Nations by Total Medals" # Added title
            )
            fig_top.update_layout(
                margin=dict(l=0, r=10, t=30, b=0),
                xaxis_title="Medal Count",
                yaxis_title="",
                height=550,
                template="plotly_dark",
                legend_title_text='Medal Type'
            )
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("Gold/Silver/Bronze columns not found or no data for current filters.")

st.markdown("---")

# ------------------------------------------------
# Section 2: Hierarchy & Continents (Tabs)
# ------------------------------------------------
st.markdown(
    '<div class="section-title">🧬 Hierarchy & Continental View</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="section-subtitle">Drill down into medal totals by continent, country, and sport discipline.</p>',
    unsafe_allow_html=True,
)

with st.container():
    tab1, tab2, tab3 = st.tabs(
        ["🌎 Medals by Continent", "👑 Sunburst Hierarchy", "🧱 Treemap Hierarchy"]
    )

    # --- Tab 1: Continent vs Medals ---
    with tab1:
        st.subheader("Gold, Silver, and Bronze Totals by Continent")

        if not filtered_medals_total.empty and gold_col and silver_col and bronze_col:
            cont_df = filtered_medals_total.copy()

            # Zero out unselected medal types
            for medal_name, col in zip(
                ["Gold", "Silver", "Bronze"],
                [gold_col, silver_col, bronze_col],
            ):
                if medal_name not in selected_medal_types and col:
                    cont_df[col] = 0

            cont_agg = cont_df.groupby("continent", as_index=False)[
                [gold_col, silver_col, bronze_col]
            ].sum()

            cont_melt = cont_agg.melt(
                id_vars=["continent"],
                value_vars=[gold_col, silver_col, bronze_col],
                var_name="Medal",
                value_name="Count",
            )
            rename_map = {
                gold_col: "Gold",
                silver_col: "Silver",
                bronze_col: "Bronze",
            }
            cont_melt["Medal"] = cont_melt["Medal"].map(rename_map).fillna(
                cont_melt["Medal"]
            )
            cont_melt = cont_melt[cont_melt["Medal"].isin(selected_medal_types)]
            cont_melt = cont_melt[cont_melt['Count'] > 0] 

            fig_cont = px.bar(
                cont_melt,
                x="continent",
                y="Count",
                color="Medal",
                barmode="group",
                color_discrete_map=MEDAL_COLOR_MAP,
                category_orders={"Medal": ["Gold", "Silver", "Bronze"]},
                title="Medal Totals by Continent"
            )
            fig_cont.update_layout(
                xaxis_title="Continent",
                yaxis_title="Medals",
                margin=dict(l=0, r=0, t=30, b=0),
                height=550,
                template="plotly_dark",
                legend_title_text='Medal Type'
            )
            st.plotly_chart(fig_cont, use_container_width=True)
        else:
            st.info("Not enough medal data to show continent comparison.")

    # --- Tab 2 & 3: Hierarchy Charts ---
    
    # Common preparation logic for Sunburst and Treemap
    hierarchy_data_ready = False
    
    if filtered_medalists is not None and not filtered_medalists.empty:
        sport_col_candidates = [
            c
            for c in filtered_medalists.columns
            if c.lower() in ["sport", "discipline", "event"]
        ]
        sport_col_med = sport_col_candidates[0] if sport_col_candidates else None

        hierarchy_df = filtered_medalists.copy()
        hierarchy_df = normalize_noc_column(hierarchy_df)
        country_label_col = get_country_column(medals_total_df)

        base_cols = ["noc", "continent"]
        if country_label_col:
            base_cols.append(country_label_col)

        join_df = medals_total_df[base_cols].drop_duplicates("noc")
        hierarchy_df = hierarchy_df.merge(join_df, on="noc", how="left")

        hierarchy_df["continent"] = hierarchy_df["continent"].fillna("Other")
        if country_label_col and country_label_col in hierarchy_df.columns:
            hierarchy_df["country_label"] = hierarchy_df[country_label_col].fillna(hierarchy_df["noc"])
        else:
            hierarchy_df["country_label"] = hierarchy_df["noc"]

        if sport_col_med:
            hierarchy_df["sport_level"] = hierarchy_df[sport_col_med]
        else:
            hierarchy_df["sport_level"] = "All sports" # Fallback if sport column is missing

        # The core grouping for both charts
        hierarchy_counts = (
            hierarchy_df.groupby(["continent", "country_label", "sport_level"], as_index=False)
            .size()
            .rename(columns={"size": "MedalCount"})
        )
        
        # Ensure sufficient hierarchy levels are present for a good visual
        if hierarchy_counts.shape[0] > 10:
            hierarchy_data_ready = True
    
    # --- Tab 2: Sunburst Hierarchy ---
    with tab2:
        st.subheader("Continent → Country → Sport Hierarchy (Sunburst View)")

        if hierarchy_data_ready:
            fig_sun = px.sunburst(
                hierarchy_counts,
                path=["continent", "country_label", "sport_level"],
                values="MedalCount",
                color="MedalCount", # Color based on count
                color_continuous_scale="Plasma",
                title="Medal Distribution by Geographic and Sport Hierarchy"
            )
            fig_sun.update_layout(
                margin=dict(l=0, r=0, t=30, b=0),
                height=550,
                template="plotly_dark",
            )
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info(
                "No 'medallists.csv' found or data is too sparse after filters. "
                "Sunburst requires granular medal data (medallists.csv) for Sport-level breakdown."
            )

    # --- Tab 3: Treemap Hierarchy ---
    with tab3:
        st.subheader("Continent → Country → Sport Hierarchy (Treemap View)")

        if hierarchy_data_ready:
            fig_tree = px.treemap(
                hierarchy_counts,
                path=["continent", "country_label", "sport_level"],
                values="MedalCount",
                color="MedalCount",
                color_continuous_scale="Viridis",
                title="Medal Distribution by Geographic and Sport Hierarchy"
            )
            fig_tree.update_layout(
                margin=dict(l=0, r=0, t=30, b=0),
                height=550,
                template="plotly_dark",
            )
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info(
                "Treemap also requires granular medal data (medallists.csv) for full hierarchy visualization. "
                "Add that file to the data/ folder for full hierarchy."
            )