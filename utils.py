import streamlit as st
import pandas as pd
from pathlib import Path
import base64

def local_image_to_data_url(path: str) -> str:
    """Return a data:image/...;base64 URL for a local image file."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        st.warning(f"Error: Image not found at {path}. Using fallback.")
        return "" 
        
    mime = "image/png"
    if path.lower().endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def apply_custom_css():
    """Apply custom CSS styles for the navbar and page layout."""
    st.markdown(
        """
        <style>
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* --------------------------------- */
        /* TRANSPARENT FIXED NAVBAR STYLES */
        /* --------------------------------- */
        .fixed-navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9999; 
            background-color: transparent; /* Makes the background fully transparent */
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); 
            padding: 1rem 3rem; 
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 5rem;
            color: #f9fafb; 
        }

        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }

        .nav-links a {
            color: #ffffff; 
            text-decoration: none;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.2s;
            padding: 0.5rem 1rem;
            border-radius: 8px;
        }

        .nav-links a:hover {
            background-color: rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }
        
        .nav-links a.active {
            font-weight: 700;
            background-color: rgba(255, 255, 255, 0.15);
        }

        .header-logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #ffffff;
            cursor: pointer;
        }
        
        .logo-image {
            height: 3.5rem;
            width: auto;
        }

        /* --------------------------------- */
        /* GLOBAL SPACE & PADDING FIXES */
        /* --------------------------------- */
        .block-container {
            padding-top: 6rem !important; 
            padding-bottom: 1rem;
            max-width: none;
        }
        
        /* --------------------------------- */
        /* METRIC CARDS AND SECTIONS */
        /* --------------------------------- */
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_navbar(current_page):
    """
    NAVBAR FINALE - Fonctionne avec Streamlit >=1.24.0
    """
    BASE_DIR = Path(__file__).parent
    LOGO_IMAGE_PATH = BASE_DIR / "utils" / "logo.png"
    
    if LOGO_IMAGE_PATH.exists():
        LOGO_IMAGE_URL = local_image_to_data_url(str(LOGO_IMAGE_PATH))
    else:
        LOGO_IMAGE_URL = ""
    
    # Pages disponibles - ADAPTEZ CES NOMS À VOS FICHIERS
    pages = [
        ("overview", "Overview"),
        ("Global_Analysis", "Global Analysis"),
        ("Athlete_Performance", "Athlete Performance"),
        ("Sports_and_Events", "Sports & Events"),
        ("bonus", "Bonus")
    ]
    
    # Créer les liens avec la BONNE SYNTAXE Streamlit
    nav_links = ""
    for page_id, page_name in pages:
        active = "active" if current_page == page_id else ""
        
        # URL CORRECTE pour Streamlit Cloud
        # Format: /nom_du_fichier_sans_extension
        if page_id == "overview":
            url = "/"  # Page principale
        else:
            # IMPORTANT: Utilisez le NOM EXACT du fichier SANS .py
            # Si votre fichier s'appelle "Global_Analysis.py", mettez "/Global_Analysis"
            # Si votre fichier s'appelle "Global Analysis.py", mettez "/Global%20Analysis"
            url = f"/{page_id}"
        
        nav_links += f'<a href="{url}" class="{active}" onclick="return streamlitNav(event)" target="_self">{page_name}</a>'
    
    # HTML de la navbar avec JavaScript minimal
    navbar_html = f'''
    <div class="fixed-navbar">
        <div class="header-logo">
            <a href="/" onclick="return streamlitNav(event)" target="_self" style="display: flex; align-items: center; text-decoration: none;">
                <img src="{LOGO_IMAGE_URL}" class="logo-image" alt="Olympic Logo">
            </a>
        </div>
        <div class="nav-links">
            {nav_links}
        </div>
    </div>
    
    <script>
    // Fonction UNIQUE pour gérer la navigation Streamlit
    function streamlitNav(event) {{
        // IMPORTANT: Laisser Streamlit gérer la navigation normalement
        // Le target="_self" force l'ouverture dans la même fenêtre
        return true;
    }}
    
    // SIMPLE protection contre les clics molette
    document.addEventListener("DOMContentLoaded", function() {{
        const navbar = document.querySelector(".fixed-navbar");
        if (navbar) {{
            navbar.addEventListener("auxclick", function(e) {{
                if (e.button === 1 && (e.target.tagName === "A" || e.target.closest("a"))) {{
                    e.preventDefault();
                }}
            }}, true);
        }}
    }});
    </script>
    '''
    
    st.markdown(navbar_html, unsafe_allow_html=True)

def get_medal_column(df: pd.DataFrame, medal_name: str):
    """
    Try to find the column corresponding to a medal type (gold/silver/bronze)
    using a case-insensitive substring search.
    """
    medal_name = medal_name.lower()
    for col in df.columns:
        cl = col.lower()
        if cl == medal_name or medal_name in cl:
            return col
    return None


# Data loading functions
DATA_DIR = Path("data")

@st.cache_data
def load_data():
    """Load all Olympic data files."""
    try:
        athletes = pd.read_csv(DATA_DIR / "athletes.csv")
        events = pd.read_csv(DATA_DIR / "events.csv")
        medals_total = pd.read_csv(DATA_DIR / "medals_total.csv")
        nocs = pd.read_csv(DATA_DIR / "nocs.csv")
    except FileNotFoundError as e:
        athletes = pd.DataFrame(columns=['id', 'sport'])
        events = pd.DataFrame(columns=['sport', 'event_id'])
        medals_total = pd.DataFrame(columns=['noc', 'gold', 'silver', 'bronze', 'total'])
        nocs = pd.DataFrame(columns=['noc', 'country'])
        return athletes, events, medals_total, nocs

    # Standardize column names
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

    medal_cols = [c for c in medals_total.columns if c.lower() in ["gold", "silver", "bronze"]]
    if "total" not in medals_total.columns and medal_cols:
        medals_total["total"] = medals_total[medal_cols].sum(axis=1)

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