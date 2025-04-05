from shapely.geometry import Point, LineString


def convert_to_linestring(geometry_str):
    '''
    Convertir une chaine en LineString
    '''
    try:
        # Supprimer les accolades externes et diviser les paires de coordonnées
        geometry_str = geometry_str.strip('{}')
        
        # Séparer les paires de coordonnées
        coords = geometry_str.split('},{')
        
        # Convertir chaque coordonnée en tuple de float
        coord_list = [tuple(map(float, coord.split(','))) for coord in coords]
        
        # Créer un LineString avec la liste de coordonnées
        return LineString(coord_list)
    except Exception as e:
        print(f"Erreur lors de la conversion : {e}")
        return None




def has_close_event(trafic, evenement, seuil=500):
    '''
    Calcul la distance entre un lieu d'evennt et un tronçon de route
    '''
    distance = trafic.distance(evenement)
    return distance <= seuil / 1000  # Convertir en kilomètres (500m = 0.5km)