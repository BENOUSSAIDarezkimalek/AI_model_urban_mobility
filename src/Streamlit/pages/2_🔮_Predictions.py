import streamlit as st
import pandas as pd
import folium
from streamlit.components.v1 import html
from branca.element import Template, MacroElement
from shapely.geometry import LineString
import geopandas as gpd
import ast
from pathlib import Path
from shapely import wkt


# --- Chargement du fichier ---

DATA_PATH = Path(__file__).parents[1] / "data" / "predictions_trafic_optimise.parquet"

@st.cache_data
def load_data(path: str) -> gpd.GeoDataFrame:
    """
    Charge un fichier Parquet en DataFrame, 
    convertit la colonne 'geometry' de WKT en objets Shapely,
    puis transforme en GeoDataFrame avec CRS EPSG:4326.
    """
    df = pd.read_parquet(path)
    df['geometry'] = df['geometry'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
    return gdf

gdf = load_data(DATA_PATH)


# --- Configuration de la page ---
st.set_page_config(page_title="Prédictions", page_icon="🔮", layout="wide")

st.title("🔮 Prédictions")
st.write(
    "Sélectionnez une date et une heure pour comparer l’état **réel** du trafic "
    "avec les données **prédites** par notre modèle de Deep Learning."
)


# ==============================================================================
# FONCTIONS LOGIQUES
# ==============================================================================


def create_traffic_map(gdf, target, time_filter, prediction):
    """
    Crée et retourne une carte Folium à partir d'un GeoDataFrame de trafic.
    """
    # Créer la carte de base
    traffic_map = folium.Map(location=[47.2184, -1.5536], zoom_start=13, tiles='CartoDB positron')
    
    # Dictionnaire pour mapper l'état du trafic aux couleurs
    color_map = {
        'Fluide': 'green',
        'Non-Fluide': 'orange',
    }
    gdf['color'] = gdf[target].map(color_map)
    
    gdf_filtered = gdf.loc[gdf['heure_arrondie'] == time_filter]

    # Une seule boucle pour dessiner tous les tronçons. 
    if prediction == 0 :
        for _, row in gdf_filtered.iterrows():
            if isinstance(row['geometry'], LineString) and pd.notna(row['color']):
                folium.PolyLine(
                    locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
                    color=row['color'],
                    weight=2,  
                    opacity=0.8,
                    tooltip=f"<b>{row.get('nom_du_troncon', '')}</b><br>État: {row['etat_du_trafic_reel']}"
                ).add_to(traffic_map)
    else :
        for _, row in gdf_filtered.iterrows():
            if isinstance(row['geometry'], LineString) and pd.notna(row['color']):
                folium.PolyLine(
                    locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
                    color=row['color'],
                    weight=2,  
                    opacity=0.8,
                    tooltip=f"<b>{row.get('nom_du_troncon', '')}</b><br>État: {row['etat_du_trafic_predit']}"
                ).add_to(traffic_map)
        

    # Légende
    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed;
        bottom: 20px;  /* Plus bas sur la page */
        left: 20px;    /* Plus proche du coin */
        width: 130px;  /* Moins large */
        background-color: white;
        border: 1px solid #ccc;
        z-index: 9999;
        font-size: 12px;
        padding: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        border-radius: 5px;
    ">
        <b>Densité</b><br>
        <div style="margin-top:5px;">
            <i style="background:green; width:10px; height:10px; border-radius:50%; float:left; margin-right:6px;"></i>
            Fluide<br>
            <i style="background:orange; width:10px; height:10px; border-radius:50%; float:left; margin-right:6px;"></i>
            Non-fluide<br>
        </div>
    </div>
    {% endmacro %}
    """
    legend = MacroElement()
    legend._template = Template(legend_html)
    traffic_map.get_root().add_child(legend)
    
    return traffic_map


# ==============================================================================
# INTERFACE UTILISATEUR (UI)
# ==============================================================================

dates_disponibles = gdf['date'].sort_values().unique()
# Convertir pour un affichage plus lisible
dates_disponibles_str = [d.strftime("%d-%m-%Y") for d in dates_disponibles]


# Choix de la date et de l'heure dans un formulaire pour éviter le refresh immédiat
with st.form(key="date_heure_form"):
    col1, col2 = st.columns(2)
    with col1:
        date_selection_str = st.selectbox("📅 Choisir une date :", dates_disponibles_str)
        date_selection = pd.to_datetime(date_selection_str, format="%d-%m-%Y").date()
    with col2:
        heures_disponibles = gdf[gdf['date'] == date_selection]['heure_arrondie'].dt.strftime('%H:%M').sort_values().unique()
        heure_selection = st.selectbox("🕒 Choisir une heure :", heures_disponibles)

    submit_button = st.form_submit_button(label="✅ Valider")

# Afficher les cartes uniquement si l'utilisateur a validé
if submit_button:
    time_filter = pd.to_datetime(f"{date_selection} {heure_selection}")
    st.markdown(
        f"<p style='font-size:0.9em; font-style:italic; color:gray;'>"
        f"Prédictions pour le {date_selection.strftime('%d/%m/%Y')} à {heure_selection}"
        f"</p>",
        unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🟢 Trafic réel")
        map_reel = create_traffic_map(gdf, target='etat_du_trafic_reel', time_filter=time_filter, prediction=0)
        html(map_reel.get_root().render(), height=600)

    with st.spinner("Récupération des données de trafic..."):
        gdf_filtered = gdf[gdf['heure_arrondie'] == time_filter]

    with col2:
        st.subheader("🔶 Trafic prédit")
        map_predit = create_traffic_map(gdf, target='etat_du_trafic_predit', time_filter=time_filter, prediction=1)
        html(map_predit.get_root().render(), height=600)
else:
    st.info("Veuillez sélectionner une date et une heure, puis cliquer sur **Valider les choix**.")