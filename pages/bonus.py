# pages/la28_dashboard.py

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# Import shared utilities (CRITICAL ADDITION)
# Assuming utils.py is in the parent directory or properly imported if using pages/ structure
# If utils.py is in the same directory as app.py (the entry point), this import works.
# If you are using Streamlit's native multipage, put this file in a 'pages' folder 
# and ensure you have an empty __init__.py in the parent folder if needed for imports.
# I will assume utils.py is available.
from utils import apply_custom_css, render_navbar
# --- 1. Configuration and Constants ---
st.set_page_config(
    layout="wide", 
    page_title="LA28 Olympic Data Dashboard",
    page_icon="🏆"
)

# Apply CSS and Render Navbar (CRITICAL ADDITION)
apply_custom_css()
# Pass the unique identifier for this page to mark it active in the navbar
render_navbar(current_page="la28_dashboard") 

# Constants
MEDAL_COLORS = {
    'Gold Medal': '#FFD700',
    'Silver Medal': '#C0C0C0',
    'Bronze Medal': '#CD7F32',
    'Gold': '#FFD700', 
    'Silver': '#C0C0C0',
    'Bronze': '#CD7F32'
}

# Simplified NOC to Continent Mapping (Required for Challenges 1 & 3)
NOC_TO_CONTINENT = {
    'USA': 'North America', 'CAN': 'North America', 'MEX': 'North America',
    'BRA': 'South America', 'ARG': 'South America', 'COL': 'South America',
    'GBR': 'Europe', 'FRA': 'Europe', 'GER': 'Europe', 'ITA': 'Europe', 'BEL': 'Europe',
    'KOR': 'Asia', 'JPN': 'Asia', 'CHN': 'Asia', 'IND': 'Asia', 'QAT': 'Asia',
    'AUS': 'Oceania', 'NZL': 'Oceania',
    'RSA': 'Africa', 'TUN': 'Africa', 'KEN': 'Africa', 'ETH': 'Africa'
}

# --- 2. Data Loading and Preprocessing ---

@st.cache_data
def load_medallists_data():
    """Loads and cleans the granular medallists data (used for Ch2, Ch4, Ch5)."""
    try:
        # NOTE: Adjust this path if your data directory structure is different
        data_dir = Path(__file__).parent.parent / "data" 
        df = pd.read_csv(data_dir / "medallists.csv")
        df = df.rename(columns={
            'discipline': 'Sport',
            'country_code': 'NOC',
            'medal_type': 'Medal',
            'name': 'Athlete_Name',
            'medal_date': 'Date',
            'gender': 'Gender'
        })
        # Data cleaning and enrichment
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.normalize()
        df = df.dropna(subset=['Date', 'Medal', 'NOC', 'Sport', 'Athlete_Name', 'Gender'])
        df['Continent'] = df['NOC'].map(NOC_TO_CONTINENT).fillna('Other')
        return df
    except FileNotFoundError:
        st.error("Error: medallists.csv not found. Check data folder path.")
        return pd.DataFrame()

@st.cache_data
def load_medals_total_data():
    """Loads the aggregated medals data (used for Ch1, Ch3 map)."""
    try:
        # NOTE: Adjust this path if your data directory structure is different
        data_dir = Path(__file__).parent.parent / "data" 
        df = pd.read_csv(data_dir / "medals_total.csv")
        df = df.rename(columns={'country_code': 'NOC', 'country': 'country'})
        
        if 'Total' not in df.columns:
            # Assuming 'Gold Medal', 'Silver Medal', 'Bronze Medal' exist based on snippet
            medal_cols = [col for col in df.columns if 'Medal' in col]
            if len(medal_cols) == 3:
                df['Total'] = df[medal_cols].sum(axis=1)
            else:
                st.warning("Medal count columns not found in medals_total.csv.")
                return pd.DataFrame()

        df['Continent'] = df['NOC'].map(NOC_TO_CONTINENT).fillna('Other')
        return df
    except FileNotFoundError:
        st.error("Error: medals_total.csv not found. Check data folder path.")
        return pd.DataFrame()

# Load DataFrames
medallists_df = load_medallists_data()
medals_total_df = load_medals_total_data()

