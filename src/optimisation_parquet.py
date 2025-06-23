import pandas as pd
import time
from pathlib import Path


# ==============================================================================
# CONFIGURATION
# ==============================================================================
# : Modifiez ces deux chemins pour qu'ils correspondent à votre projet
CHEMIN_ORIGINAL = Path(__file__).parents[1] / "data" / "df_final_15min_NoNan_20250505.parquet"
CHEMIN_OPTIMISE = Path(__file__).parents[1] / "data" / "df_final_15min_NoNan_20250505_OPTIMISE.parquet"


# ==============================================================================
# SCRIPT D'OPTIMISATION
# ==============================================================================
print("--- Début de l'optimisation complète du fichier Parquet ---")
start_total_time = time.time()

# 1. Charger le fichier original en entier
print(f"\n[ÉTAPE 1/6] Chargement du fichier original : {CHEMIN_ORIGINAL}...")
start_time = time.time()
try:
    df = pd.read_parquet(CHEMIN_ORIGINAL)
    print(f"-> Fichier chargé en {time.time() - start_time:.2f} secondes. ({len(df):,} lignes)")
except FileNotFoundError:
    print(f"\nERREUR : Le fichier '{CHEMIN_ORIGINAL}' n'a pas été trouvé.")
    print("Veuillez vérifier que le chemin est correct dans la variable CHEMIN_ORIGINAL.")
    exit() # Arrête le script si le fichier n'est pas trouvé


# 2. S'assurer que la colonne de date est au bon format
print("\n[ÉTAPE 2/6] Conversion de la colonne de date...")
start_time = time.time()
df['heure_arrondie'] = pd.to_datetime(df['heure_arrondie'])
print(f"-> Conversion terminée en {time.time() - start_time:.2f} s.")

# 3. Création des colonnes utiles pour les analyses (feature engineering)
print("\n[ÉTAPE 3/6] Création des nouvelles colonnes (date, semaine, jour)...")
start_time = time.time()
df['date_seule'] = df['heure_arrondie'].dt.date
df["semaine"] = df["heure_arrondie"].dt.isocalendar().week
df["jour_num"] = df["heure_arrondie"].dt.weekday
map_jours = {
    0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi",
    4: "vendredi", 5: "samedi", 6: "dimanche"
}
df["jour_sem"] = df["jour_num"].map(map_jours)
print(f"-> Colonnes créées en {time.time() - start_time:.2f} s.")

# 4. Sélectionner UNIQUEMENT les colonnes utilisées par le dashboard
print("\n[ÉTAPE 4/6] Sélection des colonnes utiles...")
colonnes_a_garder = [
    # Colonnes de temps
    'heure_arrondie', 'date_seule', 'semaine', 'jour_sem',
    
    # Colonnes d'identification et de mesure du trafic
    'nom_du_troncon', 'etat_du_trafic', 'debit', 'taux_occupation',
    
    # Colonnes des facteurs externes
    'precipitation', 'visibility', 'wind_speed_10m', 'temperature_2m',
    'has_event_near_troncon', 'code_pm25'
]
# On vérifie que toutes les colonnes à garder existent avant de filtrer
colonnes_existantes = [col for col in colonnes_a_garder if col in df.columns]
df = df[colonnes_existantes]
print(f"-> Sélection terminée. {len(df.columns)} colonnes conservées.")


# 5. Trier le DataFrame par date ( crucial pour la performance des filtres)
print("\n[ÉTAPE 5/6] Tri du DataFrame par 'heure_arrondie'...")
start_time = time.time()
df = df.sort_values('heure_arrondie')
print(f"-> Données triées en {time.time() - start_time:.2f} s.")

# 6. Sauvegarder le DataFrame final : trié, enrichi et allégé
print(f"\n[ÉTAPE 6/6] Sauvegarde du fichier final optimisé : {CHEMIN_OPTIMISE}...")
start_time = time.time()
df.to_parquet(CHEMIN_OPTIMISE, engine='pyarrow', index=False)
print(f"-> Nouveau fichier sauvegardé en {time.time() - start_time:.2f} s.")

print("\n" + "="*60)
print("--- OPTIMISATION TERMINÉE ! ---")
print(f"Temps total de l'opération : {time.time() - start_total_time:.2f} secondes.")
print(f"Vous pouvez maintenant utiliser le fichier '{CHEMIN_OPTIMISE}' dans votre application Streamlit.")
print("="*60)