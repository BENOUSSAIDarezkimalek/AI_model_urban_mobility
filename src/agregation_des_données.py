
# Chargement des jeux de données
lignes = gpd.read_file("trafic_routiers.geojson")
points = gpd.read_file("ralentisseur_.geojson")

# Conversion des CRS
lignes = lignes.to_crs("EPSG:3857")
points = points.to_crs("EPSG:3857")

# Faire la jointure avec une approximation de 20 metre
test = gpd.sjoin_nearest(lignes, points, how='left', max_distance=20, distance_col='distance')
