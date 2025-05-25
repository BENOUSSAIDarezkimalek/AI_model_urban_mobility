# AI_model_urban_mobility
Projet étude M2

📅 Préparation des Données :
Index temporel : heure_arrondie
Séparation Train/Test temporelle stricte. 
Période totale : du 16/02 au 14/03 → soit 27 jours.
80% Train : 16/02 au 07/03 inclus (22 jours).
20% Test : 08/03 au 14/03 inclus (5 jours).


🔍 Classification de l’état du trafic avec RandomForestClassifier
Cette section détaille trois variantes testées du modèle RandomForestClassifier pour la classification de la variable etat_du_trafic (Fluide, Dense, Saturé, Bloqué). 

1️⃣ Modèle de base : RandomForestClassifier
Configuration : modèle standard sans équilibrage de classes.

Observation : Le modèle atteint une accuracy globale de 97%, mais cette performance est largement due à la dominance de la classe Fluide (~97% des données).

Inconvénient : les classes rares (Bloqué, Dense, Saturé) sont très mal prédites.

Résultats :
(C:/Users/lisas/Downloads/Capture d'écran 2025-05-24 202408.png)


2️⃣ Modèle avec class_weight="balanced"
Configuration : RandomForestClassifier avec class_weight="balanced" pour compenser le déséquilibre des classes.

Observation : Légère amélioration du recall sur les classes rares, mais les performances globales restent faibles pour ces classes. Fluide reste toujours prédite de façon dominante.

Résultats :

(C:/Users/lisas/Downloads/Capture d'écran 2025-05-24 202837.png)

3️⃣ Modèle avec sur-échantillonnage (SMOTE)
Technique : Application de SMOTE (Synthetic Minority Over-sampling Technique) pour générer artificiellement des échantillons synthétiques des classes minoritaires avant entraînement.

Résultat : Les classes Bloqué, Dense, et Saturé sont mieux représentées, mais la qualité des prédictions reste modeste.

Limite : SMOTE crée des points interpolés qui peuvent ne pas refléter des cas réels, ce qui peut introduire du bruit.

Distribution après SMOTE : équilibrée à 1 275 632 échantillons par classe.

Résultats :

(C:/Users/lisas/Downloads/Capture d'écran 2025-05-24 203032.png)

✅ Conclusion
Le RandomForestClassifier montre une forte précision sur la classe majoritaire (Fluide), mais échoue à bien modéliser les classes rares, même avec des techniques d’équilibrage (class_weight, SMOTE). Ces résultats soulignent l’importance :

de tester d’autres modèles


