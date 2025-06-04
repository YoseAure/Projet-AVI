from flightenvelope import *

class FlightParameter:
    def __init__(self, altitude=0, flaps=0, landing_gear=0, autopilot=""):
        self.altitude = altitude
        self.flaps = flaps
        self.landing_gear = landing_gear
        self.autopilot = autopilot

class Perfo:
    def __init__(self,flightEnvelope):
        self.flightEnvelope = flightEnvelope
        self.flightPhase = None
        self.vTable=None
        self.vTargets=None
        self.nxTable=None
        self.nzTable=None
        self.fpaTable=None
        self.rollTable=None
        self.rollRateTable=None
        
    def setFlightPhase(self,previousAltitude,currentAltitude):
        self.flightPhase = self.flightEnvelope.getFlightPhase(previousAltitude,currentAltitude)
        
    def setPerfo(self,volets,trains,ap):
        if self.flightPhase is None:
            return "Fatal Error : No current limitation table found. Unable to setPerfo."
        
        trains = "LG_IN" if trains else "LG_OUT"
        ap = "PA_ON" if ap =="on" else "PA_OFF"

        if self.flightPhase.canConfigureFlaps and self.flightPhase.canConfigureLandingGear :
            self.vTable = self.flightPhase.vTable[volets][trains][ap]
            self.vTargets = self.flightPhase.vTargets[volets][trains][ap]
            self.nxTable = self.flightPhase.nxTable[volets][trains][ap]
            self.nzTable = self.flightPhase.nzTable[volets][trains][ap]
            self.fpaTable = self.flightPhase.fpaTable[volets][trains][ap]
            self.rollTable = self.flightPhase.rollTable[volets][trains][ap]
            self.rollRateTable = self.flightPhase.rollRateTable[volets][trains][ap]
            
        else :
            self.vTable = self.flightPhase.vTable[0]["LG_IN"][ap]
            self.vTargets = self.flightPhase.vTargets[0]["LG_IN"][ap]
            self.nxTable = self.flightPhase.nxTable[0]["LG_IN"][ap]
            self.nzTable = self.flightPhase.nzTable[0]["LG_IN"][ap]
            self.fpaTable = self.flightPhase.fpaTable[0]["LG_IN"][ap]
            self.rollTable = self.flightPhase.rollTable[0]["LG_IN"][ap]
            self.rollRateTable = self.flightPhase.rollRateTable[0]["LG_IN"][ap]

    def showTables(self):
        print("self.vTable : ",self.vTable)
        print("self.vTargets : ",self.vTargets)
        print("self.nxTable : ",self.nxTable)
        print("self.nzTable : ",self.nzTable)
        print("self.fpaTable : ",self.fpaTable)
        print("self.rollTable : ",self.rollTable)
        print("self.rollRateTable : ",self.rollRateTable)

        
    