# ==============================================================================
# Main Dashboard Layout
# ==============================================================================

# Add padding to avoid content being hidden under the fixed navbar
st.markdown("<div style='margin-top: 4rem;'></div>", unsafe_allow_html=True) 

st.title("LA28 Olympic Data Dashboard 🏅")
st.markdown("Explore medal performance and athlete distributions using advanced interactive visualizations.")

# Check for data availability
if medallists_df.empty or medals_total_df.empty:
    st.error("Please ensure you have uploaded `medallists.csv` and `medals_total.csv` in the correct 'data/' directory.")
    st.stop()

# Use tabs for clean navigation between challenges
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Top Countries (Ch. 1)", 
    "👨‍👩‍👧‍👦 Athlete Sunburst (Ch. 2)", 
    "🌎 Medal Distributions (Ch. 3)", 
    "⚔️ Head-to-Head (Ch. 4)", 
    "🗓️ Who Won the Day? (Ch. 5)"
])

# --- TAB 1: Overall Top Performing Countries by Continent and Gender (Challenge 1) ---

with tab1:
    st.header("🏆 Challenge 1: Top Performing Countries by Continent and Gender")
    st.markdown("Use the sidebar filters to rank countries based on performance metrics.")

    # Sidebar Filters for this tab
    st.sidebar.header("🥇 Ranking Filters (Challenge 1)")

    # The list of available continents is correctly derived from medals_total_df
    available_continents = sorted(medals_total_df['Continent'].unique())
    selected_continent_1 = st.sidebar.selectbox(
        "Select Continent (Ch. 1):",
        options=['All'] + available_continents,
        key='ch1_continent'
    )

    selected_metric_1 = st.sidebar.radio(
        "Select Ranking Metric (Ch. 1):",
        options=['Total', 'Gold Medal', 'Silver Medal', 'Bronze Medal'],
        key='ch1_metric'
    )
    
    # --- Data Preparation (Necessary to include Gender) ---
    medals_gender_df = medallists_df.groupby(['NOC', 'Gender', 'Medal'], as_index=False).size().rename(columns={'size': 'Count'})
    medals_pivot = medals_gender_df.pivot_table(
        index=['NOC', 'Gender'],
        columns='Medal',
        values='Count',
        fill_value=0
    ).reset_index()
    medals_pivot['Total'] = medals_pivot[['Gold Medal', 'Silver Medal', 'Bronze Medal']].sum(axis=1)
    medals_pivot['Continent'] = medals_pivot['NOC'].map(NOC_TO_CONTINENT).fillna('Other')

    selected_gender_1 = st.sidebar.radio(
        "Select Gender Category (Ch. 1):",
        options=['All', 'Male', 'Female'],
        key='ch1_gender'
    )
    
    # Apply Filters and Aggregate
    filtered_df_1 = medals_pivot.copy()

    # 1. Continent Filter
    if selected_continent_1 != 'All':
        filtered_df_1 = filtered_df_1[filtered_df_1['Continent'] == selected_continent_1]

    # 2. Gender Filter/Aggregation
    if selected_gender_1 != 'All':
        filtered_df_1 = filtered_df_1[filtered_df_1['Gender'] == selected_gender_1]
    else:
        # Aggregate male and female performance per country (within the continent if filtered)
        filtered_df_1 = filtered_df_1.groupby('NOC', as_index=False)[[
            'Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total'
        ]].sum()

    # Final Ranking and Plotting
    if filtered_df_1.empty:
        st.warning("No data available for the selected filters.")
    else:
        ranked_df_1 = filtered_df_1.sort_values(by=selected_metric_1, ascending=False).head(15)
        
        # --- Enhanced Plot Title for Clarity ---
        continent_title = selected_continent_1 if selected_continent_1 != 'All' else 'Global'
        gender_title = f"({selected_gender_1} Athletes)" if selected_gender_1 != 'All' else '(All Athletes)'
        plot_title_1 = f"Top 15 Countries in {continent_title} by {selected_metric_1} {gender_title}"
        
        # Prepare data for stacked bar chart (only showing the chosen metric if it's Total)
        if selected_metric_1 == 'Total':
            plot_df_1 = ranked_df_1.melt(
                id_vars='NOC',
                value_vars=['Gold Medal', 'Silver Medal', 'Bronze Medal'],
                var_name='Medal Type',
                value_name='Count'
            )
            fig_bar_1 = px.bar(
                plot_df_1, x='NOC', y='Count', color='Medal Type',
                color_discrete_map=MEDAL_COLORS, title=plot_title_1,
                category_orders={"NOC": ranked_df_1['NOC'].tolist()},
            )
        else:
            # If a single metric (Gold/Silver/Bronze) is selected, use a simpler bar chart
            fig_bar_1 = px.bar(
                ranked_df_1, x='NOC', y=selected_metric_1, color=selected_metric_1,
                color_continuous_scale='YlOrRd', title=plot_title_1,
            )
            
        fig_bar_1.update_layout(xaxis_title="Country (NOC)", yaxis_title=selected_metric_1, height=600, template="plotly_dark")
        st.plotly_chart(fig_bar_1, use_container_width=True)

