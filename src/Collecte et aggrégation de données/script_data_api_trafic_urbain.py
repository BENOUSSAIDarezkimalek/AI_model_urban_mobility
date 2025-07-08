import requests
import json
import pandas as pd
import psycopg
import os

# Récupération des secrets depuis les variables d'environnement
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connexion a la base Azure postgresql
def get_connection_uri():

    # Read URI parameters from the environment
    dbhost = DB_HOST
    dbname = DB_NAME
    dbuser = DB_USER
    password = DB_PASSWORD
    sslmode = 'require'
    db_uri = f"host={dbhost} dbname={dbname} user={dbuser} password={password} sslmode ={sslmode}"
    # Construct connection URI
    return db_uri

conn_string = get_connection_uri()

conn = psycopg.connect(conn_string)

# cursor pour ecrire dans la base
cur = conn.cursor()

# Connexion et recuperation des données depuis l'API
url = 'https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=244400404_fluidite-axes-routiers-nantes-metropole&rows=1000&timezone=Europe%2FParis'

response = requests.get(url)

data = response.json()

# Transformer en DataFrame
df = pd.json_normalize(data.get("records", []))

# renommer les colonne
df.rename(columns={
    'fields.cha_lib':'nom_du_tronçon',
    'fields.cha_long': 'longueur',
    'fields.mf1_taux': 'taux_occupation',
    'fields.cha_id': 'id',
    'fields.mf1_hd': 'horodatage',
    'fields.mf1_debit' : 'debit',
    'fields.mf1_vit' : 'vitesse',
    'fields.tc1_temps': 'temps_de_parcours',
    'fields.couleur_tp': 'code_couleur',
    'fields.etat_trafic': 'etat_du_trafic',
    'fields.geo_shape.coordinates': 'geometrie',
    'fields.geo_point_2d': 'geo_point_2d',
    'fields.geo_shape.type':'shape_geo',
    'geometry.type':'type_geo',
    'geometry.coordinates':'coordinates_geo'
    
}, inplace = True)

# supprimer les colonnes inutiles
df.drop(columns=['datasetid', 'recordid','record_timestamp'], inplace=True)

# mettre id a la premiere position
df = df[['id'] + [col for col in df.columns if col != 'id']]

# Ajout d'un id technique qu'on mettre comme clé primaire dans notre BDD (pour eviter les doublons)
df.insert(loc=0, column='id_technique',
           value=df['id'].map(str) + '-' + df['horodatage'].apply(lambda x: x[0:19].replace('-', '').replace(':','')))

# query pour ecrire dans la base
query= """
    INSERT INTO public.trafic_routier
(id_technique, id, debit, longueur, taux_occupation, code_couleur, nom_du_troncon, etat_du_trafic, temps_de_parcours, vitesse, geo_point_2d, geometrie, shape_geo, horodatage, type_geo, coordinates_geo)
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

# parcourir ligne par ligne le dataframe pour alimenter la base
for row in df.itertuples(index=False):
    cur.execute(query,
                 (row.id_technique, row.id, row.debit, row.longueur, row.taux_occupation,
                   row.code_couleur, row.nom_du_tronçon, row.etat_du_trafic
                  , row.temps_de_parcours, row.vitesse, row.geo_point_2d, 
                  row.geometrie, row.shape_geo, row.horodatage,
                    row.type_geo, row.coordinates_geo))
    
#confirmer les changement
conn.commit()

# Fermeture de la connexion
cur.close()
conn.close()
