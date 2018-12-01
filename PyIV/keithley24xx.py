import sys
import visa
import time
import pyqtgraph as pg
import numpy as np
from PyQt4 import QtGui
from communication_layer import VisaInstrument, instrument_await_function

#def instrument_await_function(func):
#        def wrapper(self,*args,**kwargs):
#            #print (isinstance(self,VisaInstrument))
#            prev_timeout = self.instrument.timeout
#            self.instrument.timeout = None
#            #self.timeout = None
#            #self.__instrument.timeout = None
#            result = func(self,*args,**kwargs)
#            self.instrument.timeout = prev_timeout
#            #self.__instrument.timeout = prev_timeout 
#            return result
#        return wrapper

class Keithley24XX(VisaInstrument):
    def __init__(self, resource):
        super().__init__(resource)

    #def __init__(self,resource):
        
        #rm = visa.ResourceManager()
        #self.instrument = rm.open_resource(resource)

##################################################################################
##
##  SET FUNCTION SHAPE
##

    FUNCTION_SHAPES = ['DC', 'PULS']
    DC_SHAPE,PULSE_SHAPE=FUNCTION_SHAPES

    def SetFunctionShape(self,shape):
        if shape in self.FUNCTION_SHAPES:
            self.write("SOUR:FUNC:SHAP {0}".format(shape))
    
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

    SOURCE_SENSE_FUNCTIONS = ['VOLT','CURR']
    VOLT_SOURCE_FUNCTION, CURR_SOURCE_FUNCTION = SOURCE_SENSE_FUNCTIONS 

    def SetSourceFunction(self,func):
        if func in self.SOURCE_SENSE_FUNCTIONS :
            self.write("SOUR:FUNC {0}".format(func))
    
    def SetVoltageSourceFunction(self):
        self.SetSourceFunction(self.VOLT_SOURCE_FUNCTION)
    

    def SetCurrentSourceFunction(self):
        self.SetSourceFunction(self.CURR_SOURCE_FUNCTION)

    def SetSenseFunction(self,func):
        if func in self.SOURCE_SENSE_FUNCTIONS :
            self.write("SENS:FUNC '{0}'".format(func)) 

    def SetVoltageSenseFunction(self):
        self.SetSenseFunction(self.VOLT_SOURCE_FUNCTION)
    

    def SetCurrentSenseFunction(self):
        self.SetSenseFunction(self.CURR_SOURCE_FUNCTION)

##
##  END SET SOURCE FUNCTION
##
##################################################################################
##
##  SET SOURCING MODE
##
    SOURSING_MODES = ['FIX','LIST','SWE']
    FIXED_SOURCING_MODE, lIST_SOURCING_MODE,SWEEP_SOURCING_MODE = SOURSING_MODES

    def SetSourcingMode(self,func, mode):
        if (mode in self.SOURSING_MODES) and (func in self.SOURCE_SENSE_FUNCTIONS):
            self.write("SOUR:{f}:MODE {m}".format(f=func,m=mode))

    def SetFixedVoltageSourceMode(self):
        self.SetSourcingMode(self.VOLT_SOURCE_FUNCTION,self.FIXED_SOURCING_MODE)

    def SetFixedCurrentSourceMode(self):
        self.SetSourcingMode(self.CURR_SOURCE_FUNCTION,self.FIXED_SOURCING_MODE)

    def SetListVoltageSourceMode(self):
        self.SetSourcingMode(self.VOLT_SOURCE_FUNCTION,self.lIST_SOURCING_MODE)

    def SetListCurrentSourceMode(self):
        self.SetSourcingMode(self.CURR_SOURCE_FUNCTION,self.lIST_SOURCING_MODE)
        
    def SetSweepVoltageSourceMode(self):
        self.SetSourcingMode(self.VOLT_SOURCE_FUNCTION,self.SWEEP_SOURCING_MODE)
        
    def SetSweepCurrentSourceMode(self):
        self.SetSourcingMode(self.CURR_SOURCE_FUNCTION,self.SWEEP_SOURCING_MODE)

        