# --- TAB 2: Athletes by Sport Discipline, Country, and Gender (Challenge 2) ---

with tab2:
    st.header("👨‍👩‍👧‍👦 Challenge 2: Athlete Distribution Sunburst Chart")
    st.markdown("This interactive chart allows drilling down from **Sport** to **Country** to **Gender** to see the unique number of athletes.")

    # 1. Data Preparation
    athlete_counts = medallists_df.groupby(['Sport', 'NOC', 'Gender'], as_index=False).agg(
        Athlete_Count=('Athlete_Name', 'nunique')
    )

    # Optional Sport Filter
    available_sports_2 = sorted(athlete_counts['Sport'].unique())
    selected_sport_2 = st.selectbox(
        "Filter by Sport Discipline (Optional):",
        options=["All Sports"] + available_sports_2,
        index=0,
        key='ch2_sport'
    )

    filtered_counts_2 = athlete_counts.copy()
    if selected_sport_2 != "All Sports":
        filtered_counts_2 = filtered_counts_2[filtered_counts_2['Sport'] == selected_sport_2]

    if filtered_counts_2.empty:
        st.warning("No data available for the selected sport.")
    else:
        # 2. Generate Sunburst Plot
        fig_sunburst = px.sunburst(
            filtered_counts_2,
            path=['Sport', 'NOC', 'Gender'],
            values='Athlete_Count',
            color='Sport', 
            color_continuous_scale=px.colors.sequential.Viridis,
            title=f"Unique Athlete Distribution by Sport, Country, and Gender ({selected_sport_2})",
            height=700
        )

        fig_sunburst.update_layout(margin=dict(t=50, l=0, r=0, b=0), template="plotly_dark")
        st.plotly_chart(fig_sunburst, use_container_width=True)


# --- TAB 3: Advanced Medal Distributions (Challenge 3) ---

