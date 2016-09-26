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

    SWITCH_STATES = STATE_ON, STATE_OFF = ['ON','OFF']
    
    ALL_VOLTAGE_RANGES = ['200E-3','2','20','100']
    VOLT_RANGE_200mV,VOLT_RANGE_2V,VOLT_RANGE_20V,VOLT_RANGE_100V = ALL_VOLTAGE_RANGES

    ALL_CURRENT_RANGES = ['10E-6','100E-6','1E-3','10E-3','100E-3','1']
    CURR_RANGE_10uA,CURR_RANGE_100uA,CURR_RANGE_1mA,CURR_RANGE_10mA,CURR_RANGE_100mA,CURR_RANGE_1A = ALL_CURRENT_RANGES

    def SetSourceRange(self,func,rang):
        if func in self.SOURCE_FUNCTIONS:
            if(rang in self.DEFAULT_RANGES) or (rang in self.ALL_VOLTAGE_RANGES) or (rang in self.ALL_CURRENT_RANGES):
                self.instrument.write("SOUR:{f}:RANG {r}".format(f=func,r=rang))

    def SetVoltageSourceRange(self,rang):
        self.SetSourceRange(self.VOLT_SOURCE_FUNCTION,rang)
        
    def SetCurrentSourceRange(self,rang):
        self.SetSourceRange(self.CURR_SOURCE_FUNCTION,rang)

    def SetAutoRange(self,func, state):
        if func in self.SOURCE_FUNCTIONS:
            if state in self.SWITCH_STATES:
                self.instrument.write("SOUR:{f}:RANG:AUTO {s}".format(f = func,s = state))

##
##  END SET SOURCING RANGE
##  
##################################################################################
##
##  SET SOURCING AMPLITUDE
##

    DEFAULT_AMPLITUDES = ['DEF','MIN','MAX']
    DEFAULT_AMPLITUDE,MIN_AMPLITUDE,MAX_AMPLITUDE = DEFAULT_AMPLITUDES
    MAX_VOLT_AMPL_VALUE, MIN_VOLT_AMPL_VALUE = [105,-105]
    MAX_CURR_AMPL_VALUE, MIN_CURR_AMPL_VALUE = [10.5,-10.5]
    def SetFixedModeAmplitude(self,func,ampl):
        if func in self.SOURCE_FUNCTIONS:
            strFmt = "SOUR:{f} {a}"
            if ampl in self.DEFAULT_AMPLITUDES:
                self.instrument.write(strFmt.format(f=func,a=ampl))
            elif func == self.VOLT_SOURCE_FUNCTION:
                if (ampl >= self.MIN_VOLT_AMPL_VALUE) and (ampl<=self.MAX_VOLT_AMPL_VALUE):
                    self.instrument.write(strFmt.format(f=func,a=ampl))
            elif func == self.CURR_SOURCE_FUNCTION:
                if(ampl >= self.MIN_CURR_AMPL_VALUE) and (ampl<=self.MAX_CURR_AMPL_VALUE):
                    self.instrument.write(strFmt.format(f=func,a=ampl))

    def SetVoltageAmplitude(self,volt):
        self.SetFixedModeAmplitude(self.VOLT_SOURCE_FUNCTION,volt)

    def SetCurrentAmplitude(self,curr):
        self.SetFixedModeAmplitude(self.CURR_SOURCE_FUNCTION,curr)
    
##
##  END SET SOURCING AMPLITUDE
##  

##################################################################################
##
##  SET FIXED AMPLITUDE WHEN TRIGGERED
##

    def SetFixedModeAmplitudeWhenTriggered(self,func, ampl):
        if func in self.SOURCE_FUNCTIONS:
            strFmt = "SOUR:{f}:TRIG {a}"
            if ampl in self.DEFAULT_AMPLITUDES:
                self.instrument.write(strFmt.format(f=func,a=ampl))
            elif func == self.VOLT_SOURCE_FUNCTION:
                if (ampl >= self.MIN_VOLT_AMPL_VALUE) and (ampl<=self.MAX_VOLT_AMPL_VALUE):
                    self.instrument.write(strFmt.format(f=func,a=ampl))
            elif func == self.CURR_SOURCE_FUNCTION:
                if(ampl >= self.MIN_CURR_AMPL_VALUE) and (ampl<=self.MAX_CURR_AMPL_VALUE):
                    self.instrument.write(strFmt.format(f=func,a=ampl))

    def SetVoltageAmplitudeWhenTriggered(self,volt):
        self.SetFixedModeAmplitudeWhenTriggered(self.VOLT_SOURCE_FUNCTION,volt)

    def SetCurrentAmplitudeWhenTriggered(self,curr):
        self.SetFixedModeAmplitudeWhenTriggered(self.CURR_SOURCE_FUNCTION,curr)

##
##  END SET FIXED AMPLITUDE WHEN TRIGGERED
##       


##################################################################################
##
##  SET FIXED AMPLITUDE WHEN TRIGGERED
##

    def SetVoltageSourceLimit(self,level):
        strFmt = "SOUR:VOLT:PROT {l}"
        if level in self.DEFAULT_AMPLITUDES:
              self.instrument.write(strFmt.format(l=level))
        elif (level <= MAX_VOLT_AMPL_VALUE)and (level>=MIN_VOLT_AMPL_VALUE):
            self.instrument.write(strFmt.format(l=level))