##
##  END SET SOURCING MODE
##
##################################################################################
##
##  SET SOURCING RANGE
##
    DEFAULT_RANGES = ['DEF','MIN','MAX','UP','DOWN']
    DEFAULT_RANGE,MIN_RANGE,MAX_RANGE,UP_RANGE,DOWN_RANGE = DEFAULT_RANGES

    STATE_ON, STATE_OFF = SWITCH_STATES = ['ON','OFF']
    
    ALL_VOLTAGE_RANGES = ['200E-3','2','20','100']
    VOLT_RANGE_200mV,VOLT_RANGE_2V,VOLT_RANGE_20V,VOLT_RANGE_100V = ALL_VOLTAGE_RANGES

    ALL_CURRENT_RANGES = ['10E-6','100E-6','1E-3','10E-3','100E-3','1']
    CURR_RANGE_10uA,CURR_RANGE_100uA,CURR_RANGE_1mA,CURR_RANGE_10mA,CURR_RANGE_100mA,CURR_RANGE_1A = ALL_CURRENT_RANGES

    def SetSourceRange(self,func,rang):
        if func in self.SOURCE_SENSE_FUNCTIONS:
            if(rang in self.DEFAULT_RANGES) or (rang in self.ALL_VOLTAGE_RANGES) or (rang in self.ALL_CURRENT_RANGES):
                self.write("SOUR:{f}:RANG {r}".format(f=func,r=rang))

    def SetVoltageSourceRange(self,rang):
        self.SetSourceRange(self.VOLT_SOURCE_FUNCTION,rang)
        
    def SetCurrentSourceRange(self,rang):
        self.SetSourceRange(self.CURR_SOURCE_FUNCTION,rang)

    def SetAutoRange(self,func, state):
        if func in self.SOURCE_SENSE_FUNCTIONS:
            if state in self.SWITCH_STATES:
                self.write("SOUR:{f}:RANG:AUTO {s}".format(f = func,s = state))

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
        if func in self.SOURCE_SENSE_FUNCTIONS:
            strFmt = "SOUR:{f} {a}"
            if ampl in self.DEFAULT_AMPLITUDES:
                self.write(strFmt.format(f=func,a=ampl))
            elif func == self.VOLT_SOURCE_FUNCTION:
                if (ampl >= self.MIN_VOLT_AMPL_VALUE) and (ampl<=self.MAX_VOLT_AMPL_VALUE):
                    self.write(strFmt.format(f=func,a=ampl))
            elif func == self.CURR_SOURCE_FUNCTION:
                if(ampl >= self.MIN_CURR_AMPL_VALUE) and (ampl<=self.MAX_CURR_AMPL_VALUE):
                    self.write(strFmt.format(f=func,a=ampl))

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
        if func in self.SOURCE_SENSE_FUNCTIONS:
            strFmt = "SOUR:{f}:TRIG {a}"
            if ampl in self.DEFAULT_AMPLITUDES:
                self.write(strFmt.format(f=func,a=ampl))
            elif func == self.VOLT_SOURCE_FUNCTION:
                if (ampl >= self.MIN_VOLT_AMPL_VALUE) and (ampl<=self.MAX_VOLT_AMPL_VALUE):
                    self.write(strFmt.format(f=func,a=ampl))
            elif func == self.CURR_SOURCE_FUNCTION:
                if(ampl >= self.MIN_CURR_AMPL_VALUE) and (ampl<=self.MAX_CURR_AMPL_VALUE):
                    self.write(strFmt.format(f=func,a=ampl))

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
    #DEFAULT_AMPLITUDES = ['DEF','MIN','MAX']
    #DEFAULT_AMPLITUDE,MIN_AMPLITUDE,MAX_AMPLITUDE = DEFAULT_AMPLITUDES
    MAX_VOLT_COMPLIANCE, MIN_VOLT_COMPLIANCE = [105,-105]
    MAX_CURR_COMPLIANCE, MIN_CURR_COMPLIANCE = [1.05,-1.05]
    def SetSenseCompliance(self,func,compliance):
        if func in self.SENSE_FUNCTIONS:
            strFmt = ":SENS:{f}:PROT {c}"
            if compliance in self.DEFAULT_AMPLITUDES:
                self.write(strFmt.format(f=func, c=compliance))
            elif func == self.VOLT_SENSE_FUNCTION:
                if (compliance >= self.MIN_VOLT_COMPLIANCE) and (compliance <= self.MAX_VOLT_COMPLIANCE):
                    self.write(strFmt.format(f=func, c=compliance))
            elif func == self.CURR_SENSE_FUNCTION:
                if (compliance >= self.MIN_CURR_COMPLIANCE) and (compliance <= self.MAX_CURR_COMPLIANCE):
                    self.write(strFmt.format(f=func, c=compliance))

    def SetVoltageSenseCompliance(self, compliance):
        self.SetSenseCompliance(self.VOLT_SENSE_FUNCTION, compliance)

    def SetCurrentSenseCompliance(self, compliance):
        self.SetSenseCompliance(self.CURR_SENSE_FUNCTION, compliance)



    def SetVoltageSourceLimit(self,level):
        strFmt = "SOUR:VOLT:PROT {l}"
        if level in self.DEFAULT_AMPLITUDES:
              self.write(strFmt.format(l=level))
        elif (level <= MAX_VOLT_AMPL_VALUE)and (level>=MIN_VOLT_AMPL_VALUE):
            self.write(strFmt.format(l=level))

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
            self.write(strFmt.format(d=delay))
        elif (delay>=self.MIN_DELAY) and (delay<=self.MAX_DELAY):
            self.write(strFmt.format(d=delay))
        
    
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
        self.write("SOUR:PULS:WIDT {0}".format(seconds))

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
        self.write("SOUR:PULS:DEL {0}".format(delay))

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
            self.write("SENS:FUNC:CONC {0}".format(state))


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
                self.write("FUNC:{0} \"{1}\"".format(state,"\",\"".join(func_List)))
            

    
    def ON_Function(self, func_list):
        self.SwitchFunction(self.STATE_ON,func_list)

    def OFF_Function(self, func_list):
        self.SwitchFunction(self.STATE_OFF,func_list)


    def SwitchAllFunctions(self,state):
        if state in self.SWITCH_STATES:
            self.write("FUNC:{0}:ALL".format(state))

    def SetNPLC(self, func, nplc):
        if func in self.SENSE_FUNCTIONS:
            self.write(":SENS:{0}:NPLC {1}".format(func, nplc))
    
    def SetVoltageNPLC(self, nplc):
        self.SetNPLC(self.VOLT_SENSE_FUNCTION, nplc)

    def SetCurrentNPLC(self, nplc):
        self.SetNPLC(self.CURR_SENSE_FUNCTION, nplc)

    def SetResistanceNPLC(self, nplc):
        self.SetNPLC(self.RES_SENSE_FUNCTION, nplc)

