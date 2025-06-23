# data_processing.py

import pandas as pd
import streamlit as st

@st.cache_data
def get_kpis_performance(_df):
    """Calcule les pourcentages de trafic fluide et non-fluide."""
    state_counts = _df["etat_du_trafic"].value_counts(normalize=True) * 100
    fluide_pct = state_counts.get("Fluide", 0)
    congestion_pct = 100 - fluide_pct
    return state_counts, fluide_pct, congestion_pct

@st.cache_data
def get_top_congested_segments(_df, top_n=10):
    """Retourne le top N des tronçons les plus congestionnés."""
    df_blocked = _df[_df["etat_du_trafic"].isin(["Saturé", "Bloqué", "Dense"])]
    problems = df_blocked["nom_du_troncon"].value_counts().head(top_n)
    return problems.sort_values(ascending=True) # Mieux pour barh

@st.cache_data
def get_weekly_debit_data(_df):
    """Prépare les données pour le graphique de débit hebdomadaire animé."""
    week_bounds = (
        _df.groupby("semaine")["heure_arrondie"]
          .agg(dt_min="min", dt_max="max")
          .reset_index()
    )
    week_bounds["plage"] = (
        week_bounds["dt_min"].dt.strftime("%d/%m/%Y")
        + " – "
        + week_bounds["dt_max"].dt.strftime("%d/%m/%Y")
    )
    ordered_plages = week_bounds.sort_values("dt_min")["plage"].tolist()

    weekly_day = (
        _df.groupby(["semaine", "jour_sem"], as_index=False)["debit"]
          .mean()
          .merge(week_bounds[["semaine","plage"]], on="semaine")
    )
    weekly_day["plage"] = pd.Categorical(weekly_day["plage"], categories=ordered_plages, ordered=True)
    day_order_fr = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
    weekly_day["jour_sem"] = pd.Categorical(weekly_day["jour_sem"], categories=day_order_fr, ordered=True)
    return weekly_day.sort_values(["plage","jour_sem"])

@st.cache_data
def get_weather_impact(_df, weather_var):
    """Calcule la moyenne d'une variable météo par état de trafic."""
    return _df.groupby("etat_du_trafic")[weather_var].mean()

@st.cache_data
def get_event_impact(_df):
    """Calcule la table de contingence pour l'impact des événements."""
    return pd.crosstab(_df["etat_du_trafic"], _df["has_event_near_troncon"], normalize='columns') * 100

@st.cache_data
def get_pollution_data(_df):
    """Extrait les données de pollution uniques par jour."""
    return _df[['date_seule', 'code_pm25']].drop_duplicates(subset=['date_seule'])

@st.cache_data
def get_daily_occupation(_df):
    """Calcule le taux d'occupation moyen journalier global."""
    return _df.resample('D', on='heure_arrondie').agg(
        taux_occupation_moyen=('taux_occupation', 'mean')
    ).reset_index()
    
@st.cache_data
def get_daily_occupation_by_state(_df):
    """
    Calcule le taux d'occupation moyen par jour ET par état de trafic.
    Prend un DataFrame (potentiellement déjà filtré) en entrée.
    """
    if _df.empty:
        return pd.DataFrame()
        
    df_agg = _df.groupby([
        pd.Grouper(key='heure_arrondie', freq='D'),
        'etat_du_trafic'
    ]).agg(
        taux_occupation_moyen=('taux_occupation', 'mean')
    ).reset_index()
    return df_agg