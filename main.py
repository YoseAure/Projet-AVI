# Commande dans le terminal pour lancer le script = ./aircraft-sim-darwin-10.10-amd64 -bus 10.1.127.255:2049
from ivy.std_api import *
from lecture_plan import read_waypoints, generate_fplwpts_string,generate_z_consigne
FCU_On = False
Mode_PA_Longitudinale = "Managed"

waypoints = read_waypoints("fpl.txt")
fplwpts_string = generate_fplwpts_string(waypoints)

vitesse_consigne = 250.0 # Vitesse de consigne en nœuds
altitude_consigne = generate_z_consigne(waypoints) # Altitude de consigne en pieds

def on_Push(agent, *larg):   #*larg = tableau qui contient les argument éventuels de notre message
    global FCU_On

    print("Msg with arg {} received".format(larg[0]))
    if FCU_On == False:
        FCU_On = True
        IvySendMsg("FCUAP1 on")

    else:
        FCU_On = False
        IvySendMsg("FCUAP1 off")
        
    print("Message recu du FCU")
    IvySendMsg(f"FplWpts Waypoints={fplwpts_string}") # Afficher le plan de vol

#------------Mini Manche------------------

    #ANGLE DE ROULIS PHHI
    IvySendMsg("FGS_PHI_MAX_MANCHE=66.0")

    #FACTEUR DE CHARGE N
    IvySendMsg("FGS_N_MAX_MANCHE=2.5")
    IvySendMsg("FGS_N_MIN_MANCHE=-1.5")

    #VITESSE DE ROULIS P
    IvySendMsg("FGS_P_MAX_MANCHE=15.0")

#------------PA LONGITUDINAL---------------

    #PHI
    IvySendMsg("FGS_PHI_MAX=33.0")
    IvySendMsg("FGS_PHI_MIN=-33.0")

    #VITESSE DE CONSIGNE
    IvySendMsg(f"FGS_V_CONSIGNE={vitesse_consigne}")

    #ALTITUDE DE CONSIGNE
    IvySendMsg(f"FGS_Z_CONSIGNE={altitude_consigne}")  

#------------------------------------------

def on_FCUVertical(agent, *larg):
    global Mode_PA_Longitudinal

    print("larg[1] = {}".format(larg[1]))
    Mode_PA_Longitudinal = larg[1]
    print("Mode_PA_Longitudinal = {}".format(Mode_PA_Longitudinal))

    alt = float(larg[0])
    print("Altitude + 5 = {}".format(alt + 5)) 


null_cb = lambda *a: None
IvyInit("testPushbutton", "Ready",0,null_cb,null_cb)
IvyBindMsg(on_Push,r'^FCUAP1 push')  # On s'abonne au message FCU_On
IvyBindMsg(on_FCUVertical, r'^FCUVertical Altitude = (\S+) Mode = (\S+) Val = (\S+)')  
IvyStart("10.1.127.255:2049")    # On se connecte
IvyMainLoop()