with tab3:
    st.header("🌎 Challenge 3: Advanced Medal Distributions")
    st.markdown("Visualize global medal distribution and compare countries within a selected continent.")
    
    col_filter_3, col_breakdown_3 = st.columns([1, 2])
    
    with col_filter_3:
        st.subheader("Map Controls")
        selected_medal_3 = st.selectbox(
            "Select Medal Type for Map:",
            options=['Total', 'Gold Medal', 'Silver Medal', 'Bronze Medal'],
            index=0,
            key='ch3_medal'
        )
        
        st.subheader("Continental Breakdown")
        available_continents_3 = sorted(medals_total_df['Continent'].unique())
        selected_continent_3 = st.selectbox(
            "Select Continent for Bar Chart:",
            options=['None'] + available_continents_3,
            index=0,
            key='ch3_continent_breakdown'
        )

    # 1. Map Data Preparation (using aggregated medals_total_df)
    map_data_3 = medals_total_df.copy()
    color_col_3 = selected_medal_3
    
    if map_data_3.empty:
        st.error("Aggregated medal data is missing.")
    else:
        # Generate Choropleth Map
        fig_map_3 = px.choropleth(
            map_data_3,
            locations='NOC',
            color=color_col_3,
            hover_name='country',
            color_continuous_scale='Plasma',
            projection="natural earth",
            title=f"Global Distribution of {color_col_3} Counts",
            height=600
        )
        fig_map_3.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, template="plotly_dark")
        
    st.plotly_chart(fig_map_3, use_container_width=True)
    
    # 2. Continental Breakdown Bar Chart
    if selected_continent_3 != 'None':
        # Filter granular data to count medals by country within the selected continent
        continent_breakdown_data = medallists_df[medallists_df['Continent'] == selected_continent_3]
        
        bar_data_3 = continent_breakdown_data.groupby(['NOC', 'Medal'], as_index=False).size().rename(columns={'size': 'Count'})
        bar_data_3 = bar_data_3.pivot_table(
            index='NOC',
            columns='Medal',
            values='Count',
            fill_value=0
        ).reset_index()
        bar_data_3['Total'] = bar_data_3[['Gold Medal', 'Silver Medal', 'Bronze Medal']].sum(axis=1)
        bar_data_3 = bar_data_3.sort_values('Total', ascending=False)
        
        fig_bar_3 = px.bar(
            bar_data_3,
            x='NOC',
            y=['Gold Medal', 'Silver Medal', 'Bronze Medal'],
            title=f"Medal Tally in {selected_continent_3} (Top 10)",
            color_discrete_map=MEDAL_COLORS,
        )
        fig_bar_3.update_layout(xaxis_title="Country (NOC)", yaxis_title="Medal Count", height=500, template="plotly_dark")
        st.plotly_chart(fig_bar_3, use_container_width=True)
    else:
        st.info("Select a continent in the controls above to see a detailed medal breakdown.")


# --- TAB 4: "Head-to-Head" Country Comparison Tool (Challenge 4) ---

with tab4:
    st.header("⚔️ Challenge 4: Head-to-Head Country Comparison Tool")
    st.markdown("Select two countries to compare their total medal performance across all sports.")
    
    # Pre-aggregate data by NOC and Sport
    comparison_base_df = medallists_df.groupby(['NOC', 'Sport', 'Medal'], as_index=False).size().rename(columns={'size': 'Count'})
    comparison_pivot = comparison_base_df.pivot_table(
        index=['NOC', 'Sport'],
        columns='Medal',
        values='Count',
        fill_value=0
    ).reset_index()
    comparison_pivot['Total'] = comparison_pivot[['Gold Medal', 'Silver Medal', 'Bronze Medal']].sum(axis=1)

    available_countries_4 = sorted(comparison_pivot['NOC'].unique())

    # 1. Selection Interface
    col_select_1, col_select_2 = st.columns(2)

    with col_select_1:
        country_1 = st.selectbox(
            "Select Country 1 (Left)",
            options=available_countries_4,
            index=available_countries_4.index('USA') if 'USA' in available_countries_4 else 0,
            key='ch4_c1'
        )

    with col_select_2:
        default_index_2 = available_countries_4.index('CHN') if 'CHN' in available_countries_4 else (1 if len(available_countries_4) > 1 else 0)
        country_2 = st.selectbox(
            "Select Country 2 (Right)",
            options=available_countries_4,
            index=default_index_2,
            key='ch4_c2'
        )
        
    # 2. Data Filtering and Merging
    if country_1 and country_2:
        
        data_1 = comparison_pivot[comparison_pivot['NOC'] == country_1]
        data_2 = comparison_pivot[comparison_pivot['NOC'] == country_2]
        
        merged_comp = pd.merge(
            data_1, data_2, on='Sport', how='outer', 
            suffixes=(f'_{country_1}', f'_{country_2}')
        ).fillna(0)
        
        medal_sports = merged_comp[(merged_comp[f'Total_{country_1}'] > 0) | (merged_comp[f'Total_{country_2}'] > 0)]
        
        if not medal_sports.empty:
            medal_sports['Combined_Total'] = medal_sports[f'Total_{country_1}'] + medal_sports[f'Total_{country_2}']
            medal_sports = medal_sports.sort_values('Combined_Total', ascending=False)
            
            # Melt data for Grouped Bar Chart
            melted_data = medal_sports.melt(
                id_vars='Sport',
                value_vars=[f'Total_{country_1}', f'Total_{country_2}'],
                var_name='Country',
                value_name='Total Medals'
            )
            melted_data['Country'] = melted_data['Country'].str.replace('Total_', '')
            
            # 3. Visualization
            fig_comp = px.bar(
                melted_data, x='Sport', y='Total Medals', color='Country', barmode='group',
                title=f"Medal Comparison: {country_1} vs. {country_2} by Sport",
                template="plotly_dark",
                category_orders={"Sport": medal_sports['Sport'].tolist()} # Maintain total ranking order
            )
            fig_comp.update_layout(xaxis_tickangle=-45, height=600)
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # 4. Summary Table
            st.subheader("Total Medal Summary")
            summary_df = pd.DataFrame({
                'Metric': ['Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total'],
                country_1: [data_1[m].sum() for m in ['Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total']],
                country_2: [data_2[m].sum() for m in ['Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total']]
            }).set_index('Metric')
            
            st.dataframe(summary_df)
        else:
            st.info("The selected countries have no overlapping medal-winning sports in this dataset.")


