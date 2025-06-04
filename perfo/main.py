from perfo import *
from perfo_test import *
from ivyserver import Server, PerfoMessageInterpreter
import unittest
import sys
import time
import multiprocessing
import os

def testsuite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerfo)
    runner = unittest.TextTestRunner(stream=open(os.devnull, 'w'))
    # runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result

def main(perfo,IvyServerPerfo,IvyProcess):
    try:
        inputs = None
        prev_inputs = None
        current_FlightParameter = FlightParameter()
        previous_FlightParameter = FlightParameter()
        
        #checking that the first inputs from ivy contain all the mandatory inputs to initialize FlightParameter
        missing_keys = []
        prev_missing_keys = []
        keys_to_check = ["FCUVertical", "Volets", "Trains", "AP"]

        while True:
            time.sleep(0.1)
            inputs = IvyServerPerfo.stored_values
            if inputs is not None and inputs != prev_inputs:
                missing_keys = [key for key in keys_to_check if key not in inputs]
                if missing_keys != prev_missing_keys and len(missing_keys) > 0:
                    print("Missing keys:", missing_keys)
                    prev_missing_keys = missing_keys.copy() #print missing keys only when there's an update
                if not missing_keys :
                    prev_inputs = inputs.copy()
                    previous_FlightParameter = current_FlightParameter
                    current_FlightParameter = FlightParameter(int(inputs["FCUVertical"]), int(inputs["Volets"]),int(inputs["Trains"]), inputs["AP"])
                    perfo.setFlightPhase(previous_FlightParameter.altitude,current_FlightParameter.altitude)
                    perfo.setPerfo(current_FlightParameter.flaps,current_FlightParameter.landing_gear,current_FlightParameter.autopilot)
                    message = (
                        "Perfo" +
                        " ViManage=" + str(perfo.vTargets[0]) +
                        " ViMin=" + str(perfo.vTable[0]) +
                        " ViMax=" + str(perfo.vTable[1]) +
                        " nxMin=" + str(perfo.nxTable[0]) +
                        " nxMax=" + str(perfo.nxTable[1]) +
                        " nzMin=" + str(perfo.nzTable[0]) +
                        " nzMax=" + str(perfo.nzTable[1]) +
                        " fpaMin=" + str(perfo.fpaTable[0]) +
                        " fpaMax=" + str(perfo.fpaTable[1]) +
                        " roulisMax=" + str(perfo.rollTable[0]) +
                        " rollrateMax=" + str(perfo.rollRateTable[0])
                    )
                    IvyServerPerfo.send_message(message)
                    print(message)

    except KeyboardInterrupt:
        print("Keyboard interrupt. Stopping the program.")
        cleanup(IvyServerPerfo,IvyProcess)
        sys.exit(0)

    except Exception as e:
        print("Exception occurred:", e)
        cleanup(IvyServerPerfo,IvyProcess)
        sys.exit(0)


def cleanup(IvyServer,IvyProcess):
    IvyServer.stop()
    IvyProcess.kill 

if __name__ == '__main__':
    
    takeoff=FlightPhase(1,1,1,[0,13],decollage_vTable,decollage_vTargetsTable,decollage_nxTable,decollage_nzTable,decollage_fpaTargetsTable,decollage_roll_Table,decollage_roll_RateTable)
    initclimb=FlightPhase(1,1,1,[14,5000],montée_initiale_vTable,montée_initiale_vTargetsTable,montée_initiale_nxTable,montée_initiale_nzTable,montée_initiale_fpaTable,montée_initiale_rollTable,montée_initiale_roll_RateTable)
    climbdesc=FlightPhase(0,0,0,[5001,24000],montée_descente_vTable,montée_descente_vTargetsTable,montée_descente_nxTable,montée_descente_nzTable,montée_descente_fpaTable,montée_descente_rollTable,montée_descente_rollrateTable)
    cruise=FlightPhase(0,0,0,[24001,41000],croisiere_vTable,croisiere_vTargetsTable,croisiere_nxTable,croisiere_nzTable,croisiere_fpaTable,croisiere_rollTable,croisiere_rollrateTable)
    approach=FlightPhase(-1,1,1,[4999,0],approche_vTable,approche_vTargetsTable,approche_nxTable,approche_nzTable,approche_fpaTable,approche_rollTable,approche_roll_RateTable)
    
    flightEnvelope = FlightEnvelope(
        {
            (0, 13): takeoff,
            (14, 5000): initclimb,
            (5001, 24000): climbdesc,
            (24001, 41000): cruise,
            (4999, 0): approach
        }
    )
    
    regex_to_extract = {
        "Volets": r"Volets=(\d+)",
        "Trains": r"Trains=(\d+)",
        "x": r"x=(\d+)",
        "y": r"y=(\d+)",
        "z": r"z=(\d+)",
        "Vp": r"Vp=(\d+)",
        "fpa": r"fpa=(\d+)",
        "psi": r"psi=(\d+)",
        "phi": r"phi=(\d+)",
        "FCUVertical": r"Altitude=(\d+)",
        "AP": r"(on|off)"
    }
    
    perfo = Perfo(flightEnvelope)
    perfo_interpreter = PerfoMessageInterpreter()
    IvyServerPerfo = Server("Perfo", "127.255.255.255:2047", ["^IHM : (.*)", "^StateVector (.*)", "FCUVertical (.*)", "FCUAP1 (.*)"], regex_to_extract, perfo_interpreter)

    result = testsuite()
    if not result.errors and not result.failures:
        IvyServerPerfo.run()
        IvyProcess = multiprocessing.Process(target=IvyServerPerfo.start_loop)
        main(perfo,IvyServerPerfo,IvyProcess)
    else:
        print(result)
    

