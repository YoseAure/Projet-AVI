# Commande dans le terminal pour lancer le script = ./aircraft-sim-darwin-10.10-amd64 -bus 10.1.127.255:2049
from ivy.std_api import *
from lecture_plan import read_waypoints, generate_fplwpts_string
FCU_On = False
Mode_PA_Longitudinale = "Managed"

waypoints = read_waypoints("fpl.txt")
fplwpts_string = generate_fplwpts_string(waypoints)

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
    IvySendMsg(f"FplWpts Waypoints={fplwpts_string}") # Envoi d'un message de type FplWpts

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