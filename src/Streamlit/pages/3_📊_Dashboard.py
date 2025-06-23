# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import plotly.express as px
from datetime import date, timedelta

# --- CONFIGURATION ET CHARGEMENT DES DONNÉES ---
st.set_page_config(page_title="Dashboard Trafic Nantes", page_icon="📊", layout="wide")

# On importe le module de traitement
try:
    import data_processing as dp
except ImportError:
    st.error("ERREUR : Le fichier `data_processing.py` est introuvable. Assurez-vous qu'il se trouve dans le même dossier que ce script.")
    st.stop()

# Chemin relatif vers votre fichier PARFAITEMENT optimisé
try:
    CHEMIN_OPTIMISE = Path(__file__).parents[1] / "data" / "df_final_15min_NoNan_20250505_OPTIMISE.parquet"
except NameError:
    CHEMIN_OPTIMISE = "data/df_final_15min_NoNan_20250505_OPTIMISE.parquet"

@st.cache_data
def load_data(path):
    """Charge le fichier Parquet qui est DÉJÀ préparé et optimisé."""
    try:
        df = pd.read_parquet(path)
        df['heure_arrondie'] = pd.to_datetime(df['heure_arrondie'])
        df['date_seule'] = pd.to_datetime(df['date_seule'])
        return df
    except FileNotFoundError:
        st.error(f"ERREUR : Le fichier optimisé est introuvable au chemin : '{path}'. Avez-vous exécuté le script d'optimisation et vérifié le chemin ?")
        return pd.DataFrame()

# Chargement unique des données au début de l'application
df = load_data(CHEMIN_OPTIMISE)

# Couleurs personnalisées par classe de trafic
traffic_colors = {
    "Fluide": "#4CAF50",
    "Dense": "#FFC107",
    "Saturé": "#FF5722",
    "Bloqué": "#F44336"
}

# --- INTERFACE PRINCIPALE ---
st.title("📊 Dashboard")
st.write("Explorez les données pour comprendre le trafic nantais.")
st.write("") 

if df.empty:
    st.warning("Le chargement des données a échoué. L'application ne peut pas continuer.")
    st.stop()

st.header("Analyse du trafic")
st.write("")

# --- KPI : performance du réseau ---
st.subheader("Performance globale du réseau")
state_counts, fluide_pct, congestion_pct = dp.get_kpis_performance(df)
col1, col2 = st.columns([3, 1])
with col1:
    st.bar_chart(state_counts)
with col2:
    st.metric("% Fluide", f"{fluide_pct:.2f}%")
    st.metric("% Non Fluide", f"{congestion_pct:.2f}%")

# --- KPI : Top 10 tronçons  ---
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
st.write("")


# --- KPI : Débit moyen journalier par semaine  ---
st.write("")
st.subheader("Débit moyen journalier par semaine")
weekly_day_data = dp.get_weekly_debit_data(df)
day_order_fr = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
fig_anim = px.bar(
    weekly_day_data,
    x="jour_sem", y="debit", color="debit",
    animation_frame="plage",
    category_orders={"jour_sem": day_order_fr},
    color_continuous_scale="Reds",
    range_color=[weekly_day_data["debit"].min(), weekly_day_data["debit"].max()],
    labels={"jour_sem":"Jour de la semaine", "debit":"Débit moyen (véhicules/h)", "plage":"Plage de dates"}
)
fig_anim.update_layout(
    xaxis_title=None, yaxis_title=None, margin={"t":50, "b":30, "l":0, "r":0}
)
st.plotly_chart(fig_anim, use_container_width=True)


# --- KPI : Taux d'occupation au fil du temps  ---
st.divider()
st.subheader("Analyse du taux d'occupation au fil du temps")
st.write("Sélectionnez une période pour visualiser le taux d'occupation.")

min_date = df['date_seule'].min()
max_date = df['date_seule'].max()

c1, c2 = st.columns(2)
start_date = c1.date_input("Date de début", min_date, min_value=min_date, max_value=max_date, key="occ_start")
end_date = c2.date_input("Date de fin", min_date, min_value=min_date, max_value=max_date, key="occ_end")

if start_date > end_date:
    st.error("Erreur : La date de début ne peut pas être après la date de fin.")