##
##  END ON/OFF FUNCTIONS
##   

##################################################################################
##
##  SWEEP FUNCTIONS
##
    
    RANGING_LIST = ["BEST","AUTO","FIX"]
    RANGING_BEST,RANGING_AUTO, RANGING_FIX = RANGING_LIST
    def SetSweepRanging(self,mode):
        if mode in self.RANGING_LIST:
            self.write(":SOUR:SWE:RANG {0}".format(mode))

    SPACING_MODES = ["LIN","LOG"]
    SPACING_LIN, SPACING_LOG = SPACING_MODES
    def SetSweepSpacing(self,spacing):
        if spacing in self.SPACING_MODES:
            self.write(":SOUR:SWE:SPAC {0}".format(spacing))

    def SetSweepStartVoltage(self, voltage):
        self.write(":SOUR:VOLT:STAR {0}".format(voltage))

    def SetSweepStopVoltage(self,voltage):
        self.write(":SOUR:VOLT:STOP {0}".format(voltage))

    def SetSweepStepVoltage(self, step):
        self.write(":SOUR:VOLT:STEP {0}".format(step))

    def SetSweepPoints(self,points):
        self.write(":SOUR:SWE:POIN {0}".format(points))

    def GetSweepPoints(self):
        return int(self.query(":SOUR:SWE:POIN?"))

