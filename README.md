# 🚦 Optimisation de la Mobilité Urbaine à l'Aide de Données Ouvertes

Ce projet vise à concevoir et développer un tableau de bord interactif pour la gestion et l'optimisation de la mobilité urbaine, en exploitant les données ouvertes et les techniques d’intelligence artificielle.

## 🧭 Introduction

Les villes modernes sont confrontées à de nombreux défis en matière de mobilité : embouteillages, pollution, saturation des transports publics, baisse de qualité de vie. L’exploitation des données ouvertes offre de nouvelles opportunités pour anticiper les congestions, fluidifier le trafic et améliorer les services de mobilité urbaine.

## 🎯 Objectifs du Projet

Le projet poursuit trois objectifs principaux :

- **Prédire les conditions de circulation** : via des modèles d’analyse prédictive pour anticiper les congestions et prévoir l’évolution du trafic.
- **Fournir des outils d’aide à la décision** : sous forme de tableau de bord interactif avec visualisations et mécanismes de simulation à destination des gestionnaires urbains.
- **Favoriser une mobilité fluide, durable et participative** : en intégrant des données environnementales, comme l’indice de qualité de l’air.

## 🏗️ Architecture et Technologies

Le projet repose sur les technologies suivantes :

- **Langage** : Python, utilisé pour le traitement de données, le machine learning et le deep learning.
- **Collecte des données** : d’abord via Make, puis automatisée avec GitHub Actions.
- **Visualisation** : Streamlit, pour concevoir une interface interactive accessible.
- **Base de données** : PostgreSQL, hébergée sur Azure (région France Centrale) pour respecter la souveraineté des données et le RGPD.

## 📦 Données utilisées

### 📌 Sources

- **Trafic routier** : données Open Data de Nantes Métropole (débit, vitesse, taux d’occupation, pas de 15 min).
- **Météo** : API Open-Meteo (température, pluie, vent, humidité).
- **Événements** : OpenAgenda (événements géolocalisés et horodatés).
- **Pollution** : indice ATMO journalier via API de Nantes Métropole.
- **Calendrier scolaire** : via l’API du ministère de l’Éducation nationale.

### 🔄 Intégration des données

- **Historique (ETL)** : données météo, pollution, événements nettoyées et structurées avant chargement.
- **Temps réel (ELT)** : données de trafic chargées rapidement puis transformées via scripts Python.

### 🔐 Stockage & Sécurité

Toutes les données sont stockées sur Azure dans un environnement collaboratif et sécurisé. Seules des données ouvertes et non sensibles sont manipulées.

## 📊 Modélisation

Le modèle relationnel est centré sur la table `trafic_routier`, liée aux données météo, pollution, événements et calendrier.

### 🔍 Analyse exploratoire et nettoyage

- Suppression des observations avec valeurs manquantes ou classe cible "indéterminé".
- Standardisation temporelle (tranches de 15 minutes).
- Interpolation des variables continues ; imputation des variables dynamiques via Random Forest.
- Saisonnalité confirmée, justifiant l’usage de modèles temporels.

## 🧠 Modèles testés

### 🔹 Prédiction de l'état du trafic (XGBoost)

- Variables : météo, pollution, jour, événement, cluster temporel, etc.
- Rééquilibrage via pondération inverse.
- F1-scores faibles (~0.28), malgré plusieurs ajustements.

### 🔹 Prédiction de la vitesse (LSTM)

- **Univarié** : sensible aux pics extrêmes.
- **Multivarié** : plus stable grâce à des features temporelles.
- Résultats optimaux pour vitesses ≤ 50 km/h (MAE = 1.27 km/h, RMSE = 2.09).

### 🔹 Prédiction du taux d’occupation

- **Prophet** : bonne saisonnalité, sous-estimation des pics (MAE = 2.2).
- **SARIMAX** : résultats faibles, prédictions quasi constantes.
- **LSTM** : moyenne, tendance à lisser les pics (MAE = 0.26).

### 🔹 Prédiction du temps de parcours (LSTM)

- Très bon sur conditions normales (MAE = 0.11).
- Inefficace sur incidents (RMSE = 0.84), erreurs importantes sur les cas rares.

# 🤖 Solution Retenue : Double Modèle LSTM

Notre solution repose sur une architecture en cascade avec deux modèles **LSTM** pour prédire l'état du trafic. Cette approche décompose le problème pour plus de précision.

### Étape 1 : LSTM pour le Taux d'Occupation

Un premier LSTM est entraîné pour prédire la valeur future du **taux d'occupation**.

- **Input** : Séquences temporelles du taux d'occupation historique + variables externes (météo, trafic, calendrier).
- **Output** : La valeur prédite du taux d'occupation.
- **Objectif** : Modéliser la dynamique temporelle.

### Étape 2 : LSTM pour le Code de Circulation (etat_du_trafic)

Un second LSTM utilise cette prédiction pour classifier l'état final du trafic.

- **Input** :
    - **Taux d'occupation prédit** (par le modèle 1).
    - **Variables exogènes** (heure, jour, météo, événements, etc.).
- **Output** : Le code de circulation final (Fluide / Non-Fluide).
- **Objectif** : Contextualiser la prédiction de densité.

## 🚀 Pistes d'amélioration

- Étendre la période de collecte à une année complète.
- Repenser la classification : modèle binaire "fluide/non-fluide", suivi d’une classification fine.
- Explorer des modèles spatio-temporels hybrides (ex : CNN-LSTM).
- Intégrer d’autres sources (accidents, travaux).
- Développer un service de prédiction d’itinéraires personnalisés en fonction des conditions futures.

## 👥 Auteurs

- Lisa Smah  
- Arezki Ben Oussaïd  
- Emmanuelle Le Gal
