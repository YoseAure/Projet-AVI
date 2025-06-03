# Commande dans le terminal pour lancer le script = ./aircraft-sim-darwin-10.10-amd64 -bus 10.1.127.255:2049
from ivy.std_api import *
from lecture_plan import read_waypoints, generate_fplwpts_string,generate_z_consigne, generate_legs_strings, generate_leg_from_position

# =================== INITIALISATION ==========================
FCU_On = False
Mode_PA_Longitudinal = "Managed"

waypoints = read_waypoints("fpl.txt")
fplwpts_string = generate_fplwpts_string(waypoints)
altitude_consigne = generate_z_consigne(waypoints) #pieds
vitesse_consigne = 250.0  # nœuds
legs = generate_legs_strings(waypoints)
current_leg_index = 0

# ================== CALLBACKS =======================
def on_Push(agent, *larg):
    global FCU_On, navigation_active
    print("Msg with arg {}received".format(larg[0]))
    if FCU_On == False:
        FCU_On = True
        navigation_active = True
        IvySendMsg("FCUAP1 on")
        print("[FCU] AP1 activé")
        
        # Affichage du plan de vol sur la simulation
        IvySendMsg(f"FplWpts Waypoints={fplwpts_string}")
        print(f"[FPL] Plan de vol envoyé : {len(waypoints)} waypoints")
        
        # Paramètres de performances
        send_performance_parameters()

        # Envoi du premier leg
        send_current_leg()
    else:
        FCU_On = False
        navigation_active = False
        IvySendMsg("FCUAP1 off")
        print("[FCU] AP1 désactivé")

def send_performance_parameters():
    performance_params = {
        "FGS_PHI_MANCHE": 66.0,
        "FGS_NZ_MAX_MANCHE": 2.5,
        "FGS_NZ_MIN_MANCHE": -1.5,
        "FGS_P_MANCHE": 15.0,
        "FGS_NZ_MAX": 1.5,
        "FGS_NZ_MIN": 0.5,
        "FGS_NX_MAX": 0.3,
        "FGS_NX_MIN": 0.0,
        "FGS_PHI_MAX": 33.0,
        "FGS_PHI_MIN": -33.0,
        "FGS_V_CONSIGNE": vitesse_consigne,
        "FGS_Z_CONSIGNE": altitude_consigne
    }
    for param, value in performance_params.items():
        IvySendMsg(f"{param}={value}")
    print("[FGS] Paramètres de performance envoyés")

def send_current_leg():
    global current_leg_index
    if current_leg_index < len(legs):
        leg = legs[current_leg_index]
        wp1, wp2 = leg.split(";")
        msg = f"FGSLateral Mode=Axis WP1={wp1};WP2={wp2}"
        IvySendMsg(msg)
        print(f"[FGS] Envoi leg {current_leg_index+1}: {msg}")
    else:
        print("[FGS] Tous les legs ont été envoyés.")

def on_request_next_leg(agent, *larg):
    global current_leg_index
    if current_leg_index + 1 < len(legs):
        current_leg_index += 1
        send_current_leg()
    else:
        print("[FGS] Dernier leg atteint. Aucun leg suivant.")

def on_FCUVertical(agent, *larg):
    global Mode_PA_Longitudinal
    print("larg[1] = {}".format(larg[1]))
    Mode_PA_Longitudinal = larg[1]
    print("Mode_PA_Longitudinal = {}".format(Mode_PA_Longitudinal))
    alt = float(larg[0])
    print("Altitude + 5 = {}".format(alt + 5)) 

def on_aircraft_position(agent, *larg):
    try:
        x_avion = float(larg[0])
        y_avion = float(larg[1])
        idx, leg_msg = generate_leg_from_position(x_avion, y_avion, waypoints)
        if leg_msg:
            IvySendMsg(leg_msg)
            print(f"[NAV] Position avion ({x_avion:.1f}, {y_avion:.1f}) → Envoi leg {idx+1}: {leg_msg}")
        else:
            print("[NAV] Aucun leg actif trouvé pour cette position.")
    except Exception as e:
        print(f"[ERROR] Erreur dans on_aircraft_position : {e}")

# ================ IVY SETUP ========================
IvyInit("testPushbutton", "Ready", 0, lambda *a: None, lambda *a: None)
IvyBindMsg(on_Push, r'^FCUAP1 push')
IvyBindMsg(on_FCUVertical, r'^FCUVertical Altitude = (\S+) Mode = (\S+) Val = (\S+)')

IvyBindMsg(on_aircraft_position, r'^StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)')

IvyBindMsg(on_request_next_leg, r'^SendNextLeg')  # Pour avancer manuellement dans les legs
IvyStart("10.1.127.255:2049")
IvyMainLoop()