##
##  END SWEEP FUNCTIONS
##        
##################################################################################
##
##  SET SENSING RANGE
##
    #DEFAULT_RANGES = ['DEF','MIN','MAX','UP','DOWN']
    #DEFAULT_RANGE,MIN_RANGE,MAX_RANGE,UP_RANGE,DOWN_RANGE = DEFAULT_RANGES

    #STATE_ON, STATE_OFF = SWITCH_STATES = ['ON','OFF']
    
    #ALL_VOLTAGE_RANGES = ['200E-3','2','20','100']
    #VOLT_RANGE_200mV,VOLT_RANGE_2V,VOLT_RANGE_20V,VOLT_RANGE_100V = ALL_VOLTAGE_RANGES

    #ALL_CURRENT_RANGES = ['10E-6','100E-6','1E-3','10E-3','100E-3','1']
    #CURR_RANGE_10uA,CURR_RANGE_100uA,CURR_RANGE_1mA,CURR_RANGE_10mA,CURR_RANGE_100mA,CURR_RANGE_1A = ALL_CURRENT_RANGES

    def SetSenseRange(self,func,rang):
        if func in self.SOURCE_SENSE_FUNCTIONS:
            if(rang in self.DEFAULT_RANGES) or (rang in self.ALL_VOLTAGE_RANGES) or (rang in self.ALL_CURRENT_RANGES):
                self.write("SENS:{f}:RANG {r}".format(f=func,r=rang))

    def SetVoltageSenseRange(self,rang):
        self.SetSenseRange(self.VOLT_SENSE_FUNCTION,rang)
    
    def SetCurrentSenseRange(self,rang):
        self.SetSenseRange(self.CURR_SENSE_FUNCTION,rang)

    def SetAutoSenseRange(self,func, state):
        if func in self.SOURCE_SENSE_FUNCTIONS:
            if state in self.SWITCH_STATES:
                self.write("SENS:{f}:RANG:AUTO {s}".format(f = func,s = state))

    def SwitchCurrentAutoSenseRangeOn(self):
        self.SetAutoSenseRange(self.CURR_SENSE_FUNCTION, self.STATE_ON)

    def SwitchCurrentAutoSenseRangeOff(self):
        self.SetAutoSenseRange(self.CURR_SENSE_FUNCTION, self.STATE_OFF)

##
##  END SET SENSING RANGE
##
##################################################################################
##
##  Triggering FUNCTIONS
##
    MIN_TRIG_COUNT = 1
    MAX_TRIG_COUNT = 2500
    def SetTriggerCount(self, count):
        if count<self.MIN_TRIG_COUNT:
            count = self.MIN_TRIG_COUNT
        elif count> self.MAX_TRIG_COUNT:
            count = self.MAX_TRIG_COUNT
        self.write(":TRIG:COUN {0}".format(count))
    
    def SetArmCount(self,count):
        if count<self.MIN_TRIG_COUNT:
            count = self.MIN_TRIG_COUNT
        elif count> self.MAX_TRIG_COUNT:
            count = self.MAX_TRIG_COUNT
        self.write(":ARM:COUN {0}".format(count))

    def ClearInputTriggers(self):
        self.write(":TRIG:CLE")

    def Initiate(self):
        self.write(":INIT")
    
    def Abort(self):
        self.write("ABOR")

    MIN_TRIG_DELAY, MAX_TRIG_DELAY = (0, 999.999)
    def SetTriggerDelay(self,delay):
        if delay < self.MIN_TRIG_DELAY:
            delay = self.MIN_TRIG_DELAY
        if delay > self.MAX_TRIG_DELAY:
            delay = self.MAX_TRIG_DELAY
        self.write(":TRIG:DEL {0}".format(delay))

    TRIG_SOURCE_LIST = ["IMM","TLIN","TIM", "MAN", "BUS", "NST", "PST","BST"]
    TRIG_IMM, TRIG_TLIN,TRIG_TIM,TRIG_MAN,TRIG_BUS,TRIG_NST,TRIG_PST,TRIG_BST = TRIG_SOURCE_LIST
    def SetTriggerSource(self,source):
        if source in self.TRIG_SOURCE_LIST:
            self.write(":TRIG:SOUR {0}".format(source))

    def SetArmSource(self,source):
        if source in self.TRIG_SOURCE_LIST:
            self.write(":ARM:SOUR {0}".format(source))

    TRIG_EVENTS = ["SOUR","SENS","DEL","NONE"]
    TRIG_SOUR_EVENT,TRIG_SENS_EVENT,TRIG_DEL_EVENT,TRIG_NONE_EVENT = TRIG_EVENTS
    def SetTriggerInputEventDetection(self, *event):
        events = filter(lambda x: x in self.TRIG_EVENTS, event)
        if events:
            res = ", ".join(events)
            self.write(":TRIG:INP {0}".format(res))

    def SetTriggerOutputEvent(self, *event):
        events = filter(lambda x: x in self.TRIG_EVENTS, event)
        if events:
            res = ", ".join(events)
            self.write(":TRIG:OUTP {0}".format(res))

    ARM_EVENTS = ["TENT", "TEX", "NONE"]
    ARM_TENT_EVENT, ARM_TEX_EVENT, ARM_NONE_EVENT = ARM_EVENTS

    def SetArmOutputEvent(self, *event):
        events = filter(lambda x: x in self.ARM_EVENTS, event)
        if events:
            res = ", ".join(events)
            self.write(":ARM:OUTP {0}".format(res))



    TRIG_INPUT_LINES = [1,2,3,4]
    def SetTriggerInputLine(self, line):
        if line in self.TRIG_INPUT_LINES:
            self.write(":TRIG:ILIN {0}".format(line))
            
    TRIG_OUTPUT_LINES = [1,2,3,4]
    def SetTriggerOutputLine(self, line):
        if line in self.TRIG_OUTPUT_LINES:
            self.write(":TRIG:OLIN {0}".format(line))


