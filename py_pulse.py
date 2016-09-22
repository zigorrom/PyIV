import visa
import time

class Keithley24XX:
    def __init__(self,resource):
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(resource)

##################################################################################
##
##  SET FUNCTION SHAPE
##

    FUNCTION_SHAPES = ['DC', 'PULS']
    DC_SHAPE,PULSE_SHAPE=FUNCTION_SHAPES

    def SetFunctionShape(self,shape):
        if shape in self.FUNCTION_SHAPES:
            self.instrument.write("SOUR:FUNC:SHAP {0}".format(shape))
    
    def SetDC(self):
        self.SetFunctionShape(self.DC_SHAPE)

    def SetPulse(self):
        self.SetFunctionShape(self.PULSE_SHAPE)

##
##  END SET FUNCTION SHAPE
##
##################################################################################
##
##  SET SOURCE FUNCTION
##

    SOURCE_FUNCTIONS = ['VOLT','CURR']
    VOLT_SOURCE_FUNCTION, CURR_SOURCE_FUNCTION = SOURCE_FUNCTIONS

    def SetSourceFunction(self,func):
        if func in self.SOURCE_FUNCTIONS:
            self.instrument.write("SOUR:FUNC {0}".format(func))
    
    def SetVoltageSourceFunction(self):
        self.SetSourceFunction(self.VOLT_SOURCE_FUNCTION)
    

    def SetCurrentSourceFunction(self):
        self.SetSourceFunction(self.CURR_SOURCE_FUNCTION)

##
##  END SET SOURCE FUNCTION
##
##################################################################################
##
##  SET SOURCING MODE
##
    SOURSING_MODES = ['FIX','LIST','SWE']
    FIXED_SOURCING_MODE, lIST_SOURCING_MODE,SWEEP_SOURCING_MODE = SOURSING_MODES

    def SetSourceMode(self,func, mode):
        if (mode in self.SOURSING_MODES) and (func in self.SOURCE_FUNCTIONS):
            self.instrument.write("SOUR:{f}:MODE {m}".format(f=func,m=mode))

    def SetFixedVoltageSourceMode(self):
        self.SetSourcingMode(VOLT_SOURCE_FUNCTION,FIXED_SOURCING_MODE)

    def SetFixedCurrentSourceMode(self):
        self.SetSourcingMode(CURR_SOURCE_FUNCTION,FIXED_SOURCING_MODE)

    def SetListVoltageSourceMode(self):
        self.SetSourcingMode(VOLT_SOURCE_FUNCTION,lIST_SOURCING_MODE)

    def SetLisrCurrentSourceMode(self):
        self.SetSourcingMode(CURR_SOURCE_FUNCTION,lIST_SOURCING_MODE)
        
    def SetSweepVoltageSourceMode(self):
        self.SetSourcingMode(VOLT_SOURCE_FUNCTION,SWEEP_SOURCING_MODE)
        
    def SetSweepCurrentSourceMode(self):
        self.SetSourcingMode(CURR_SOURCE_FUNCTION,SWEEP_SOURCING_MODE)

        
##
##  END SET SOURCING MODE
##
##################################################################################
##
##  SET SOURCING RANGE
##
    DEFAULT_RANGES = ['DEF','MIN','MAX','UP','DOWN']
    DEFAULT_RANGE,MIN_RANGE,MAX_RANGE,UP_RANGE,DOWN_RANGE = DEFAULT_RANGES

    AUTO_RANGE_STATES = AUTO_RANGE_ON, AUTO_RANGE_OFF = ['ON','OFF']
    
    ALL_VOLTAGE_RANGES = ['200E-3','2','20','100']
    VOLT_RANGE_200mV,VOLT_RANGE_2V,VOLT_RANGE_20V,VOLT_RANGE_100V = ALL_VOLTAGE_RANGES

    ALL_CURRENT_RANGES = ['10E-6','100E-6','1E-3','10E-3','100E-3','1']
    CURR_RANGE_10uA,CURR_RANGE_100uA,CURR_RANGE_1mA,CURR_RANGE_10mA,CURR_RANGE_100mA,CURR_RANGE_1A = ALL_CURRENT_RANGES

    def SetSourceRange(self,func,range):
        if func in self.SOURCE_FUNCTIONS:
            if(range in self.DEFAULT_RANGES) or (range in self.ALL_VOLTAGE_RANGES) or (range in self.ALL_CURRENT_RANGES):
                self.instrument.write("SOUR:{f}:RANG {r}".format(f=func,r=range))

    def SetVoltageSourceRange(self,range):
        if range in self.ALL_VOLTAGE_RANGES:
            self.SetSourceRange(self.VOLT_SOURCE_FUNCTION,range)
        
    def SetCurrentSourceRange(self,range):
        if range in self.ALL_CURRENT_RANGES:
            self.SetSourceRange(self.CURR_SOURCE_FUNCTION,range)

    def SetAutoRange(self,func, state):
        if func in self.SOURCE_FUNCTIONS:
            if state in self.AUTO_RANGE_STATES:
                self.instrument.write("SOUR:{f}:RANG:AUTO {s}".format(f = func,s = state))

##
##  END SET SOURCING RANGE
##  
##################################################################################
##
##  SET SOURCING RANGE
##

    

##
##  END SET SOURCING RANGE
##  

        

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




    
    ## implement fixed sourcing mode

    ## implement range

        
    def SetVoltageAmplitude(self,voltage):
        self.instrument.write("SOUR:VOLT:LEV {0}".format(voltage))


    def SetCurrentAmplitude(self,current):
        self.instrument.write("SOUR:CURR:LEV {0}".format(current))

    
        
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

    def StartOutputAndRead(self):
        return self.instrument.ask(":READ?")

    

    

    
    
    
    
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
    k = Keithley24XX('GPIB0::5::INSTR')
##    k.Reset()
    print(k.IDN())
    
    k.SetCurrentSourceFunction()
    time.sleep(1)
    k.SetVoltageSourceFunction()
    
    time.sleep(1)
    k.SetPulse()
    k.DisablePulseMeasurements()
    k.SetPulseWidth(0.005)
    k.SetTriggerCount(1)

    time.sleep(1)
    k.SetVoltageSourceRange(k.MIN_RANGE)
    time.sleep(1)
    k.SetAutoRange(k.VOLT_SOURCE_FUNCTION,k.AUTO_RANGE_ON)
    print(k.AUTO_RANGE_ON)
##    k.SetSourcingRange(k.VOLT_SOURCE_FUNCTION,k.VOLT_RANGE_200mV)
    k.SetVoltageAmplitude(100)
    time.sleep(1)
##    k.StartOutput()
    k.OutputOn()
##    print(k.StartOutputAndRead())
    time.sleep(2)
    k.OutputOff()
    k.SetDC()
    time.sleep(1)
