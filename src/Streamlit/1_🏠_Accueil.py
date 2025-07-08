import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import requests
from shapely.geometry import LineString
from branca.element import Template, MacroElement
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# --- Configuration de la page ---
st.set_page_config(page_title="Trafic Routier Nantes", page_icon="🚦", layout="wide")


# ==============================================================================
# FONCTIONS LOGIQUES
# ==============================================================================

@st.cache_data(ttl=600)
def load_and_process_data():
    """
    Récupère les données depuis l'API, les nettoie, les transforme en GeoDataFrame
    et les met en cache pour 10 minutes (600 secondes).
    """
    api_url = "https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=244400404_fluidite-axes-routiers-nantes-metropole&rows=10000&timezone=Europe%2FParis"
    headers = {
        "User-Agent": "Projet Etudiant IA Trafic Nantes"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP (4xx/5xx)
        data = response.json()
        records = data.get("records", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API: {e}")
        return None, None, None
    except json.JSONDecodeError:
        st.error("Réponse invalide de l'API (non-JSON).")
        return None, None, None
        
    if not records:
        st.warning("Aucune donnée de trafic n'a été retournée par l'API.")
        return None, None, None

    # --- Traitement des données ---
    df = pd.json_normalize(records, sep='_')
    
    # Conversion du timestamp
    df['record_timestamp'] = pd.to_datetime(df['record_timestamp'])
    record_date = df['record_timestamp'].dt.strftime('%d/%m/%Y').max()
    record_time = df['record_timestamp'].dt.strftime('%H:%M').max()

    # Transformation en GeoDataFrame
    df['geometry'] = df['fields_geo_shape_coordinates'].apply(LineString)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
    
    return gdf, record_date, record_time

def create_traffic_map(gdf):
    """
    Crée et retourne une carte Folium à partir d'un GeoDataFrame de trafic.
    """
    # Créer la carte de base
    traffic_map = folium.Map(location=[47.2184, -1.5536], zoom_start=13, tiles='CartoDB positron')
    
    # Dictionnaire pour mapper l'état du trafic aux couleurs
    color_map = {
        'Fluide': 'green',
        'Dense': 'orange',
        'Saturé': 'red',
        'Bloqué': 'black',
        'Indéterminé': 'gray'
    }
    gdf['color'] = gdf['fields_etat_trafic'].map(color_map)

    # Une seule boucle pour dessiner tous les tronçons. 
    for _, row in gdf.iterrows():
        if isinstance(row['geometry'], LineString) and pd.notna(row['color']):
            folium.PolyLine(
                locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
                color=row['color'],
                weight=2,  
                opacity=0.8,
                tooltip=f"<b>{row.get('fields_cha_lib', '')}</b><br>État: {row['fields_etat_trafic']}"
            ).add_to(traffic_map)

    # Légende
    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: 160px; 
    background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
    padding: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <b>Densité du trafic</b><br>
        <i style="background:green; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Fluide<br>
        <i style="background:orange; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Dense<br>
        <i style="background:red; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Saturé<br>
        <i style="background:black; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Bloqué<br>
        <i style="background:gray; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Indéterminé<br>
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

st_autorefresh(interval=600000, key="refresh")
st.title("🏠 Accueil")
st.write("Explorez en temps réel l’état de la circulation sur les principaux axes de la métropole. Visualisez les conditions de trafic, identifiez les zones fluides ou congestionnées, et prenez les meilleures décisions pour vos déplacements.")
st.write("")  
st.subheader("État actuel du trafic routier nantais")

with st.spinner("Récupération des dernières données de trafic..."):
    gdf, record_date, record_time = load_and_process_data()

if gdf is not None:
    map_nantes = create_traffic_map(gdf)
    components.html(map_nantes.get_root().render(), height=600)
    st.write(f"Dernière mise à jour le {record_date} à {record_time}")
    st.markdown("""
    ###### 🔄 _Mise à jour automatique toutes les 10 minutes._  
    """)