##
##  END SET FIXED AMPLITUDE WHEN TRIGGERED
##       
##################################################################################
##
##  SET DELAY (NOT USED FOR PULSE MODE)
##

    DELAY_VALUES = [0,999.9999]
    MIN_DELAY, MAX_DELAY = DELAY_VALUES
    
    def SetDelay(self,delay):
        strFmt = "SOUR:DEL {d}"
        if delay in self.DEFAULT_AMPLITUDES:
            self.instrument.write(strFmt.format(d=delay))
        elif (delay>=self.MIN_DELAY) and (delay<=self.MAX_DELAY):
            self.instrument.write(strFmt.format(d=delay))
        
    
##
##  END SET DELAY (NOT USED FOR PULSE MODE)
##       
##################################################################################
##
##  SET PULSE WIDTH (USED FOR PULSE MODE)
##

    MIN_PULSE_WIDTH = 0.00015
    MAX_PULSE_WIDTH = 0.005
    def SetPulseWidth(self,seconds):
        if seconds<self.MIN_PULSE_WIDTH:
            seconds = self.MIN_PULSE_WIDTH
        elif seconds >self.MAX_PULSE_WIDTH :
            seconds = self.MAX_PULSE_WIDTH
        self.instrument.write("SOUR:PULS:WIDT {0}".format(seconds))

##
##   END SET PULSE WIDTH (USED FOR PULSE MODE)
##


##################################################################################
##
##  SET PULSE WIDTH (USED FOR PULSE MODE)
##
    MIN_DELAY = 0
    MAX_DELAY = 9999.99872
    def SetPulseDelay(self,delay):
        if delay<self.MIN_DELAY:
            delay = self.MIN_DELAY
        elif delay > self.MAX_DELAY:
            delay = self.MAX_DELAY
        self.instrument.write("SOUR:PULS:DEL {0}".format(delay))

##
##  END SET PULSE WIDTH (USED FOR PULSE MODE)
##



### SENSE1 SUBSYSTEM
##################################################################################
##
##  SET CONCURRENT MEASUREMENT
##
##  For the Model 2430 Pulse Mode, concurrent measurements are always disabled. 
##  Sending this command results in error +831.
        
    def SetConcurrentMeasurement(self,state):
        if state in self.SWITCH_STATES:
            self.instrument.write("SENS:FUNC:CONC {0}".format(state))


##
##  END SET CONCURRENT MEASUREMENT
##

##################################################################################
##
##  ON/OFF FUNCTIONS
##   
    SENSE_FUNCTIONS = ['VOLT','CURR','RES']
    VOLT_SENSE_FUNCTION, CURR_SENSE_FUNCTION, RES_SENSE_FUNCTION = SENSE_FUNCTIONS

    def SwitchFunction(self, state, func_List):
        if (func_list is list) and (state in self.SWITCH_STATES):
            if all(item in self.SENSE_FUNCTIONS for item in func_list):
                self.instrument.write("FUNC:{0} \"{1}\"".format(state,"\",\"".join(func_List)))
            

    
    def ON_Function(self, func_list):
        self.SwitchFunction(self.STATE_ON,func_list)

    def OFF_Function(self, func_list):
        self.SwitchFunction(self.STATE_OFF,func_list)


    def SwitchAllFunctions(self,state):
        if state in self.SWITCH_STATES:
            self.instrument.write("FUNC:{0}:ALL".format(state))
    
##
##  END ON/OFF FUNCTIONS
##   

##################################################################################
##
##  ON/OFF FUNCTIONS
##

    

##
##  END ON/OFF FUNCTIONS
##        


    
    ## implement fixed sourcing mode

    ## implement range

        
##    def SetVoltageAmplitude(self,voltage):
##        self.instrument.write("SOUR:VOLT:LEV {0}".format(voltage))
##
##
##    def SetCurrentAmplitude(self,current):
##        self.instrument.write("SOUR:CURR:LEV {0}".format(current))

    
        
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
        self.instrument.write("*RST")



    

if __name__ == "__main__":
    k = Keithley24XX('GPIB0::5::INSTR')
    k.Reset()
    time.sleep(1)
    print(k.IDN())
    
    k.SetCurrentSourceFunction()
    time.sleep(1)
    k.SetVoltageSourceFunction()
##    k.SwitchAllFunctions(k.STATE_ON)
##    time.sleep(1)
    k.SetPulse()
    k.DisablePulseMeasurements()
    print("pw")
    k.SetPulseWidth(0.005)
    print("pd")
    k.SetPulseDelay(1)
    print("pc")
    k.SetTriggerCount(3)
    print("a")
    time.sleep(1)
    k.SetVoltageSourceRange(k.MAX_RANGE)#VOLT_RANGE_100V)
    time.sleep(1)
    
    k.SetVoltageAmplitude(100)
    time.sleep(1)
    k.StartOutput()
##    k.OutputOn()
##    print(k.StartOutputAndRead())
    time.sleep(2)
    k.OutputOff()
    k.SetDC()
    time.sleep(1)
