import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os
import random 

# --- Configuration ---
st.set_page_config(
    page_title="Page 4: Sports and Events",
    page_icon="🏟️",
    layout="wide",
)

# Define a consistent color scheme for medals (if needed)
MEDAL_COLOR_MAP = {
    "Gold": "#FFD700",   
    "Silver": "#C0C0C0", 
    "Bronze": "#CD7F32", 
}

# --- Data Helpers (Updated and simplified based on debug output) ---
DATA_DIR = Path("data")

# FIX 1: Normalize Medal Column Names based on the debug output
def normalize_medal_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames medal columns from 'Gold Medal' etc. to 'Gold', 'Silver', 'Bronze', and 'total'."""
    
    col_mapping = {}
    
    # Map the exact column names found in your debug image ('Gold Medal', 'Total')
    if 'Gold Medal' in df.columns:
        col_mapping['Gold Medal'] = 'Gold'
    if 'Silver Medal' in df.columns:
        col_mapping['Silver Medal'] = 'Silver'
    if 'Bronze Medal' in df.columns:
        col_mapping['Bronze Medal'] = 'Bronze'
    
    # Your Total column is named 'Total', we rename it to 'total' (lowercase)
    if 'Total' in df.columns:
        col_mapping['Total'] = 'total'
    
    if col_mapping:
        df = df.rename(columns=col_mapping)
    
    # Ensure 'total' exists by calculating it if the individual medals exist
    if 'total' not in df.columns:
        medal_cols_present = [c for c in ['Gold', 'Silver', 'Bronze'] if c in df.columns]
        if medal_cols_present:
            df['total'] = df[medal_cols_present].sum(axis=1)
            
    return df

def get_sport_column(df: pd.DataFrame) -> str | None:
    for cand in ["sport", "discipline", "Sport", "Discipline"]:
        if cand in df.columns:
            return cand
    return None

def get_medal_type_column(df: pd.DataFrame) -> str | None:
    for cand in ["medal", "Medal", "Medal Type", "medal_type", "Medal_Type_treemap"]: # Added Medal_Type_treemap
        if cand in df.columns:
            return cand
    return None


@st.cache_data
def load_data():
    """Loads and preprocesses necessary dataframes."""
    
    try:
        # Load country-aggregated medals for general use (e.g., world map on page 3)
        medals_total = pd.read_csv(DATA_DIR / "medals_total.csv")
        events = pd.read_csv(DATA_DIR / "events.csv")
    except FileNotFoundError as e:
        st.error(f"Required data file not found: {e.filename}. Please ensure 'medals_total.csv' and 'events.csv' are in the 'data' folder.")
        # Removed st.stop() for the purpose of runnable VM code, replace with st.stop() in your app
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame() 
        
    # **CRITICAL FIX 1:** Normalize Medal Column Names in the main file
    medals_total = normalize_medal_columns(medals_total)
    
    # --- Prepare Granular Medals Data for Treemap ---
    sport_medals_df = None
    
    # OPTION A: Try to load the more granular 'medals.csv'
    if (DATA_DIR / "medals.csv").exists():
        try:
            sport_medals_df = pd.read_csv(DATA_DIR / "medals.csv")
            # Rename sport column (e.g., from 'Discipline' to 'sport')
            sport_col_name = get_sport_column(sport_medals_df)
            if sport_col_name:
                sport_medals_df = sport_medals_df.rename(columns={sport_col_name: 'sport_treemap'})
            
            # Ensure the medal column is standardized
            medal_col_name = get_medal_type_column(sport_medals_df)
            if medal_col_name:
                sport_medals_df = sport_medals_df.rename(columns={medal_col_name: 'Medal_Type_treemap'})
            
        except Exception as e:
            st.error(f"Could not load or process medals.csv: {e}")
            sport_medals_df = None
            
    # OPTION B: If 'medals.csv' failed, try 'medallists.csv'
    if sport_medals_df is None and (DATA_DIR / "medallists.csv").exists():
        try:
            sport_medals_df = pd.read_csv(DATA_DIR / "medallists.csv")
            # Ensure the sport column is standardized for the Treemap logic
            sport_col_name = get_sport_column(sport_medals_df)
            if sport_col_name:
                sport_medals_df = sport_medals_df.rename(columns={sport_col_name: 'sport_treemap'})
            
            # Ensure the medal column is standardized
            medal_col_name = get_medal_type_column(sport_medals_df)
            if medal_col_name:
                sport_medals_df = sport_medals_df.rename(columns={medal_col_name: 'Medal_Type_treemap'})

        except Exception as e:
            st.error(f"Could not load or process medallists.csv: {e}")
            sport_medals_df = None

    # Final Check: If granular data is still missing, use the country total file as a fallback
    # ... (Fallback logic removed for brevity but should exist if the files are unreliable)
    # ... (Assuming synthetic data is only for scheduling and venues, as per your code structure)
         
    # --- Prepare Venue Data (Synthetic for Mapbox task - Unchanged) ---
    venue_df = pd.DataFrame({
        'Venue': ['Stade de France', 'Arena Bercy', 'Paris La Défense Arena', 'Place de la Concorde', 'Versailles'],
        'Sport': ['Athletics', 'Basketball', 'Swimming', 'Skateboarding', 'Equestrian'],
        'Latitude': [48.922, 48.839, 48.894, 48.865, 48.807], 
        'Longitude': [2.360, 2.378, 2.235, 2.322, 2.128], 
        'Capacity': [80000, 15000, 17000, 30000, 15000]
    })
    
    # --- Prepare Event Schedule (Synthetic for Gantt task - Unchanged) ---
    sports_list = events['sport'].unique()[:15] 

    schedule_data = []
    start_date = pd.to_datetime('2024-07-26')
    for sport in sports_list:
        event_name = events[events['sport'] == sport]['event'].iloc[0] if not events[events['sport'] == sport].empty else sport + " Final"
        
        start_day_offset = random.randint(1, 10)
        duration = random.randint(3, 7)
        
        start_time = start_date + pd.Timedelta(days=start_day_offset)
        end_time = start_time + pd.Timedelta(days=duration)
        
        schedule_data.append({
            'Sport': sport,
            'Event': event_name,
            'Start': start_time,
            'Finish': end_time,
            'Venue': random.choice(venue_df['Venue'].tolist())
        })
        
    schedule_df = pd.DataFrame(schedule_data)

    return medals_total, schedule_df, venue_df, sport_medals_df

medals_total_df, schedule_df, venue_df, sport_medals_df = load_data()


# --- CSS & Design (Unchanged) ---
st.markdown(
    """
    <style>
    /* Adjust main content container padding for a cleaner look */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Ensure Streamlit headers are visible in dark mode */
    h2, h3, h4 {
        color: #f0f2f6 !important; 
        margin-top: 1.5rem; 
    }
    
    /* Set minimum height for charts */
    .stPlotlyChart {
        background-color: transparent !important;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
## 🏟️ The Competition Arena: Sports and Events Analysis
# ==============================================================================

st.markdown("## 🏟️ The Competition Arena: Sports and Events Analysis")
st.markdown("Analyze the competitive landscape through event scheduling, medal distribution by sport, and venue locations.")

st.markdown("---")

# ==============================================================================
## 1. Event Schedule: Timeline/Gantt Chart (Unchanged)
# ==============================================================================

st.markdown("### 📅 Event Schedule Timeline")
st.markdown("Visualize the timing and duration of key events across the selected time period.")

col_sport_filter, col_venue_filter = st.columns(2)

with col_sport_filter:
    available_sports = sorted(schedule_df['Sport'].unique())
    selected_sports = st.multiselect(
        "Select Sports for Timeline:",
        options=available_sports,
        default=available_sports[:5],
    )

with col_venue_filter:
    available_venues = sorted(schedule_df['Venue'].unique())
    selected_venues = st.multiselect(
        "Select Venues for Timeline:",
        options=available_venues,
        default=available_venues,
    )

filtered_schedule = schedule_df[
    schedule_df['Sport'].isin(selected_sports) & 
    schedule_df['Venue'].isin(selected_venues)
].sort_values(by='Start')


if not filtered_schedule.empty:
    fig_schedule = px.timeline(
        filtered_schedule,
        x_start="Start", 
        x_end="Finish", 
        y="Event", 
        color="Sport",
        title="Olympic Event Schedule by Sport and Venue",
        hover_data=["Venue", "Sport"],
        template="plotly_dark"
    )

    fig_schedule.update_layout(
        xaxis_title="Date and Time",
        yaxis_title="Event",
        height=600,
        margin=dict(l=50, r=50, t=50, b=50),
    )
    
    fig_schedule.update_yaxes(categoryorder='array', categoryarray=filtered_schedule['Event'])
    
    st.plotly_chart(fig_schedule, use_container_width=True)
else:
    st.info("No events match the current sport and venue filters.")

st.markdown("---")


# ==============================================================================
## 2. Medal Count by Sport: Treemap (FIXED TO USE CORRECT MEDAL VALUES)
# ==============================================================================

st.markdown("### 🥇 Medal Count Distribution by Sport")
st.markdown("Use the Treemap to visualize the total medals awarded in each sport, allowing for drill-down into specific medal types.")

# Define the actual medal values present in the data, based on the debug output
MEDAL_TYPES_IN_DATA = ['Gold Medal', 'Silver Medal', 'Bronze Medal']

# --- Data Prep for Treemap ---
if sport_medals_df is not None and 'sport_treemap' in sport_medals_df.columns:
    
    # Check if we have the necessary columns for the full Sport/Medal Treemap
    if 'Medal_Type_treemap' in sport_medals_df.columns:
        
        # 1. Count medals by Sport and Medal Type (granular data logic)
        sport_counts = sport_medals_df.groupby(['sport_treemap', 'Medal_Type_treemap'], as_index=False).size().rename(columns={'size': 'Count'})
        
        # FIX: Filter for the actual medal types found in the data
        sport_counts = sport_counts[sport_counts['Medal_Type_treemap'].isin(MEDAL_TYPES_IN_DATA)]

        if not sport_counts.empty and sport_counts['sport_treemap'].nunique() > 1:
            
            # Create a Plotly color map using the data's medal names mapped to the standard colors
            plotly_color_map = {
                'Gold Medal': MEDAL_COLOR_MAP['Gold'],
                'Silver Medal': MEDAL_COLOR_MAP['Silver'],
                'Bronze Medal': MEDAL_COLOR_MAP['Bronze'],
                '(?)': '#27303e', # Default or other values
            }
            
            # --- Generate Treemap with Sport -> MedalType hierarchy ---
            fig_treemap = px.treemap(
                sport_counts,
                path=[px.Constant("All Sports"), 'sport_treemap', 'Medal_Type_treemap'], 
                values='Count',
                color='Medal_Type_treemap', # Color by medal type (using the data's names)
                color_discrete_map=plotly_color_map,
                title="Total Medal Count by Sport (Drill-down by Medal Type)",
                template="plotly_dark"
            )
            
            fig_treemap.update_layout(
                height=650,
                margin=dict(t=50, l=0, r=0, b=0)
            )
            
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            # Fallback for insufficient variety, but the logic should now work if data exists
            st.warning("Medal data by sport is available but lacks sufficient variety (less than 2 unique sports) or valid medal types to generate the detailed Treemap. Falling back to simplified view.")
            # Execute simplified Treemap logic as fallback:
            # Simple count of all rows grouped by sport (Total Medals per Sport)
            treemap_df = (
                sport_medals_df.groupby('sport_treemap', as_index=False)
                .size()
                .rename(columns={"size": "MedalCount"})
            )

            fig_treemap = px.treemap(
                treemap_df,
                path=[px.Constant("All Sports"), 'sport_treemap'],
                values="MedalCount",
                color="MedalCount",
                color_continuous_scale="Viridis",
                title="Total Medal Count by Sport (Simplified View)",
                template="plotly_dark"
            )
            fig_treemap.update_layout(
                height=650,
                margin=dict(t=50, l=0, r=0, b=0),
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
            
    # Fallback: If Medal Type column itself is missing (not applicable in this case, but kept for robustness)
    else:
        # Simple count of all rows grouped by sport (Total Medals per Sport)
        treemap_df = (
            sport_medals_df.groupby('sport_treemap', as_index=False)
            .size()
            .rename(columns={"size": "MedalCount"})
        )

        fig_treemap = px.treemap(
            treemap_df,
            path=[px.Constant("All Sports"), 'sport_treemap'],
            values="MedalCount",
            color="MedalCount",
            color_continuous_scale="Viridis",
            title="Total Medal Count by Sport (Simplified View)",
            template="plotly_dark"
        )
        fig_treemap.update_layout(
            height=650,
            margin=dict(t=50, l=0, r=0, b=0),
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
        st.info("Using simplified Treemap (total medals per sport) because the granular file did not contain a recognizable 'Medal Type' column.")
    
else:
    st.error("No suitable granular medals data file (`medallists.csv` or similar) was found and processed to generate the Sport Treemap.")

st.markdown("---")


# ==============================================================================
## 3. Venue Map: Scatter Mapbox (Unchanged)
# ==============================================================================

st.markdown("### 🗺️ Olympic Venue Map")
st.markdown("A dynamic map showing the geographical location of all competition venues.")

if not venue_df.empty:
    
    fig_map = px.scatter_mapbox(
        venue_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Venue",
        hover_data=["Sport", "Capacity"],
        color="Sport",
        size="Capacity", 
        zoom=9,          
        height=600,
        mapbox_style="carto-darkmatter", 
        title="Competition Venues (Approximate Locations)",
        template="plotly_dark"
    )

    fig_map.update_layout(
        mapbox=dict(
            center=dict(lat=48.86, lon=2.35), 
            zoom=9.5 
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
    )

    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Venue location data is not available.")
    
st.markdown("---")