##
##  END Triggering FUNCTIONS
##        



##################################################################################
##
##  FILTERING FUNCTIONS
##

    REPEAT_FILTER, MOVING_FILTER = FILTER_TYPES = ["REP", "MOV"]
    def SetAverageFilter(self, filter):
        if filter in self.FILTER_TYPES:
            self.write(":SENS:AVER:TCON {0}".format(filter))

    def SetRepeatAverageFilter(self):
        self.SetAverageFilter(self.REPEAT_FILTER)

    def SetMovingAverageFilter(self):
        self.SetAverageFilter(self.MOVING_FILTER)

    MIN_FILTER_COUNT,DEFAULT_FILTER_COUNT, MAX_FILTER_COUNT = (1,10,100)
    def SetAverageFilterCount(self,count):
        if count <= self.MAX_FILTER_COUNT and count >= self.MIN_FILTER_COUNT:
            self.write(":SENS:AVER:COUN {0}".format(count))

    def SetMinAverageFilterCount(self):
        self.SetAverageFilterCount(self.MIN_FILTER_COUNT)

    def SetDefaultAverageFilterCount(self):
        self.SetAverageFilterCount(self.DEFAULT_FILTER_COUNT)

    def SetMaxAverageFilterCount(self):
        self.SetAverageFilterCount(self.MAX_FILTER_COUNT)
    
    def SwitchAveragingFilter(self, state):
        if state in self.SWITCH_STATES:
            self.write(":SENS:AVER:STAT {0}".format(state))

    def SwitchAveragingFilterOn(self):
        self.SwitchAveragingFilter(self.STATE_ON)

    def SwitchAveragingFilterOff(self):
        self.SwitchAveragingFilter(self.STATE_OFF)

##
##  END FILTERING FUNCTIONS
## 
    
##################################################################################
##
##  AUTO ZERO FUNCTIONS
##

    def SwitchAutoZero(self, state):
        if state in self.SWITCH_STATES:
            self.write(":SYST:AZER:STAT {0}".format(state))

    def SwitchAutoZeroOn(self):
        self.SwitchAutoZero(self.STATE_ON)

    def SwitchAutoZeroOff(self):
        self.SwitchAutoZero(self.STATE_OFF)

    def ForceAutoZeroUpdate(self):
        self.write(":SYST:AZER:STAT ONCE")

##
##  END AUTO ZERO FUNCTIONS
## 
   

##################################################################################
##
##  NPLC CACHING FUNCTIONS
##

    def SwitchNPLCcaching(self, state):
        if state in self.SWITCH_STATES:
            self.write(":SYST:AZER:CACH:STAT {0}".format(state))

    def SwitchNPLCcachingOn(self):
        self.SwitchNPLCcaching(self.STATE_ON)

    def SwitchNPLCcachingOff(self):
        self.SwitchNPLCcaching(self.STATE_OFF)

    def UpdateNPLCcacheValues(self):
        self.write(":SYST:AZER:CACH:REFR")

    def ClearNPLCcacheValues(self):
        self.write(":SYST:AZER:CACH::RES")



