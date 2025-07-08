# import pandas as pd
# import json

# def json_to_dataframe(data_list):
#     """
#     Transforme une liste de dictionnaires (fields) en DataFrame normalisée.
#     """
#     rows_list = []


#     for fields in data_list:
#         geo_point = fields.get("geo_point_2d", [None, None])  # Pour récupérer lat/lon

#         # Inverser geo_point_2d pour coordinates_geo : [lat, lon] -> [lon, lat]
#         coordinates_geo = [geo_point[1], geo_point[0]] if all(geo_point) else [None, None]
#         row = {
#             "id": fields.get("cha_id"),
#             "debit": fields.get("mf1_debit"),
#             "longueur": fields.get("cha_long"),
#             "taux_occupation": fields.get("mf1_taux"),
#             "code_couleur": fields.get("couleur_tp"),
#             "nom_du_troncon": fields.get("cha_lib"),
#             "etat_du_trafic": fields.get("etat_trafic"),
#             "temps_de_parcours": fields.get("tc1_temps"),
#             "vitesse": fields.get("mf1_vit"),
#             "geo_point_2d": str(fields.get("geo_point_2d")),  # Liste => texte
#             "geometrie": json.dumps(fields.get("geo_shape")),  # Dict => JSON string
#             "shape_geo": fields.get("geo_shape", {}).get("type"),
#             "horodatage": fields.get("mf1_hd"),  # Timestamp brut
#             "type_geo": 'Point',  # Pas présent dans tes données, mettre None
#             "coordinates_geo": str(coordinates_geo)
#         }

#         rows_list.append(row)

#     # Transformer en DataFrame
#     df = pd.DataFrame(rows_list)
#     return df

# import pandas as pd

# def json_to_dataframe(data_list):
#     """
#     Transforme une liste de dictionnaires (fields) en DataFrame avec format identique à la BDD.
#     """
#     rows_list = []

#     for fields in data_list:
#         geo_point = fields.get("geo_point_2d", [None, None])  # [lat, lon]

#         # Inverser geo_point_2d pour coordinates_geo (lon, lat)
#         coordinates_geo = [geo_point[1], geo_point[0]] if all(geo_point) else [None, None]

#         # Récupérer les coordonnées de la géométrie
#         geo_shape = fields.get("geo_shape", {})
#         coordinates_shape = geo_shape.get('coordinates', [])

#         # Formater les données selon ce qu'on veut en BDD
#         row = {
#             "id": fields.get("cha_id"),  # int
#             "debit": fields.get("mf1_debit"),  # int
#             "longueur": fields.get("cha_long"),  # int
#             "taux_occupation": fields.get("mf1_taux"),  # float
#             "code_couleur": int(fields.get("couleur_tp")) if fields.get("couleur_tp") else None,  # int
#             "nom_du_troncon": fields.get("cha_lib"),  # str
#             "etat_du_trafic": fields.get("etat_trafic"),  # str
#             "temps_de_parcours": fields.get("tc1_temps"),  # int
#             "vitesse": fields.get("mf1_vit"),  # int
#             "geo_point_2d": f"{{{geo_point[0]},{geo_point[1]}}}" if all(geo_point) else None,  # {lat,lon}
#             "geometrie": "{" + "},{".join([f"{c[0]},{c[1]}" for c in coordinates_shape]) + "}" if coordinates_shape else None,  # {{lon,lat},{lon,lat}}
#             "shape_geo": geo_shape.get("type"),  # str
#             "horodatage": pd.to_datetime(fields.get("mf1_hd")).strftime('%Y-%m-%d %H:%M:%S.000') if fields.get("mf1_hd") else None,  # format timestamp
#             "type_geo": "Point",  # str
#             "coordinates_geo": f"{{{coordinates_geo[0]},{coordinates_geo[1]}}}" if all(coordinates_geo) else None  # {lon,lat}
#         }

#         rows_list.append(row)

#     # Transformer en DataFrame
#     df = pd.DataFrame(rows_list)
#     return df


import pandas as pd

def json_to_dataframe(data_list):
    """
    Transforme une liste de dictionnaires (fields) en DataFrame avec format identique à la BDD.
    """
    rows_list = []

    for fields in data_list:
        geo_point = fields.get("geo_point_2d", [None, None])  # [lat, lon]

        # Inverser geo_point_2d pour coordinates_geo : [lat, lon] -> [lon, lat]
        coordinates_geo = [geo_point[1], geo_point[0]] if all(geo_point) else [None, None]

        # Récupérer les coordonnées de la géométrie
        geo_shape = fields.get("geo_shape", {})
        coordinates_shape = geo_shape.get('coordinates', [])

        # Correction du format de geometrie : {{lon,lat},{lon,lat}}
        geometrie = None
        if coordinates_shape:
            geometrie = "{" + ",".join([f"{{{lon},{lat}}}" for lon, lat in coordinates_shape]) + "}"

        # Préparer la ligne finale
        row = {
            "id": fields.get("cha_id"),  # int
            "debit": fields.get("mf1_debit"),  # int
            "longueur": fields.get("cha_long"),  # int
            "taux_occupation": fields.get("mf1_taux"),  # float
            "code_couleur": int(fields.get("couleur_tp")) if fields.get("couleur_tp") else None,  # int
            "nom_du_troncon": fields.get("cha_lib"),  # str
            "etat_du_trafic": fields.get("etat_trafic"),  # str
            "temps_de_parcours": fields.get("tc1_temps"),  # int
            "vitesse": fields.get("mf1_vit"),  # int
            "geo_point_2d": f"{{{geo_point[0]},{geo_point[1]}}}" if all(geo_point) else None,  # {lat,lon}
            "geometrie": geometrie,  # format corrigé
            "shape_geo": geo_shape.get("type"),  # str
            "horodatage": pd.to_datetime(fields.get("mf1_hd")).strftime('%Y-%m-%d %H:%M:%S.000') if fields.get("mf1_hd") else None,  # format timestamp
            "type_geo": "Point",  # str
            "coordinates_geo": f"{{{coordinates_geo[0]},{coordinates_geo[1]}}}" if all(coordinates_geo) else None  # {lon,lat}
        }
        
        rows_list.append(row)

    # Transformer en DataFrame
    df = pd.DataFrame(rows_list)
    return df
