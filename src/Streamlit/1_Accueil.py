import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from PIL import Image
import requests
import folium
import pandas as pd
from shapely.geometry import LineString
import geopandas as gpd
from branca.element import Template, MacroElement
from streamlit_folium import folium_static
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh


# --- Configuration intitulé navigateur ---
st.set_page_config(page_title="Trafic Routier Nantes", page_icon="🚦", layout="wide")

hide_menu_style = """
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- Rafraîchissemet automatique ---
st_autorefresh(interval=600000, key="refresh")

# --- Menu personnalisé ---
st.sidebar.title("🚦 Menu")

selection = st.sidebar.radio(
    "Navigation",
    ["Accueil", "Accès publique", "Accès mairie"]
)

# --- Gestion des pages ---
if selection == "Accueil":
    st.title("🏠 Accueil")
    st.write("Explorez en temps réel l’état de la circulation sur les principaux axes de la métropole.Visualisez les conditions de trafic, identifiez les zones fluides ou congestionnées, et prenez les meilleures décisions pour vos déplacements.")
elif selection == "Accès publique":
    st.title("🚗 Accès publique")
    st.write("Visualisation publique des données de trafic.")
elif selection == "Accès mairie":
    st.title("🏢 Accès mairie")
    st.write("Section réservée à la mairie avec données détaillées.")
st.write("")  
st.subheader("État actuel du trafic routier nantais")

# --- Appel API ---
api_url = "https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=244400404_fluidite-axes-routiers-nantes-metropole&rows=10000&timezone=Europe%2FParis"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0"  # Remplace par ton contact
}

response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    data = response.json()
    records = data.get("records", [])
    
# --- Clean data ---
df = pd.json_normalize(
    records, 
    sep='_',
)

# Filtered
columns = ['record_timestamp', 'fields_cha_lib', 'fields_geo_shape_coordinates']
df_filtered = df[columns]

# Get date and time
df_filtered['record_timestamp'] = pd.to_datetime(df_filtered['record_timestamp'])
record_date = df_filtered['record_timestamp'].dt.strftime('%d/%m/%Y').max()
record_time = df_filtered['record_timestamp'].dt.strftime('%H:%M').max()


# Transformer toutes les coordonnées en LineString
df['geometry'] = df['fields_geo_shape_coordinates'].apply(LineString)

# Convertir en GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

# Créer une carte centrée sur Nantes
map_nantes = folium.Map(location=[47.2184, -1.5536], zoom_start=13,
    tiles='CartoDB positron')

# 1. Tronçons Fluide
for idx, row in gdf[gdf["fields_etat_trafic"] == 'Fluide'].iterrows():
    if isinstance(row['geometry'], LineString):
        folium.PolyLine(
            locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
            color='green',
            weight=2,
            opacity=0.7,
            tooltip=row.get("fields_cha_lib", "")
        ).add_to(map_nantes)

# 2. Tronçons Dense
for idx, row in gdf[gdf["fields_etat_trafic"] == 'Dense'].iterrows():
    if isinstance(row['geometry'], LineString):
        folium.PolyLine(
            locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
            color='orange',
            weight=2,
            opacity=0.7,
            tooltip=row.get("fields_cha_lib", "")
        ).add_to(map_nantes)

# 3. Tronçons Saturé
for idx, row in gdf[gdf["fields_etat_trafic"] == 'Saturé'].iterrows():
    if isinstance(row['geometry'], LineString):
        folium.PolyLine(
            locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
            color='red',
            weight=2,
            opacity=0.7,
            tooltip=row.get("fields_cha_lib", "")
        ).add_to(map_nantes)

# 4. Tronçons Bloqué
for idx, row in gdf[gdf["fields_etat_trafic"] == 'Bloqué'].iterrows():
    if isinstance(row['geometry'], LineString):
        folium.PolyLine(
            locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
            color='black',
            weight=2,
            opacity=0.7,
            tooltip=row.get("fields_cha_lib", "")
        ).add_to(map_nantes)
        
# 5. Tronçons Indéterminé
for idx, row in gdf[gdf["fields_etat_trafic"] == 'Indéterminé'].iterrows():
    if isinstance(row['geometry'], LineString):
        folium.PolyLine(
            locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
            color='gray',
            weight=2,
            opacity=0.7,
            tooltip=row.get("fields_cha_lib", "")
        ).add_to(map_nantes)

# Légende
legend_html = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 50px; left: 50px; width: 150px; height: 160px; 
    background-color: white; 
    border:2px solid grey; 
    z-index:9999; 
    font-size:14px;
    padding: 10px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    ">
    <b>Densité du trafic</b><br>
    <i style="background:green; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Fluide<br>
    <i style="background:orange; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Dense<br>
    <i style="background:red; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Saturé<br>
    <i style="background:black; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Bloqué<br>
    <i style="background:gray; width:12px; height:12px; border-radius:50%; float:left; margin-right:8px;"></i> Indéterminé<br>
</div>
{% endmacro %}
"""

# Injection dans la carte
legend = MacroElement()
legend._template = Template(legend_html)
map_nantes.get_root().add_child(legend)

# Rendu complet du HTML (pas juste _repr_html_())
m_html = map_nantes.get_root().render()

# Injecte le HTML complet dans Streamlit
components.html(m_html, height=600)

st.write(f"Dernière mise à jour le {record_date} à {record_time}")
st.markdown("""
###### 🔄 _Mise à jour automatique toutes les 10 minutes. Les données de circulation sont actualisées régulièrement pour vous garantir une information la plus récente possible._  
""")
