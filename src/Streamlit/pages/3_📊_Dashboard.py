import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard")
st.write("Explorez les données pour comprendre le trafic nantais.")
st.write("") 

DATA_PATH = Path(__file__).parents[1] / "data" / "df_final_15min_NoNan_20250505.parquet"

# Charger les données
@st.cache_data
def load_data():
    df = pd.read_parquet(DATA_PATH, engine="fastparquet")
    df["heure_arrondie"] = pd.to_datetime(df["heure_arrondie"])
    return df.sort_values("heure_arrondie")

df = load_data()

st.header("Analyse du trafic")
st.write("")
# KPI : performance du réseau 
st.subheader("Performance globale du réseau")

# Calcul des proportions
state_counts = df["etat_du_trafic"].value_counts(normalize=True) * 100
fluide_pct = state_counts.get("Fluide", 0)
congestion_pct = state_counts.get("Saturé", 0) + state_counts.get("Bloqué", 0) + state_counts.get("Dense", 0)

# Colonnes côte à côte
col1, col2 = st.columns([3, 1])

with col1:
    st.bar_chart(state_counts)

with col2:
    st.metric("% Fluide", f"{fluide_pct:.2f}%")
    st.metric("% Non Fluide", f"{congestion_pct:.2f}%")

# Top 10 tronçons les plus problématiques 
st.subheader("Top 10 tronçons les plus congestionnés")

df_blocked = df[df["etat_du_trafic"].isin(["Saturé", "Bloqué", "Dense"])]
problems = df_blocked["nom_du_troncon"].value_counts().head(10).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(problems.index, problems.values, color="#2196F3")
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 50, f"{int(height)}", ha='center')
ax.set_ylabel("Nombre de cas de congestion")
ax.set_xlabel("Tronçon")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)


st.header("Analyse de l'impact des facteurs externes sur le trafic")
st.subheader("Impact de la météo sur l'état du trafic")

# Variables météo à afficher
weather_vars = ["precipitation", "visibility", "wind_speed_10m", "temperature_2m"]

# Dictionnaire pour renommer les variables dans l'interface
display_names = {
    "precipitation": "Précipitations (mm)",
    "visibility": "Visibilité (m)",
    "wind_speed_10m": "Vitesse du vent (km/h)",
    "temperature_2m": "Température (°C)"
}

# Couleurs personnalisées par classe de trafic
traffic_colors = {
    "Fluide": "#4CAF50",
    "Dense": "#FFC107",
    "Saturé": "#FF5722",
    "Bloqué": "#F44336"
}

# Afficher 2 graphes par ligne
for i in range(0, len(weather_vars), 2):
    cols = st.columns(2)

    for j in range(2):
        if i + j < len(weather_vars):
            # Nom technique de la variable
            var = weather_vars[i + j]
            # Nom à afficher, récupéré du dictionnaire
            display_name = display_names.get(var, var)

            with cols[j]:
                st.subheader(display_name)
                mean_vals = df.groupby("etat_du_trafic")[var].mean()
                
                # S'assurer que l'ordre des couleurs correspond à l'ordre de l'index de mean_vals
                colors = [traffic_colors.get(state, "#999999") for state in mean_vals.index]

                fig, ax = plt.subplots()
                ax.bar(mean_vals.index, mean_vals.values, color=colors)
                
                # Utiliser le joli nom pour les labels et le titre
                ax.set_ylabel(display_name)
                ax.set_xlabel("État du trafic")
                ax.set_title(f"Moyenne de {display_name}")
                
                # Améliorer la lisibilité des labels de l'axe X si les noms sont longs
                plt.xticks(rotation=15, ha="right")
                plt.tight_layout() 

                st.pyplot(fig)


st.write("")
# Visualisation événements proximité 
st.subheader("Impact des événements sur l'état du trafic")


# Table de contingence
contingency = pd.crosstab(df["etat_du_trafic"], df["has_event_near_troncon"], normalize='columns') * 100

# Heatmap
fig, ax = plt.subplots()
sns.heatmap(contingency, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax)
ax.set_xlabel("Présence d'un événement à proximité")
ax.set_ylabel("État du trafic")
ax.set_xticklabels(['Aucun événement', 'Événement détecté'], rotation=0)
ax.set_title("Répartition (%) de l'état du trafic selon la présence d'un événement")

# Affichage dans Streamlit
st.pyplot(fig, use_container_width=True)