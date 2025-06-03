import math
from ivy.std_api import *

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

"""def generate_legs(waypoints): 
    legs = []
    for i in range(len(waypoints) - 1):
        leg = (waypoints[i], waypoints[i+1])
        legs.append(leg)
    return legs"""

def generate_legs_strings(waypoints):
    legs_strings = []
    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i + 1]
        leg = f"{wp1['x']},{wp1['y']};{wp2['x']},{wp2['y']}"
        legs_strings.append(leg)
    return legs_strings

def generate_z_consigne(waypoints):
    z_consigne = []
    for wp in waypoints:
        if wp['z'] == -1: # Altitude non définie
            z_consigne.append(None)
        else:
            # Nouvelle consigne d'altitude
            z_consigne.append(wp['z'])
    return z_consigne

def distance_point_to_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == dy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)

def find_active_leg(aircraft_x, aircraft_y, waypoints):
    min_distance = float('inf')
    selected_leg = None
    selected_index = -1
    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i + 1]
        dist = distance_point_to_segment(aircraft_x, aircraft_y, wp1["x"], wp1["y"], wp2["x"], wp2["y"])
        if dist < min_distance:
            min_distance = dist
            selected_leg = (wp1, wp2)
            selected_index = i
    return selected_index, selected_leg

def generate_leg_from_position(x, y, waypoints):
    idx, leg = find_active_leg(x, y, waypoints)
    if leg is None:
        return None, None
    wp1, wp2 = leg
    mode = "FlyOver" if wp1["overfly"].lower() == "true" else "FlyBy"
    wp1_str = f"{wp1['x']},{wp1['y']}"
    wp2_str = f"{wp2['x']},{wp2['y']}"
    msg = f"FGSLateral Mode={mode} WP1={wp1_str};WP2={wp2_str}"
    return idx, msg

#============================================================

if __name__ == "__main__":
    # Utiliser le nom de fichier 'fpl.txt'
    waypoints = read_waypoints('fpl.txt')
    
    """# Afficher les coordonnées des waypoints
    coordinates = []
    for wp in waypoints:
        # Créer un tuple avec toutes les informations du waypoint
        coordinates.append((wp['name'],wp['x'], wp['y'], wp['z'], wp['overfly']))
    print("Liste des coordonnées :")
    for coord in coordinates:
        print(coord)
    
     # Générer les legs et les afficher
    legs = generate_legs(waypoints) 
    for idx, (start, end) in enumerate(legs, 1):
        print(f"\nLeg {idx}:")  # Format : name,x,y,z,overfly
        print(f"{start['name']},{start['x']},{start['y']},{start['z']},{start['overfly']}") # Waypoint de départ
        print(f"{end['name']},{end['x']},{end['y']},{end['z']},{end['overfly']}") # Waypoint d'arrivée"""
    
    """fplwpts_string = generate_fplwpts_string(waypoints)
    print("\n=== Plan de vol ===")
    print(fplwpts_string)"""

    """z_consigne = generate_z_consigne(waypoints)
    print("\n=== Altitudes de consigne ===")
    print("|".join(str(z) for z in z_consigne))"""
    
    """legs_strings = generate_legs_strings(waypoints)
    print("\n=== Legs formatés ===")
    for idx, leg_str in enumerate(legs_strings, 1):
        print(f"{leg_str}")"""


#=========Test de la fonction generate_leg_from_position avec position avion========
test_xAvion = -4000
test_yAvion = 15000
idx, leg_msg = generate_leg_from_position(test_xAvion, test_yAvion, waypoints)

print("\n=== TEST generate_leg_from_position ===")
print(f"Position avion : ({test_xAvion}, {test_yAvion})")
if leg_msg:
    print(f"Leg actif : {idx+1}")
    print(f"Message FGSLateral : {leg_msg}")
else:
    print("Aucun leg actif trouvé.")
