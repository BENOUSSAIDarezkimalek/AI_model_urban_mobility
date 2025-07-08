import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

def fetch_table_from_trafic_db(table_name) :
    '''
        Récupère toutes les données d'une table spécifique depuis la base de données de trafic.
        
        Args:
            table_name (str): Le nom de la table à récupérer.
            
        Returns:
            pd.DataFrame: Un DataFrame contenant les données de la table demandée.
    '''
    engine = create_engine(DATABASE_URL)
    query = f"SELECT * FROM {table_name};" 
    df = pd.read_sql(query, engine)
    return df