##
##  END NPLC CACHING FUNCTIONS
## 




    ## implement fixed sourcing mode

    ## implement range

        
##    def SetVoltageAmplitude(self,voltage):
##        self.write("SOUR:VOLT:LEV {0}".format(voltage))
##
##
##    def SetCurrentAmplitude(self,current):
##        self.write("SOUR:CURR:LEV {0}".format(current))

        
    def OutputOn(self):
        self.write("OUTP:STAT ON")
                
    def OutputOff(self):
        self.write("OUTP:STAT OFF")
          
    #TRACE***********************

    def ClearBuffer(self):
        self.write(":TRAC:CLE")
    

    MAX_TRACE_POINTS_COUNT, MIN_TRACE_POINTS_COUNT = (2500,1)
    def SetTraceBufferSize(self, count):
        if count>= self.MIN_TRACE_POINTS_COUNT and count <= self.MAX_TRACE_POINTS_COUNT:
            self.write(":TRAC:POIN {0}".format(count))

    TRACE_CONTROLS = ["NEXT", "NEV"]
    NEXT_TRACE_CONTROL, NEVER_TRACE_CONTROL = TRACE_CONTROLS
    def SelectTraceBufferControl(self, ctrl):
        if ctrl in self.TRACE_CONTROLS:
            self.write(":TRAC:FEED:CONT {0}".format(ctrl))


    @instrument_await_function
    def ReadTraceData(self):
        return self.query(":TRAC:DATA?")



    @instrument_await_function
    def StartOutputAndRead(self):
        return self.query(":READ?")

    @instrument_await_function
    def FetchData(self):
        return self.query(":FETC?")

    
    #***********************************************
    
    
    
    
    def DisablePulseMeasurements(self):
        self.write(":SENSe:FUNCtion:OFF:ALL")

    
    
    def IDN(self):
        if self.is_initialized():
            return self.query("*IDN?")

    def Reset(self):
        self.write("*RST")

    def ClearStatus(self):
        self.write("*CLS")

    def OperationCompletedQuery(self):
        return bool(self.query("*OPC?"))

    def WaitOperationCompleted(self):
        self.write("*WAI")

    def SwitchBeeper(self, state):
        if state in Keithley24XX.SWITCH_STATES:
            self.write(":SYST:BEEP:STAT {0}".format(state))

    def SwitchBeeperOn(self):
        self.SwitchBeeper(Keithley24XX.STATE_ON)

    def SwitchBeeperOff(self):
        self.SwitchBeeper(Keithley24XX.STATE_OFF)

    def QueryBeeperState(self):
        val = self.query(":SYST:BEEP:STAT?")
        return val
    
    def PerformBeep(self):
        self.write(":SYST:BEEP:IMM 2560, 0.2")
            

