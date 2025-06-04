from ivy.std_api import *
from tools import *
from waypoint import Waypoint
from leg import Leg
import config




def angle(x_start, y_start, x_intermediate, y_intermediate, x_arrival, y_arrival):
    """
    Compute the angle between two consecutive legs
    """
    v1 = (x_start - x_intermediate, y_start - y_intermediate)
    v2 = (x_arrival - x_intermediate, y_arrival - y_intermediate)
    norm_v1 = math.hypot(*v1)
    norm_v2 = math.hypot(*v2)
    scalar_product = v1[0] * v2[0] + v1[1] * v2[1]
    return math.acos(scalar_product / (norm_v1 * norm_v2))


def radius(legs, active_leg, x, y, ground_speed, phi_max):

    g = 9.80665
    if legs[active_leg].end.type == "flyby" and active_leg + 1 < len(legs):
        next_leg = legs[active_leg + 1]
        alpha = angle(x, y, next_leg.start.x, next_leg.start.y, next_leg.end.x, next_leg.end.y)
    else:
        return 2 * ground_speed

    if phi_max == 0 or alpha == 0:
        return 4630
    else:
        d = ground_speed ** 2 / (g * math.tan(alpha / 2) * math.tan(phi_max))
        return min(max(d, 2 * ground_speed), 4630)


# ============================ Lecture du plan de vol ===========================
def read_flightplan(filename):
    """
    Read flight plan from txt file "flight_plan.txt"
    line format : name x y z wpt_type
    units:
        x, y: m
        z: ft

    return: list of objects Waypoint
    """
    waypoints = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                name = str(parts[0])
                x = parts[1]          # m
                y = parts[2]          # m
                z = ft_to_m(int(parts[3])) # m
                wpt_type = parts[4]   # flyover / flyby
                waypoints.append(Waypoint(name, x, y, z, wpt_type))
    return waypoints

def format_fpl_message(waypoints):
    """
    Prepare and return ivy bus message with every waypoints from the flight plan
    """
    msg = "FplWpts Waypoints="
    segments = [f"{wpt.get_name()};{int(wpt.get_x())};{int(wpt.get_y())};{int(wpt.get_z())}" for wpt in waypoints]
    return msg + "|".join(segments)

def create_legs(waypoints):
    legs = []
    for i in range(len(waypoints) - 1):
        legs.append(Leg(waypoints[i], waypoints[i + 1]))
    return legs

# ========================= Callbacks de connexion Ivy =========================
def on_cx_proc(agent, connected):
    pass

def on_die_proc(agent, _id):
    pass

def on_time_1_msg(agent, *larg):
    """
    State vector initialisation on Time t=1.0
    """
    if float(larg[0]) == 1.0:
        IvySendMsg(f"FplWpts Waypoints={format_fpl_message(flightplan)[len('FplWpts Waypoints='):]}")
        IvySendMsg(f"InitStateVector x={x:.2f} y={y:.2f} z={z:.2f} Vp={Vp:.2f} fpa={fpa:.4f} psi={psi:.4f} phi={phi:.4f}")
        IvySendMsg(f"WindComponent VWind={v_wind:.2f} dirWind={psi_w:.4f}")
        IvySendMsg(f"MagneticDeclination={magnetic_declination:.4f}")
        print("Initilisation terminée")

def on_state_vector(agent, *args):
    """
    Send active leg
    """
    global active_leg_index, Vp, psi_w
    x_plane = float(args[0])
    y_plane = float(args[1])
    Vp = float(args[3])
    # phi = float(args[6])

    ground_speed = Vp * math.cos(psi_w)

    if active_leg_index < len(legs):
        leg = legs[active_leg_index]
        if leg.end.type == "flyover":
            # calcul côté de la perpendiculaire
            dx = leg.end.x - leg.start.x
            dy = leg.end.y - leg.start.y
            normal = (-dy, dx)
            vect_to_plane = (x_plane - leg.end.x, y_plane - leg.end.y)
            if (normal[0] * vect_to_plane[0] + normal[1] * vect_to_plane[1]) > 0:
                active_leg_index += 1
        else:  # flyby
            d = radius(legs, active_leg_index, leg.start.x, leg.start.y, ground_speed, phi_max) # phi_max à récupérer des perfos
            dist = distance(x_plane, y_plane, leg.end.x, leg.end.y)
            if dist < d:
                active_leg_index += 1

    if active_leg_index >= len(legs):
        active_leg_index = len(legs) - 1

    leg = legs[active_leg_index]
    msg = f"FGSLateralMode x1={int(leg.start.x)} x2={int(leg.end.x)} y1={int(leg.start.y)} y2={int(leg.end.y)}" #  h_contrainte={int(leg.end.z)}
    IvySendMsg(msg)
    print("Leg envoyé:", msg)

def on_dirto(agent, *args):
    """
    Callback function for DIRTO
    """
    global dirto_target, active_leg_index
    dirto_name = args[0]
    dirto_target = dirto_name

    # Rechercher dans le plan de vol le leg qui conrrespond à la consigne
    for i, leg in enumerate(legs):
        if leg.end.name == dirto_name:
            active_leg_index = i
            print(f"DIRTO vers {dirto_name}, leg {i} activé")
            return

    print(f"DIRTO reçu mais le waypoint est inconnu : {dirto_name}")

if __name__=='__main__':
    # ============================ Lecture du plan de vol ===========================
    flightplan = read_flightplan("flight_plan.txt")
    legs = create_legs(flightplan)
    active_leg_index = 0
    initial_wp = flightplan[0]
    dirto_target = None
    # ============================= Paramètres initiaux =============================
    magnetic_declination = math.radians(13.69) # rad
    v_wind = kt_to_mps(10) # m/s
    wind_dir = math.radians(20) % math.pi # rad

    phi_max = math.radians(33) # rad

    # Initialisation de l'avion à partir du 1er point du plan de vol
    x = initial_wp.get_x() # m
    y = initial_wp.get_y() # m
    z = initial_wp.get_z() if initial_wp.get_z() > 0 else ft_to_m(1000) # m
    Vp = kt_to_mps(250) # m/s
    fpa = math.radians(0) # rad
    phi = math.radians(0) # rad
    khi_geo = math.radians(14) # rad
    khi = khi_geo + magnetic_declination # rad
    psi_w = wind_dir + magnetic_declination # rad

    # Drift angle et cap
    try:
        drift_angle = math.asin((v_wind * math.sin(khi - psi_w)) / (Vp * math.cos(fpa)))
    except ValueError:
        drift_angle = 0  # pour éviter les erreurs numériques
    psi = khi - drift_angle
    # ============================= Initialisation Ivy =============================
    IvyInit(config.app_name, "[FGS ready]", 0, on_cx_proc, on_die_proc)
    IvyStart(config.local_adress)
    # ============================= Abonnement au temps ============================
    IvyBindMsg(on_time_1_msg, r'^Time t=(\S+)')
    IvyBindMsg(on_state_vector, r'^StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)')
    IvyBindMsg(on_dirto, r'^DIRTO (\S+)')
    # ================================= Boucle Ivy =================================
    IvyMainLoop()
    # ==============================================================================