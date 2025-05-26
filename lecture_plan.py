def read_waypoints(filename):
    waypoints = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.strip():  # Vérifier que la ligne n'est pas vide
                    parts = line.strip().split()
                    if len(parts) == 5:  # Vérifier qu'il y a bien 5 éléments
                        name, x, y, z, overfly = parts
                        waypoint = {
                            'name': name,
                            'x': int(x),
                            'y': int(y),
                            'z': int(z),
                            'overfly': overfly
                        }
                        waypoints.append(waypoint)
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{filename}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
    
    return waypoints

def generate_fplwpts_string(waypoints):
    parts = []
    for wp in waypoints:
        part = f"{wp['name']};{wp['x']};{wp['y']};{wp['z']}"
        parts.append(part)
    return  "|".join(parts)

def generate_legs(waypoints): #générer les legs
    legs = []
    for i in range(len(waypoints) - 1):
        leg = (waypoints[i], waypoints[i+1])
        legs.append(leg)
    return legs

def generate_legs_strings(waypoints):  # générer les legs au format chaîne demandée
    legs_strings = []
    for i in range(len(waypoints) - 1):
        wp_start = waypoints[i]
        wp_end = waypoints[i + 1]
        start_str = f"{wp_start['name']};{wp_start['x']};{wp_start['y']};{wp_start['z']};{wp_start['overfly']}"
        end_str = f"{wp_end['name']};{wp_end['x']};{wp_end['y']};{wp_end['z']};{wp_end['overfly']}"
        leg_str = f'"{start_str}|{end_str}"'
        legs_strings.append(leg_str)
    return legs_strings

def generate_z_consigne(waypoints) :
    """
    Génère une liste des altitudes de consigne à partir des waypoints.
    """
    z_consigne = []
    for wp in waypoints:
        z_consigne.append(wp['z'])
    return z_consigne

if __name__ == "__main__":
    # Utiliser le nom de fichier 'fpl.txt'
    waypoints = read_waypoints('fpl.txt')
    
    """# Afficher le résultat
    print(f"\nNombre de waypoints lus : {len(waypoints)}\n")
    
    coordinates = []
    for wp in waypoints:
        # Créer un tuple avec toutes les informations du waypoint
        coordinates.append((wp['name'],wp['x'], wp['y'], wp['z'], wp['overfly']))
    
    print("Liste des coordonnées :")
    for coord in coordinates:
        print(coord)"""
    
    fplwpts_string = generate_fplwpts_string(waypoints)
    print("Plan de vol :")
    print(fplwpts_string)

    z_consigne = generate_z_consigne(waypoints)
    print("\nAltitudes de consigne:")
    print("|".join(str(z) for z in z_consigne))

    """legs = generate_legs(waypoints)
    for idx, (start, end) in enumerate(legs, 1):
        print(f"\nLeg {idx}:")  # Format : name,x,y,z,overfly
        print(f"{start['name']},{start['x']},{start['y']},{start['z']},{start['overfly']}") # Waypoint de départ
        print(f"{end['name']},{end['x']},{end['y']},{end['z']},{end['overfly']}") # Waypoint d'arrivée
    
    legs_strings = generate_legs_strings(waypoints)
    print("\nLegs formatés :")
    for idx, leg_str in enumerate(legs_strings, 1):
        print(f"Leg {idx}: {leg_str}")"""