def perform_sweep():
    k = Keithley24XX('GPIB0::5::INSTR')
    k2 = Keithley24XX('GPIB0::16::INSTR')
    k.Abort()
    k2.Abort()

    k.Reset()
    k2.Reset()
    
    k.ClearBuffer()
    k2.ClearBuffer()
    

    print(k.IDN())
    print(k2.IDN())

   

    k.SetConcurrentMeasurement(Keithley24XX.STATE_ON)
    k2.SetConcurrentMeasurement(Keithley24XX.STATE_ON)
    #k.SetConcurrentMeasurement(Keithley24XX.STATE_OFF)
    #k2.SetConcurrentMeasurement(Keithley24XX.STATE_OFF)



    k.SetVoltageSourceFunction()
    k2.SetVoltageSourceFunction()

    k.SetCurrentSenseFunction()
    k2.SetCurrentSenseFunction()

    k.SetVoltageNPLC(0.1)
    k2.SetVoltageNPLC(0.1)

    k.SetCurrentSenseCompliance(Keithley24XX.MAX_CURR_COMPLIANCE)
    k2.SetCurrentSenseCompliance(Keithley24XX.MAX_CURR_COMPLIANCE)

    k.SetSweepStartVoltage(-1)
    k.SetSweepStopVoltage(1)
    k.SetSweepPoints(101)
    #k.SetSweepStepVoltage(0.001)
    npoints = k.GetSweepPoints()

    k.SetSweepVoltageSourceMode()
    k2.SetVoltageAmplitude(0.5)

    

    k.SetSweepRanging(Keithley24XX.RANGING_AUTO)
    k.SetSweepSpacing(Keithley24XX.SPACING_LIN)
    
    k.SetTriggerCount(npoints)
    k2.SetTriggerCount(npoints)
    k.SetTraceBufferSize(npoints)
    k2.SetTraceBufferSize(npoints)

    k.SelectTraceBufferControl(Keithley24XX.NEXT_TRACE_CONTROL)
    k2.SelectTraceBufferControl(Keithley24XX.NEXT_TRACE_CONTROL)


    k2.SetTriggerSource(Keithley24XX.TRIG_TLIN)
    k2.SetTriggerInputEventDetection(Keithley24XX.TRIG_SOUR_EVENT)
    k2.SetTriggerInputLine(1)
    k2.SetTriggerOutputLine(2)
    k2.SetTriggerOutputEvent(Keithley24XX.TRIG_SENS_EVENT)


    k.SetTriggerSource(Keithley24XX.TRIG_TLIN)
    k.SetTriggerInputEventDetection(Keithley24XX.TRIG_SENS_EVENT)
    k.SetTriggerOutputEvent(Keithley24XX.TRIG_SOUR_EVENT)
    k.SetTriggerOutputLine(1)
    k.SetTriggerInputLine(2)

    k.SetDelay(0.001)
    k2.SetDelay(0.001)

    k.OutputOn()
    k2.OutputOn()
    
    k.Initiate()
    k2.Initiate()

    #while not k.OperationCompletedQuery():
    k.WaitOperationCompleted()
    k2.WaitOperationCompleted()
    #k.OperationCompletedQuery()
    k.OutputOff()
    k2.OutputOff()

    strData = k.ReadTraceData() #k.FetchData()
    strData2 = k2.ReadTraceData() #k2.FetchData()

    
    #print(strData)
    #print(k.StartOutputAndRead())
    

    data = np.fromstring(strData, sep=',')
    data2 = np.fromstring(strData2, sep=',')
    data = data.reshape((npoints,5)).T
    data2 = data2.reshape((npoints,5)).T
    
    voltages, currents, resistances, times, status  = data
    voltages2, currents2, resistances2, times2, status2  = data2


    pg.plot(voltages, currents)
    pg.plot(voltages2, currents2)

    #pg.plot(times, currents)

def perform_beep():
    k = Keithley24XX('GPIB0::5::INSTR')
    k.SwitchBeeper(Keithley24XX.STATE_ON)
    k.write(":SYST:BEEP:IMM 2560, 0.2")


if __name__ == "__main__":
    
    perform_beep()

    #app = QtGui.QApplication(sys.argv)
    #app.setApplicationName("IV measurement")
    
    #perform_sweep()
    
    #sys.exit(app.exec_())


#    k = Keithley24XX('GPIB0::5::INSTR')
#    k.Reset()
#    time.sleep(1)
#    print(k.IDN())
    
#    k.SetCurrentSourceFunction()
#    time.sleep(1)
#    k.SetVoltageSourceFunction()
###    k.SwitchAllFunctions(k.STATE_ON)
###    time.sleep(1)
#    k.SetPulse()
#    k.DisablePulseMeasurements()
#    print("pw")
#    k.SetPulseWidth(0.005)
#    print("pd")
#    k.SetPulseDelay(1)
#    print("pc")
#    k.SetTriggerCount(3)
#    print("a")
#    time.sleep(1)
#    k.SetVoltageSourceRange(k.MAX_RANGE)#VOLT_RANGE_100V)
#    time.sleep(1)
    
#    k.SetVoltageAmplitude(100)
#    time.sleep(1)
#    k.StartOutput()
###    k.OutputOn()
###    print(k.StartOutputAndRead())
#    time.sleep(2)
#    k.OutputOff()
#    k.SetDC()
#    time.sleep(1)