else:
    df_filtered = df[(df['date_seule'] >= pd.to_datetime(start_date)) & (df['date_seule'] <= pd.to_datetime(end_date))]
    
    st.metric("Lignes de données dans la sélection", f"{len(df_filtered):,}")

    if df_filtered.empty:
        st.warning("Aucune donnée disponible pour la période sélectionnée.")
    else:
        # --- LOGIQUE DYNAMIQUE : RÉEL vs MOYEN ---
        NOMBRE_JOURS_SEUIL = 5
        duree_selection = (end_date - start_date).days
        
        if duree_selection <= NOMBRE_JOURS_SEUIL:
            # --- VUE RÉELLE POUR LES COURTES PÉRIODES (STYLE DEMANDÉ) ---
            st.info("Affichage des données réelles (granularité de 15 min).")
            
            fig_occ = px.line(
                df_filtered.sort_values("heure_arrondie"),
                x="heure_arrondie", y="taux_occupation", color="etat_du_trafic",
                labels={"heure_arrondie":"Date & heure", "taux_occupation":"% d’occupation", "etat_du_trafic":"État du trafic"},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_occ.update_layout(
                xaxis=dict(rangeslider=dict(visible=True), type="date"),
                margin={"t":50, "b":0, "l":0, "r":0}
            )
            st.plotly_chart(fig_occ, use_container_width=True)
            
        else:
            # --- VUE MOYENNÉE POUR LES LONGUES PÉRIODES ---
            st.info(f"Pour les périodes > {NOMBRE_JOURS_SEUIL} jours, une moyenne journalière est affichée pour garantir la performance.")
            
            occupation_data_moyen = dp.get_daily_occupation_by_state(df_filtered)
            
            fig_occ_moyen = px.line(
                occupation_data_moyen, x='heure_arrondie', y='taux_occupation_moyen',
                color='etat_du_trafic', color_discrete_map=traffic_colors,
                title="Taux d'occupation moyen par état de trafic",
                labels={"heure_arrondie": "Date", "taux_occupation_moyen": "% d'occupation moyen", "etat_du_trafic": "État du trafic"}
            )
            # CORRECTION : Ajout du rangeslider ici aussi pour la cohérence
            fig_occ_moyen.update_layout(
                xaxis=dict(rangeslider=dict(visible=True), type="date"),
                margin={"t":50, "b":0, "l":0, "r":0}
            )
            st.plotly_chart(fig_occ_moyen, use_container_width=True)


# --- PART 2 : FACTEURS EXTERNES ---
st.header("Analyse de l'impact des facteurs externes sur le trafic")

# --- Impact de la météo ---
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

# --- Impact des événements ---
st.subheader("Impact des événements sur l'état du trafic")
contingency_data = dp.get_event_impact(df)
fig_event, ax_event = plt.subplots()
sns.heatmap(contingency_data, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax_event)
ax_event.set_xlabel("Présence d'un événement à proximité")
ax_event.set_ylabel("État du trafic")
ax_event.set_xticklabels(['Aucun événement', 'Événement détecté'], rotation=0)
ax_event.set_title("Répartition (%) de l'état du trafic selon la présence d'un événement")
st.pyplot(fig_event, use_container_width=True)

# --- Analyse Pollution  ---
st.header("Analyse des particules fines")
st.write("")
st.subheader("Concentration de PM₂.₅ au fil du temps")
pollution_data = dp.get_pollution_data(df)
fig_poll = px.scatter(
    pollution_data.sort_values("date_seule"),
    x="date_seule", y="code_pm25", color="code_pm25",
    color_continuous_scale="Reds",
    labels={"date_seule": "Date", "code_pm25": "PM₂.₅ (µg/m³)"}
)
fig_poll.update_traces(
    mode='lines+markers',
    marker=dict(size=9, opacity=0.9),
    line=dict(color='lightgrey', width=1)
)
fig_poll.update_layout(
    xaxis=dict(rangeslider=dict(visible=True), type="date"),
    margin={"t": 50, "b": 0, "l": 0, "r": 0},
    coloraxis_colorbar=dict(title="PM₂.₅ (µg/m³)")
)
st.plotly_chart(fig_poll, use_container_width=True)


