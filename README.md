# 🏅 Olympic Games Analytics Dashboard (Paris 2024 Focus)

This interactive data dashboard, built with **Streamlit** and **Plotly**, provides a comprehensive, filtered overview and analysis of Olympic Games data, with a strong stylistic focus on the Paris 2024 event. Users can dynamically filter key metrics like athletes, medals, and events by Country (NOC), Sport, and Medal Type.

## 🚀 How to Run the Application Locally

Follow these steps to set up and run the Streamlit application on your local machine.

### Prerequisites

You must have **Python 3.8+** installed on your system.

### 1. Clone the Repository

Clone the project from your GitHub repository:

```bash
git clone [https://github.com/nabahat9/streamlit_Paris_olympics.git](https://github.com/nabahat9/streamlit_Paris_olympics.git)
cd streamlit_Paris_olympics


# 🏅 Paris 2024 Olympics – Interactive Data Analytics Dashboard

Welcome to the Paris Olympics Analytics Dashboard!  
This Streamlit application provides a rich and interactive exploration of athlete performance, medal distributions, venue locations, sports scheduling, and advanced insights through custom challenges.

---

## 🚀 How to Run the App Locally

### 📌 1. Clone the repository
```bash
git clone https://github.com/nabahat9/streamlit_Paris_olympics.git
cd paris_olympics_analytics
```



### 📌 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 📌 5. Run the application
```bash
streamlit run app.py
```

## 📁 Folder Structure
```
.
├─ app.py                 (Welcome page)
├─ utils.py           
├─ pages/
│   ├─ Global_Analysis.py
│   ├─ Athlete_Performance.py
│   ├─ bonus.py
│   ├─ Sports_and_Events.py
├ data/
├ utils/
│   ├─ results/
├─ requirements.txt
├─ .gitignore
├─ __init__.py
└─ README.md
```
## 🎨 Design Choices

### 🧭 Navigation
- Multi-page structure using Streamlit’s navigation.
- Logical grouping for readability.

### 🖼️ UI/UX Styling
- Modern dark dashboard theme.
- Custom card-style section grouping.
- Consistent color palette.

### 🎨 Color Guidelines
- 🥇 Gold → `#FFD700`  
- 🥈 Silver → `#C0C0C0`  
- 🥉 Bronze → `#CD7F32`

---

## 📊 Core Features (Required Tasks)

### 🌍 Page 1 — Global Analysis
✔️ World medal map  
✔️ Top-20 breakdown  
✔️ Sunburst hierarchy  
✔️ Treemap view  
✔️ Continent-level comparison  

### 👥 Page 2 — Athletes Analysis
✔️ Gender stats  
✔️ Sport-level breakdown  
✔️ Nationality distribution  

### 🏅 Page 3 — Medals Insights
✔️ Global medal rankings  
✔️ Country drilldowns  

### 🏟️ Page 4 — Sports & Events
✔️ Gantt event schedule  
✔️ Venue map (Mapbox)  
✔️ Sport medal treemap  

---

## 🔗 Deployment Link
https://parisolympics2024.streamlit.app/