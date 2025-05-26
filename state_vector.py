from ivy.std_api import *
import time


IvyInit("StateVectorSender", "State Vector Sender Ready", 0, None, None) 
IvyStart("224.255.255.255:2045")

def send_state_vector():
    x, y, z = 0, 0, 10000.0 
    Vp = 250.0  
    fpa = 0 
    psi = 90.0
    phi = 0  

    message = f"StateVector x={x} y={y} z={z} Vp={Vp} fpa={fpa} psi={psi} phi={phi}"
    print(f"Envoi : {message}")

    IvySendMsg(message)

try:
    while True:
        send_state_vector()
        time.sleep(1)
except KeyboardInterrupt:
    print("Arrêt par l'utilisateur")
finally:
    IvyStop()

