import streamlit as st
import pandas as pd
import ast
from datetime import datetime
import plotly.express as px
import re
from pathlib import Path

# --- Configurer la page ---
st.set_page_config(
    page_title="Paris 2024 Athlete Dashboard",
    page_icon="🏅",
    layout="wide"
)

# --- Supprimer header/footer Streamlit ---
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- CSS global amélioré ---
st.markdown("""
<style>
.stApp { background-color: #1B1108 !important; }

/* Avatar avec gradient et ombre */
.avatar-container {
    width: 260px;
    height: 260px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FFD500, #F9B93A);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    box-shadow: 0 8px 25px rgba(249, 185, 58, 0.35);
    border: 3px solid #F9B93A;
}
.avatar-initials {
    font-size: 100px;
    font-weight: 800;
    color: white;
    font-family: 'Arial Black', sans-serif;
}

/* Encadré infos athlète modernisé */
.athlete-info {
    max-width: 580px;
    background-color: #FFF8F0;
    padding: 25px;
    border-radius: 25px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.15);
    border: 2px solid #F9B93A;
    font-size: 20px;
    color: #5A3E36;
    margin-left: 40px;
}

/* Section header avec ligne décorative */
.section-header {
    margin-top: 40px;
    margin-bottom: 25px;
    color: white;
    font-weight: bold;
    font-size: 28px;
    border-bottom: 3px solid #F9B93A;
    padding-bottom: 5px;
}

/* Selectbox stylisée */
div.stSelectbox > div[role="combobox"] > div {
    background-color: white !important;
    color: #5A3E36 !important;
    border-radius: 15px !important;
    border: 2px solid #F9B93A !important;
    padding: 8px 12px !important;
    font-size: 16px;
    margin-bottom: 25px;
    transition: all 0.3s ease;
}
div.stSelectbox > div[role="combobox"] > div:hover {
    border-color: #FFD500 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Couleurs olympiques ---
olympic_colors = ["#1A73E8", "#F4C300", "#4E342E", "#009F4D", "#D32F2F"]

# --- Charger les données ---
BASE_DIR = Path(__file__).parent.parent  # remonte d'un dossier (depuis pages/ → projet/)
DATA_DIR = BASE_DIR / "data"

athletes = pd.read_csv(DATA_DIR / "athletes.csv")
coaches = pd.read_csv(DATA_DIR / "coaches.csv") if (DATA_DIR / "coaches.csv").exists() else None
teams = pd.read_csv(DATA_DIR / "teams.csv") if (DATA_DIR / "teams.csv").exists() else None
medals = pd.read_csv(DATA_DIR / "medals.csv")

# --- Fonctions utilitaires ---
def create_avatar(name):
    initials = "??" if pd.isna(name) or not name else (str(name).strip()[:2].upper() if len(str(name).strip())>=2 else str(name).strip().upper() + "?")
    return f'''
    <div class="avatar-container">
        <div class="avatar-initials">{initials}</div>
    </div>
    '''

def safe_literal_eval(x):
    try:
        return ast.literal_eval(x)
    except:
        return []

def clean_coach_name(name):
    if not name or pd.isna(name):
        return None
    name = re.sub(r'^\s*(Personal|National)\s*[:\-]\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\([A-Z]{3}\)', '', name)
    return name.strip() if name else None

# -------------------------------
# 1️⃣ Athlete Detailed Profile
# -------------------------------
st.markdown('<div class="section-header">Athlete Detailed Profile</div>', unsafe_allow_html=True)

athlete_names = athletes['name'].dropna().tolist()
selected_athlete_name = st.selectbox("Select Athlete", athlete_names)

athlete = athletes[athletes['name'] == selected_athlete_name].iloc[0]

col1, col2 = st.columns([1,1])
with col1:
    st.markdown(create_avatar(selected_athlete_name), unsafe_allow_html=True)

with col2:
    country_info = []
    if 'country' in athlete and pd.notna(athlete['country']):
        country_info.append(str(athlete['country']))
    if 'country_code' in athlete and pd.notna(athlete['country_code']):
        country_info.append(f"({athlete['country_code']})")
    
    coach_list = []
    if 'coach' in athlete and pd.notna(athlete['coach']):
        coach_list += [c.strip() for c in athlete['coach'].split(',')]
    if coaches is not None and 'athlete_id' in coaches.columns:
        coach_list += coaches[coaches['athlete_id']==athlete['code']]['coach_name'].tolist()
    if teams is not None and 'athlete_id' in teams.columns:
        coach_list += teams[teams['athlete_id']==athlete['code']]['coach_name'].tolist()
    coach_list = list(dict.fromkeys(filter(None,[clean_coach_name(c) for c in coach_list])))

    sports_list = []
    if pd.notna(athlete.get('disciplines', None)):
        sports_list += safe_literal_eval(athlete['disciplines'])
    if pd.notna(athlete.get('other_sports', None)):
        sports_list += safe_literal_eval(athlete['other_sports'])

    st.markdown(f"""
    <div class="athlete-info">
        <p><strong>Full Name:</strong> {athlete['name']}</p>
        <p><strong>Country/NOC:</strong> {' '.join(country_info) if country_info else 'Not available'}</p>
        <p><strong>Height:</strong> {athlete['height']} cm</p>
        <p><strong>Weight:</strong> {athlete['weight']} kg</p>
        <p><strong>Coach(s):</strong> {', '.join(coach_list) if coach_list else 'Not available'}</p>
        <p><strong>Sport(s) & Discipline(s):</strong> {', '.join(sports_list) if sports_list else 'Not available'}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------
# 2️⃣ Athlete Age Distribution
# -------------------------------
st.markdown('<div class="section-header">Athlete Age Distribution</div>', unsafe_allow_html=True)

if 'birth_date' in athletes.columns:

    # --- Calcul âge ---
    athletes['birth_date'] = pd.to_datetime(athletes['birth_date'], errors='coerce')
    athletes['age'] = (pd.to_datetime("2024-07-26") - athletes['birth_date']).dt.days // 365

    # --- Extraire toutes les disciplines ---
    if 'disciplines' in athletes.columns:
        all_disciplines = sorted(
            list(set([d for sublist in athletes['disciplines'].dropna().apply(safe_literal_eval) for d in sublist]))
        )
        all_disciplines = ["All"] + all_disciplines  # ADD "All"

        selected_sport = st.selectbox("Select a Sport for Age Distribution", all_disciplines)

        # --- Filtrage ---
        if selected_sport == "All":
            sport_athletes = athletes.copy()
        else:
            sport_athletes = athletes[
                athletes['disciplines'].apply(
                    lambda x: selected_sport in safe_literal_eval(x) if pd.notna(x) else False
                )
            ]

        # --- Plot ---
        if not sport_athletes.empty and 'gender' in sport_athletes.columns:
            fig_age = px.violin(
                sport_athletes,
                x="gender",
                y="age",
                color="gender",
                box=True,
                points="all",
                hover_data=["name"],
                title=(
                    "Age Distribution of All Athletes"
                    if selected_sport == "All"
                    else f"Age Distribution of Athletes in {selected_sport}"
                ),
                color_discrete_sequence=olympic_colors
            )

            fig_age.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                margin=dict(t=50, l=20, r=20, b=50),
                font=dict(color="#1B1108"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#F9B93A"),
                title_font=dict(size=20, color="#1B1108", family="Arial Black"),
                legend=dict(title='Gender', font=dict(color='#1B1108'))
            )

            fig_age.update_traces(marker_line_color="#F9B93A", marker_line_width=2)
            st.plotly_chart(fig_age, use_container_width=True)

        else:
            st.info("No data available for age distribution.")


# -------------------------------
# 3️⃣ Gender Distribution by Country
# -------------------------------
st.markdown('<div class="section-header">Gender Distribution by Country</div>', unsafe_allow_html=True)

if 'country' in athletes.columns and 'gender' in athletes.columns:
    countries = ["All"] + list(athletes['country'].dropna().unique())
    selected_country = st.selectbox("Select Country (or All)", countries)
    if selected_country != "All":
        gender_df = athletes[athletes['country']==selected_country]['gender'].value_counts().reset_index()
    else:
        gender_df = athletes['gender'].value_counts().reset_index()
    gender_df.columns = ['gender','count']
    
    if not gender_df.empty:
        fig_gender = px.bar(
            gender_df,
            x='gender',
            y='count',
            color='gender',
            text='count',
            title=f"Gender Distribution {'in ' + selected_country if selected_country != 'All' else 'Worldwide'}",
            color_discrete_sequence=olympic_colors
        )
        fig_gender.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color="#1B1108"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F9B93A"),
            margin=dict(t=50, l=20, r=20, b=50),
            legend=dict(title='Gender', font=dict(color='#1B1108'))
        )
        st.plotly_chart(fig_gender, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------
# 4️⃣ Top 10 Athletes by Medals
# -------------------------------
st.markdown('<div class="section-header">Top 10 Athletes by Total Medals</div>', unsafe_allow_html=True)

if not medals.empty:
    athlete_totals = medals.groupby(['code','name'])['medal_type'].count().reset_index().rename(columns={'medal_type':'total_medals'})
    top_10_athletes = athlete_totals.sort_values(by='total_medals', ascending=False).head(10)
    
    if not top_10_athletes.empty:
        fig_medals = px.bar(
            top_10_athletes,
            x='name',
            y='total_medals',
            color='total_medals',
            text='total_medals',
            title="Top 10 Athletes by Total Medals",
            color_discrete_sequence=olympic_colors
        )
        fig_medals.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color="#1B1108"),
            xaxis_tickangle=-45,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F9B93A"),
            margin=dict(t=50, l=20, r=20, b=50),
            legend=dict(title='Medals', font=dict(color='#1B1108'))
        )
        fig_medals.update_traces(marker_line_color="#F9B93A", marker_line_width=2)
        st.plotly_chart(fig_medals, use_container_width=True)
