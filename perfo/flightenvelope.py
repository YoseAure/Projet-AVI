from perfovalues import *

class FlightPhase:
    def __init__(self, flightPhaseType, canConfigureFlaps, canConfigureLandingGear, altitudeRange, vTable, vTargets, nxTable, nzTable, fpaTable, rollTable, rollRateTable):
        self.flightPhaseType=flightPhaseType # 1 : climb - 0 : cruize - -1 : descent
        self.canConfigureFlaps=canConfigureFlaps
        self.canConfigureLandingGear=canConfigureLandingGear
        self.altitudeRanges=altitudeRange
        self.vTable=vTable
        self.vTargets=vTargets
        self.nxTable=nxTable
        self.nzTable=nzTable
        self.fpaTable=fpaTable
        self.rollTable=rollTable
        self.rollRateTable=rollRateTable

class FlightEnvelope:
    def __init__(self, flightPhases):
        self.flightPhases = flightPhases
        
    def getMatchingFlightPhases(self,currentAltiude):
        altitudeRanges = ()
        for key in self.flightPhases:
            if key[0] <= currentAltiude <= key[1] or key[0] >= currentAltiude >= key[1]:
                altitudeRanges += (key,)
        return altitudeRanges
        
    def getFlightPhase(self,previousAltitude,currentAltiude):
        altitudeRanges = self.getMatchingFlightPhases(currentAltiude)
        if len(altitudeRanges) == 1:
            if self.flightPhases[altitudeRanges[0]].flightPhaseType == self.getflightPhaseType(previousAltitude,currentAltiude):
                return self.flightPhases[altitudeRanges[0]]
        elif len(altitudeRanges) == 2:
            for altitudeRange in altitudeRanges:
                if self.flightPhases[altitudeRange].flightPhaseType == self.getflightPhaseType(previousAltitude,currentAltiude):
                    return self.flightPhases[altitudeRange] 
        return None
    
    def getflightPhaseType(self,previousAltitude,currentAltiude):
        if 5001 <= currentAltiude <= 24000: return 0 #croisière
        elif 24001 <= currentAltiude <= 41000: return 0 #croisière
        elif currentAltiude > previousAltitude :return 1 #montée
        elif currentAltiude < previousAltitude :return -1 #descente
        
        