# --- TAB 5: "Who Won the Day?" Feature (Challenge 5) ---

with tab5:
    st.header("🗓️ Challenge 5: Who Won the Day?")
    st.markdown("Select a day to see all medal events and the top performing country for that day.")
    
    if medallists_df.empty:
        st.info("No data available for date analysis.")
        st.stop()
        
    min_date = medallists_df['Date'].min()
    max_date = medallists_df['Date'].max()

    if pd.isna(min_date) or pd.isna(max_date):
        st.error("Date column in medallists.csv is invalid or empty.")
        st.stop()

    # Convert to standard Python date objects for the slider
    min_date_py = min_date.date()
    max_date_py = max_date.date()

    # Use a container to keep the slider clean
    with st.container():
        selected_date_py = st.slider(
            "Select a Day of the Games:",
            min_value=min_date_py,
            max_value=max_date_py,
            value=min_date_py,
            step=pd.Timedelta(days=1),
            format="MMM DD, YYYY",
            key='ch5_date'
        )
    
    selected_date_dt = pd.to_datetime(selected_date_py)

    # 1. Filter Data for Selected Day
    daily_events = medallists_df[medallists_df['Date'] == selected_date_dt]

    if daily_events.empty:
        st.info(f"No medal events recorded on **{selected_date_py.strftime('%B %d, %Y')}**.")
    else:
        st.subheader(f"🥇 Medal Events on {selected_date_py.strftime('%A, %B %d, %Y')}")
        
        # --- Top Performing Country for the Day ---
        daily_summary = daily_events.groupby('NOC')['Medal'].count().sort_values(ascending=False)
        top_country = daily_summary.index[0]
        total_medals = daily_summary.iloc[0]
        
        st.success(f"**🏅 The Top Performer of the Day was {top_country}** with **{total_medals}** total medals!")

        # --- Daily Medal Count Bar Chart ---
        daily_medal_counts = daily_events.groupby(['NOC', 'Medal'], as_index=False).size().rename(columns={'size': 'Count'})

        fig_daily = px.bar(
            daily_medal_counts, x='NOC', y='Count', color='Medal',
            color_discrete_map=MEDAL_COLORS, title="Daily Medal Distribution by Country",
            template="plotly_dark"
        )
        st.plotly_chart(fig_daily, use_container_width=True)

        # --- Detailed Events Table ---
        st.subheader("Detailed Medal Events")
        
        display_cols = ['Medal', 'NOC', 'Sport', 'event', 'Athlete_Name']
        
        # Sort events by Medal Type (Gold -> Silver -> Bronze)
        medal_order = pd.CategoricalDtype(
            ['Gold Medal', 'Silver Medal', 'Bronze Medal'], ordered=True
        )
        daily_events_sorted = daily_events.copy()
        daily_events_sorted['Medal'] = daily_events_sorted['Medal'].astype(medal_order)
        daily_events_sorted = daily_events_sorted.sort_values(
            by=['Medal', 'NOC', 'event'], ascending=[True, True, True]
        )
        
        st.dataframe(
            daily_events_sorted[display_cols].reset_index(drop=True).rename(
                columns={'Athlete_Name': 'Athlete'}
            ),
            use_container_width=True,
            hide_index=True
        )