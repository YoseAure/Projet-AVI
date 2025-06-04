from perfo import *
import unittest

takeoff=FlightPhase(1,1,1,[0,13],decollage_vTable,decollage_vTargetsTable,decollage_nxTable,decollage_nzTable,decollage_fpaTargetsTable,decollage_roll_Table,decollage_roll_RateTable)
initclimb=FlightPhase(1,1,1,[14,5000],montée_initiale_vTable,montée_initiale_vTargetsTable,montée_initiale_nxTable,montée_initiale_nzTable,montée_initiale_fpaTable,montée_initiale_rollTable,montée_initiale_roll_RateTable)
climbdesc=FlightPhase(0,0,0,[5001,24000],montée_descente_vTable,montée_descente_vTargetsTable,montée_descente_nxTable,montée_descente_nzTable,montée_descente_fpaTable,montée_descente_rollTable,montée_descente_rollrateTable)
cruise=FlightPhase(0,0,0,[24001,41000],croisiere_vTable,croisiere_vTargetsTable,croisiere_nxTable,croisiere_nzTable,croisiere_fpaTable,croisiere_rollTable,croisiere_rollrateTable)
approach=FlightPhase(-1,1,1,[4999,0],approche_vTable,approche_vTargetsTable,approche_nxTable,approche_nzTable,approche_fpaTable,approche_rollTable,approche_roll_RateTable)
        
class TestPerfo(unittest.TestCase):
    def setUp(self):
        flightEnvelope = FlightEnvelope(
            {
                (0, 13): takeoff,
                (14, 5000): initclimb,
                (5001, 24000): climbdesc,
                (24001, 41000): cruise,
                (4999, 0): approach
            }
        )
        self.perfo = Perfo(flightEnvelope)

    def test_setFlightPhase(self):
        self.perfo.setFlightPhase(0,12)
        self.assertEqual(self.perfo.flightPhase, takeoff)
        
        self.perfo.setFlightPhase(0,2500)
        self.assertEqual(self.perfo.flightPhase, initclimb)
        
        self.perfo.setFlightPhase(0,15000)
        self.assertEqual(self.perfo.flightPhase, climbdesc)
        
        self.perfo.setFlightPhase(0,33000)
        self.assertEqual(self.perfo.flightPhase, cruise)
        
        self.perfo.setFlightPhase(4999,4000)
        self.assertEqual(self.perfo.flightPhase, approach)
        
        self.perfo.setFlightPhase(2000,3000)
        self.assertEqual(self.perfo.flightPhase, initclimb)
        
        self.perfo.setFlightPhase(0,100000)
        self.assertEqual(self.perfo.flightPhase, None)
        
        self.perfo.setFlightPhase(0,-100000)
        self.assertEqual(self.perfo.flightPhase, None)
            
    def test_setPerfo(self):
        mock_flight_phase_data = {
            1: {
                "LG_IN": {
                    "PA_ON": [1, 2, 3],
                },
                "LG_OUT": {
                    "PA_ON": [4, 5, 6],
                },
            },
            0: {
                "LG_IN": {
                    "PA_ON": [7, 8, 9],
                },
            },
        }
        
        #Set flightPhase to a random one just to initialize it
        self.perfo.flightPhase = takeoff
        
        # Set the mocked data to the vTable and others in the flightPhase
        self.perfo.flightPhase.vTable = mock_flight_phase_data
        self.perfo.flightPhase.vTargets = mock_flight_phase_data
        self.perfo.flightPhase.nxTable = mock_flight_phase_data
        self.perfo.flightPhase.nzTable = mock_flight_phase_data
        self.perfo.flightPhase.fpaTable = mock_flight_phase_data
        self.perfo.flightPhase.rollTable = mock_flight_phase_data
        self.perfo.flightPhase.rollRateTable = mock_flight_phase_data

        self.perfo.flightPhase.canConfigureFlaps = True
        self.perfo.flightPhase.canConfigureLandingGear = True

        # Call the method to test
        volets = 1
        trains = True
        ap = "on"
        self.perfo.setPerfo(volets, trains, ap)

        # Check the values
        self.assertEqual(self.perfo.vTable, [1, 2, 3])
        self.assertEqual(self.perfo.vTargets, [1, 2, 3])
        self.assertEqual(self.perfo.nxTable, [1, 2, 3])
        self.assertEqual(self.perfo.nzTable, [1, 2, 3])
        self.assertEqual(self.perfo.fpaTable, [1, 2, 3])
        self.assertEqual(self.perfo.rollTable, [1, 2, 3])
        self.assertEqual(self.perfo.rollRateTable, [1, 2, 3])
        
        # Set canConfigureFlaps and canConfigureLandingGear to False
        self.perfo.flightPhase.canConfigureFlaps = False
        self.perfo.flightPhase.canConfigureLandingGear = False

        # Call the method to test again
        self.perfo.setPerfo(volets, trains, ap)

        # Check the values
        self.assertEqual(self.perfo.vTable, [7, 8, 9])
        self.assertEqual(self.perfo.vTargets, [7, 8, 9])
        self.assertEqual(self.perfo.nxTable, [7, 8, 9])
        self.assertEqual(self.perfo.nzTable, [7, 8, 9])
        self.assertEqual(self.perfo.fpaTable, [7, 8, 9])
        self.assertEqual(self.perfo.rollTable, [7, 8, 9])
        self.assertEqual(self.perfo.rollRateTable, [7, 8, 9])


        



