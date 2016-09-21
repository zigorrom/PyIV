import visa
import time

class Keithley2430:
    def __init__(self,resource):
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(resource)

##    def SwitchOutput(self, output):
##        if output is bool:
##            command = 'OFF'
##            if output:
##                command = 'ON'     
##            self.instrument.write("OUTP:STAT {0}".format(command))
##            

    def OutputOff(self):
        self.instrument.write("OUTP:STAT OFF")
        if self.instrument.ask("OUTP:STAT?") == 'OFF':
            return True
        else:
            return False
        
        
    def StartOutput(self):
        self.instrument.write(":INIT")
    
    def OutputOn(self):
        self.instrument.write("OUTP:STAT ON")
        if self.instrument.ask("OUTP:STAT?") == 'ON':
            return True
        else:
            return False

    def StartPulseAndRead(self):
        return self.instrument.ask(":READ?")

    def SetDC(self):
        self.instrument.write("SOUR:FUNC:SHAP DC")

    def SetPulse(self):
        self.instrument.write("SOUR:FUNC:SHAP PULS")

    def SetVoltageMode(self):
        self.instrument.write("SOUR:FUNC VOLT")

    def SetCurrentMode(self):
        self.instrument.write("SOUR:FUNC CURR")

    def SetVoltageAmplitude(self,voltage):
        self.instrument.write("SOUR:VOLT:LEV:IMM:AMPL {0}".format(voltage))

    MIN_PULSE_WIDTH = 0.00015
    MAX_PULSE_WIDTH = 0.005
    def SetPulseWidth(self,seconds):
        if seconds<self.MIN_PULSE_WIDTH:
            seconds = self.MIN_PULSE_WIDTH
        elif seconds >self.MAX_PULSE_WIDTH :
            seconds = self.MAX_PULSE_WIDTH
        self.instrument.write("SOUR:PULS:WIDT {0}".format(seconds))

    MIN_DELAY = 0
    MAX_DELAY = 9999.99872
    def SetPulseDelay(self,delay):
        if delay<self.MIN_DELAY:
            delay = self.MIN_DELAY
        elif delay > self.MAX_DELAY:
            delay = self.MAX_DELAY
        self.instrument.write("SOUR:PULS:WIDT {0}".format(delay))

    def DisablePulseMeasurements(self):
        self.instrument.write(":SENSe:FUNCtion:OFF:ALL")

    MIN_TRIG_COUNT = 1
    MAX_TRIG_COUNT = 2500
    def SetTriggerCount(self, count):
        if count<self.MIN_TRIG_COUNT:
            count = self.MIN_TRIG_COUNT
        elif count> self.MAX_TRIG_COUNT:
            count = self.MAX_TRIG_COUNT
        self.instrument.write(":TRIG:COUN {0}".format(count))
    
    def IDN(self):
        if self.instrument:
            return self.instrument.ask("*IDN?")

    def Reset(self):
        self.instrument.ask("*RST")
    

if __name__ == "__main__":
    k = Keithley2430('GPIB0::5::INSTR')
##    k.Reset()
    print(k.IDN())
    k.SetCurrentMode()
    time.sleep(1)
    k.SetVoltageMode()
    time.sleep(1)
    k.SetPulse()
    k.DisablePulseMeasurements()
    k.SetPulseWidth(0.005)
    k.SetTriggerCount(1)
##    k.SetPulseDelay(0.01)
    time.sleep(1)
    k.SetVoltageAmplitude(1)
    time.sleep(1)
####    k.StartPulseAndRead()
####    k.StartOutput()
    k.OutputOn()
    time.sleep(2)
    k.OutputOff()
    k.SetDC()
    time.sleep(1)
