import sys
import os
import time
import datetime
import configparser
import numpy as np
import pandas as pd
import pint

from pint import UnitRegistry
from PyQt4 import uic, QtGui, QtCore
from PyQt4.QtCore import QThread

from communication_layer import get_available_gpib_resources, get_available_com_resources
from keithley24xx import Keithley24XX
from range_handlers import float_range
from iv_plot import IV_PlotWidget



INTEGRATION_SPEEDS = ["Slow", "Middle", "Fast"]
INTEGRATION_SLOW,INTEGRATION_MIDDLE, INTEGRATION_FAST = INTEGRATION_SPEEDS

MEASUREMENT_TYPES = ["Output", "Transfer"]
OUTPUT_MEASUREMENT, TRANSFER_MEASUREMENT = MEASUREMENT_TYPES


  

class IV_Experiment(QThread):
    measurementStarted = QtCore.pyqtSignal() # int - max amount of points in the sweep
    measurementFinished = QtCore.pyqtSignal()

    experimentStarted = QtCore.pyqtSignal(int)  # int - max amount of points in the sweep
    experimentFinished = QtCore.pyqtSignal()

    measurementProgressChanged =QtCore.pyqtSignal(int)
    measurementDataArrived = QtCore.pyqtSignal(tuple) 
    measurementNextFile = QtCore.pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.alive = True

        self.gate_keithley = None
        self.drain_keithley = None
        
        self.measurement_type = None
        self.gate_range = None
        self.drain_range = None
        self.hardware_sweep = True
        self.integration_time = None
        self.current_compliance = None
        self.set_measure_delay = None
        self.averaging_count = 0 

        self.experiment_name = None
        self.measurement_name = None
        self.measurement_count = None
        self.working_folder = None

    def __del__(self):
        self.wait()

    def stop(self,timeout = -1):
        self.alive = False
        self.wait(timeout)

    def run(self):
        self.perform_measurement()

    def init_hardware(self, drain_keithley_resource, gate_keithley_resource):
        self.drain_keithley = Keithley24XX(drain_keithley_resource)
        self.gate_keithley = Keithley24XX(gate_keithley_resource)

    def open_experiment(self, working_folder,experiment_name, measurement_name, measurement_count):
        self.working_folder = working_folder
        self.experiment_name = experiment_name
        self.measurement_name = measurement_name
        self.measurement_count = measurement_count

    def prepare_experiment(self, measurement_type, gate_range, drain_range, hardware_sweep, integration_time, current_compliance, set_measure_delay, averaging_count):
        self.measurement_type = measurement_type
        self.gate_range = gate_range
        self.drain_range = drain_range
        self.hardware_sweep = hardware_sweep
        self.integration_time = integration_time
        self.current_compliance = current_compliance
        self.set_measure_delay = set_measure_delay
        self.averaging_count = averaging_count

    def __prepare_device(self,device):
        assert isinstance(device, Keithley24XX), "Wrong device type. Expected Keithley24XX"
        #abort operations
        device.Abort()
        #reset devices
        device.Reset()
        #clear Status
        device.ClearStatus()

        #switch beeper off
        device.SwitchBeeper(Keithley24XX.STATE_OFF)
        #switch off buffer control
        device.SelectTraceBufferControl(Keithley24XX.NEVER_TRACE_CONTROL)
        #clear buffer
        device.ClearBuffer()
        #switch concurrent measurement off
        device.SetConcurrentMeasurement(Keithley24XX.STATE_OFF)

        device.SetVoltageSourceFunction()
        
        device.SetCurrentSenseFunction()

        #configure autozero 
        device.SwitchAutoZeroOff()
        #configure nplc caching
        device.SwitchNPLCcachingOn()



        assert self.integration_time in INTEGRATION_SPEEDS, "Integration time is not set correct"

        nplc = 1
        if self.integration_time == INTEGRATION_SLOW:
            nplc = 1
        elif self.integration_time == INTEGRATION_MIDDLE:
            nplc = 0.1
        elif self.integration_time == INTEGRATION_FAST:
            nplc = 0.01
        device.SetVoltageNPLC(nplc)

        device.SetCurrentSenseCompliance(self.current_compliance)

        device.SetDelay(self.set_measure_delay)

        device.SetRepeatAverageFilter()

        if self.averaging_count>0:
            device.SetAverageFilterCount(self.averaging_count)
            device.SwitchAveragingFilterOn()
        else:
            device.SwitchAveragingFilterOff()


    def __prepare_hardware_sweep(self, indep_device, dep_device, sweep_range):
        assert isinstance(sweep_range, float_range), "sweep range is not of type float_range"
        
        indep_device.SetSweepStartVoltage(sweep_range.start)
        indep_device.SetSweepStopVoltage(sweep_range.stop)
        indep_device.SetSweepPoints(sweep_range.length)
        confirm_points = indep_device.GetSweepPoints()
        assert sweep_range.length == confirm_points, "range setting error"
        indep_device.SetSweepVoltageSourceMode()
        indep_device.SetSweepRanging(Keithley24XX.RANGING_AUTO)
        indep_device.SetSweepSpacing(Keithley24XX.SPACING_LIN)

        indep_device.SetTriggerCount(confirm_points)
        indep_device.SetTraceBufferSize(confirm_points)

        dep_device.SetTriggerCount(confirm_points)
        dep_device.SetTraceBufferSize(confirm_points)

        #indep_device.SelectTraceBufferControl(Keithley24XX.NEXT_TRACE_CONTROL)
        #dep_device.SelectTraceBufferControl(Keithley24XX.NEXT_TRACE_CONTROL)
        
        self.__configure_device_trigger_link(indep_device, dep_device)

    def __prepare_software_sweep(self,device):
        device.SetFixedVoltageSourceMode()

    def __configure_device_trigger_link(self, independent_device, dependent_device):
        assert isinstance(independent_device, Keithley24XX), "Wrong type for independent device"
        assert isinstance(dependent_device, Keithley24XX), "Wrong type for dependent device"
        
        dependent_device.SetTriggerSource(Keithley24XX.TRIG_TLIN)
        dependent_device.SetTriggerInputEventDetection(Keithley24XX.TRIG_SOUR_EVENT)
        dependent_device.SetTriggerInputLine(1)
        dependent_device.SetTriggerOutputLine(2)
        dependent_device.SetTriggerOutputEvent(Keithley24XX.TRIG_SENS_EVENT)

        independent_device.SetTriggerSource(Keithley24XX.TRIG_TLIN)
        independent_device.SetTriggerInputEventDetection(Keithley24XX.TRIG_SENS_EVENT)
        independent_device.SetTriggerOutputEvent(Keithley24XX.TRIG_SOUR_EVENT)
        independent_device.SetTriggerOutputLine(1)
        independent_device.SetTriggerInputLine(2)

    def __prepare_output_measurement(self):
        if self.hardware_sweep:
            print("using hardware sweep")
            self.__prepare_hardware_sweep(self.drain_keithley, self.gate_keithley, self.drain_range)
            self.__prepare_software_sweep(self.gate_keithley)
            
        else:
            print("using software sweep")
            self.__prepare_software_sweep(self.gate_keithley)
            self.__prepare_software_sweep(self.drain_keithley)

    def __prepare_transfer_measurement(self):
        if self.hardware_sweep:
            print("using hardware sweep")
            self.__prepare_hardware_sweep(self.gate_keithley,self.drain_keithley, self.gate_range)
            self.__prepare_software_sweep(self.drain_keithley)
        else:
            print("using software sweep")
            self.__prepare_software_sweep(self.drain_keithley)
            self.__prepare_software_sweep(self.gate_keithley)

    def prepare_hardware(self):
        self.__prepare_device(self.drain_keithley)
        self.__prepare_device(self.gate_keithley)

        if self.measurement_type == OUTPUT_MEASUREMENT:
            self.__prepare_output_measurement()
        elif self.measurement_type == TRANSFER_MEASUREMENT:
            self.__prepare_transfer_measurement()
        else:
            raise Exception("Measurement type error")

    def __make_beep(self,device):
        device.SwitchBeeperOn()
        device.PerformBeep()
        device.SwitchBeeperOff()

    def __activate_minimal_sensing_range(self, device):
       assert isinstance(device, Keithley24XX), "Wrong type for independent device"
       device.SetCurrentSenseRange(Keithley24XX.MIN_RANGE)
       device.SwitchCurrentAutoSenseRangeOn()

    def __perform_hardware_sweep(self, independent_device, independent_range, dependent_device, dependent_range, independent_variable_name, dependent_variable_name, visualize_independent_values):
        assert isinstance(independent_device, Keithley24XX), "Wrong type for independent device"
        assert isinstance(dependent_device, Keithley24XX), "Wrong type for dependent device"
        NUMBER_OF_ELEMENTS_READ_FROM_DEVICE = 5
        cols = "{0} voltage;{0} current;{0} timestamp;{1} voltage;{1} current;{1} timestamp".format(independent_variable_name.title(), dependent_variable_name.title()).split(';')
        filename_format = "{0}_{1}_{2}.dat"
        measurement_data_filename = os.path.join(self.working_folder,"MeasurmentData_{0}.dat".format(self.experiment_name))
        need_to_write_header = lambda: not os.path.isfile(measurement_data_filename)
        filename_option = "Filename"
        timestamp_option = "Timestamp"
        indep_var_option = "Independent Var"
        dep_var_option = "Dependent Var"
        dep_volt_option = "Dependent Voltage"

        #measurement_data_dataFrame = pd.DataFrame(columns = [filename_option, timestamp_option, indep_var_option, dep_var_option, dep_volt_option])

        self.__make_beep(dependent_device)
        self.experimentStarted.emit(dependent_range.length)

        #try:
        for count, dependent_voltage in enumerate(np.linspace(dependent_range.start, dependent_range.stop, dependent_range.length, True)):
            if not self.alive:
                print("Measurement abort")
                return

            self.measurementStarted.emit()#dependent_range.length)
            
            #update autozero values
            #independent_device.ForceAutoZeroUpdate()
            #dependent_device.ForceAutoZeroUpdate()

            self.__activate_minimal_sensing_range(independent_device)
            self.__activate_minimal_sensing_range(dependent_device)

            independent_device.OutputOn()
            dependent_device.OutputOn() 
            dependent_device.SetVoltageAmplitude(dependent_voltage)
                
            dependent_device.SelectTraceBufferControl(Keithley24XX.NEXT_TRACE_CONTROL)
            independent_device.SelectTraceBufferControl(Keithley24XX.NEXT_TRACE_CONTROL)

            independent_device.Initiate()
            dependent_device.Initiate()
                
            independent_device.WaitOperationCompleted()
            dependent_device.WaitOperationCompleted()

            independent_device.OutputOff()
            dependent_device.OutputOff() 
            
            strData = independent_device.ReadTraceData() #k.FetchData()
            strData2 = dependent_device.ReadTraceData() #k2.FetchData()

            independent_device.ClearBuffer()
            dependent_device.ClearBuffer()
                
            indep_data = np.fromstring(strData, sep=',')
            dep_data = np.fromstring(strData2, sep=',')
            
            indep_data = indep_data.reshape((independent_range.length,NUMBER_OF_ELEMENTS_READ_FROM_DEVICE)).T
            dep_data = dep_data.reshape((independent_range.length,NUMBER_OF_ELEMENTS_READ_FROM_DEVICE)).T

            indep_voltages, indep_currents, indep_resistances, indep_times, indep_status  = indep_data
            dep_voltages, dep_currents, dep_resistances, dep_times, dep_status  = dep_data

            res_array = np.vstack((indep_voltages, indep_currents, indep_times, dep_voltages, dep_currents, dep_times)).T
            
            visual_currents = indep_currents if visualize_independent_values else dep_currents
            self.measurementDataArrived.emit(("V{0} = {1:.5} V".format(dependent_variable_name[0], dependent_voltage), indep_voltages, visual_currents))
            #else:
            #    self.measurementDataArrived.emit(("V{0} = {1:.5} V".format(dependent_variable_name[0], dependent_voltage), indep_voltages, dep_currents))

            df = pd.DataFrame(res_array,index = np.arange(independent_range.length), columns = cols)
            timestamp =  datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = filename_format.format(self.measurement_name,self.measurement_count, timestamp )
            filepath = os.path.join(self.working_folder,filename) 
            df.to_csv(filepath, index = False)

            measurement_data_dataFrame = pd.DataFrame([[filename, 
                                                timestamp,
                                                independent_variable_name,
                                                dependent_variable_name,
                                                dependent_voltage]], index = [0], columns = [filename_option, 
                                                                                             timestamp_option, 
                                                                                             indep_var_option, 
                                                                                             dep_var_option, 
                                                                                             dep_volt_option])

            measurement_data_dataFrame.to_csv(measurement_data_filename, mode= 'a', header=need_to_write_header(), index = False)
            
            self.__increment_file_count()
            self.measurementProgressChanged.emit(count+1)
            self.measurementFinished.emit()
        #except Exception as e:
        #    independent_device.OutputOff()
        #    dependent_device.OutputOff() 
        

        

        self.__make_beep(dependent_device)
        self.experimentFinished.emit()
            #indep_voltages, indep_currents, indep_resistances, indep_times, indep_status  = data
            #dep_voltages, dep_currents, dep_resistances, dep_times, dep_status  = data2
            #print("VG={0}".format(dependent_voltage))
            #print(dep_voltages)
            #print(indep_currents)

    def __increment_file_count(self):
        self.measurement_count +=1
        self.measurementNextFile.emit()

    def _perform_hardware_sweep_for_measurement_type(self):
        drain_var, gate_var = ("drain","gate")
        if self.measurement_type == OUTPUT_MEASUREMENT:
            self.__perform_hardware_sweep(self.drain_keithley, self.drain_range,self.gate_keithley,self.gate_range, drain_var, gate_var, True)
        elif self.measurement_type == TRANSFER_MEASUREMENT:
            self.__perform_hardware_sweep(self.gate_keithley,self.gate_range, self.drain_keithley, self.drain_range, gate_var, drain_var, False)



    def _perform_software_sweep(self):
        raise NotImplementedError("Software sweep is in the development")
        #if self.measurement_type == OUTPUT_MEASUREMENT:
        #    pass
        #elif self.measurement_type == TRANSFER_MEASUREMENT:
        #    pass

    def perform_measurement(self):
        if self.hardware_sweep:
            self._perform_hardware_sweep_for_measurement_type()
        else:
            self._perform_software_sweep()


    
    
class QVoltageValidator(QtGui.QRegExpValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        regex = QtCore.QRegExp("^-?(?:0|[1-9]\d*).?(\d*)\s*(?:[yzafpnumcdhkMGTPEZY])?[V]")   #"(\d+).?(\d*)\s*(m|cm|km)")
        self.setRegExp(regex)   

def extract_from_experiment_measurement_names(experiment_name, measurement_name):
    pass

EXPERIMENT_NAME_FORMAT = "{w}_{c}_{exp}"
MEASUREMENT_NAME_FORMAT = "t{trans}-{type}"


def compose_wafer_chip_transistor_to_experiment_measurement_names(experiment, measurement, wafer,chip,transistor,measurement_type):
    exp_name = EXPERIMENT_NAME_FORMAT.format(w = wafer, c = chip, exp = experiment)
    meas_name = MEASUREMENT_NAME_FORMAT.format(trans = transistor, type = measurement_type)
    if measurement:
        meas_name = "_".join([meas_name,measurement])

    return (exp_name,meas_name)

def convert_value_to_volts(ureg, value):
    assert isinstance(ureg, UnitRegistry)
    try:
          v = ureg(value)
          if not isinstance(v,pint.quantity._Quantity):
              v = float(v) * ureg.volt
          print("{0} {1}".format(v.magnitude, v.units))
          v.ito(ureg.volt)
          return v.magnitude
    except Exception as e:
          print("error while handling value")
          print(str(e))
          return 0.0

def string_to_volt_converter(ureg):
    def wrapper(value):
       return convert_value_to_volts(ureg, value)
    return wrapper

#def setupFolderBrowseButton(parent, ):
#        self.popMenu = QtGui.QMenu(parent)
#        self.selected_folder_context_menu_item = QtGui.QAction(self)
#        self.selected_folder_context_menu_item.triggered.connect(self.on_open_folder_in_explorer)
#        self.popMenu.addAction(self.selected_folder_context_menu_item)
#        self.popMenu.addSeparator()

#        #open_folder_action = QtGui.QAction("Open in explorer...",self)
#        #open_folder_action.triggered.connect(self.on_open_folder_in_explorer)
#        #self.popMenu.addAction(open_folder_action)
        
#        self.folderBrowseButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
#        self.folderBrowseButton.customContextMenuRequested.connect(self.on_folder_browse_button_context_menu)

#from ui_iv_measurement import Ui_MainWindow

mainViewBase, mainViewForm = uic.loadUiType("UI/UI_IV_Measurement_v3.ui")
class MainView(mainViewBase, mainViewForm): #Ui_MainWindow): 
    ureg = UnitRegistry()
    #str_to_volt_converter = string_to_volt_converter(ureg)
    config_filename = 'configuration.ini'
    config_file_section_name = "UI_Options"
    (measurement_type_option,
                drain_keithley_resource_option, 
                gate_keithley_resource_option, 
                drain_start_option, 
                drain_stop_option, 
                drain_points_option, 
                gate_start_option, 
                gate_stop_option, 
                gate_points_option, 
                hardware_sweep_option, 
                integration_time_option, 
                current_compliance_option,
                set_measure_delay_option,
                experiment_name_option,
                measurement_name_option,
                measurement_count_option,
                working_directory_option,
                averaging_count_option) = ("type",
                                             "ds_resource",
                                             "gs_resource",
                                             "drain_start",
                                             "drain_stop",
                                             "drain_points",
                                             "gate_start",
                                             "gate_stop" ,
                                             "gate_points" ,
                                             "hardware_sweep",
                                             "integration_time",
                                             "current_compliance",
                                             "set_measure_delay",
                                             "experiment_name",
                                             "measuremtn_name",
                                             "measurement_count",
                                             "working_directory",
                                             "averaging_count")

    def __init__(self, parent = None):
        super(mainViewBase, self).__init__(parent)
        #super().__init__()

        self.configuration = configparser.RawConfigParser()
        self.configuration.read(self.config_filename)
        self.working_directory = ""
        self.setupUi()
        self.experiment = None
        

    def show_message(self,message, timeout = 0):
        if message:
            self.statusbar.showMessage(message, timeout)

    @QtCore.pyqtSlot()
    def on_folderBrowseButton_clicked(self):
        print("Select folder")
        
        folder_name = QtGui.QFileDialog.getExistingDirectory(self,caption="Select Folder", directory = self.working_directory)
        if not folder_name:
            return False

        folder_name = os.path.abspath(folder_name)
        
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText(folder_name)
        msg.setStandardButtons(QtGui.QMessageBox.Ok)# | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()
        if retval:
            self.working_directory = folder_name
            self.configuration[MainView.config_file_section_name][self.working_directory_option] = self.working_directory
            self.set_selected_folder_context_menu_item_text(self.working_directory)
        return retval

    def setupFolderBrowseButton(self):
        self.popMenu = QtGui.QMenu(self)
        self.selected_folder_context_menu_item = QtGui.QAction(self)
        self.selected_folder_context_menu_item.triggered.connect(self.on_open_folder_in_explorer)
        self.popMenu.addAction(self.selected_folder_context_menu_item)
        self.popMenu.addSeparator()

        #open_folder_action = QtGui.QAction("Open in explorer...",self)
        #open_folder_action.triggered.connect(self.on_open_folder_in_explorer)
        #self.popMenu.addAction(open_folder_action)
        
        self.folderBrowseButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.folderBrowseButton.customContextMenuRequested.connect(self.on_folder_browse_button_context_menu)
        
    def set_selected_folder_context_menu_item_text(self,text):
        self.selected_folder_context_menu_item.setText(text)

    def on_open_folder_in_explorer(self):
        print("opening folder")
        print(self.working_directory)
        request = 'explorer "{0}"'.format(self.working_directory)
        print(request)
        os.system(request)

    def on_folder_browse_button_context_menu(self,point):
        self.popMenu.exec_(self.folderBrowseButton.mapToGlobal(point))

    def setVisibleToAdvancedSaveDialog(self,state):
        if state == QtCore.Qt.Unchecked:
            self.ui_advanced_dialog_widget.hide()
        else:
            self.ui_advanced_dialog_widget.show()

    

    def setupUi(self):
        super(MainView, self).setupUi(self)
        self.ui_ds_start.setValidator(QVoltageValidator())
        self.ui_ds_stop.setValidator(QVoltageValidator())
        self.ui_gs_start.setValidator(QVoltageValidator())
        self.ui_gs_stop.setValidator(QVoltageValidator())
        self.ui_current_compliance.setValidator(QtGui.QDoubleValidator())
        self.ui_set_meas_delay.setValidator(QtGui.QDoubleValidator())
        self.setupFolderBrowseButton()

        self.ui_use_advanced_dialog.stateChanged.connect(self.setVisibleToAdvancedSaveDialog)
        self.setVisibleToAdvancedSaveDialog(self.ui_use_advanced_dialog.checkState())




        self.ivPlotWidget = IV_PlotWidget(self.ui_plot)

        self.ui_measurement_type.addItems(MEASUREMENT_TYPES)
        gpib_resources = get_available_gpib_resources()
        self.ui_ds_resource.addItems(gpib_resources)
        self.ui_gs_resource.addItems(gpib_resources)
        self.ui_integration_time.addItems(INTEGRATION_SPEEDS)
        integration_count_list = list(map(str,[0,1,5,10,20,40,50,80,100]))
        self.ui_averaging_count.addItems(integration_count_list)

        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progressBar)


        self.__setup_ui_from_config()

        #self.ui_ds_start.valueChanged.connect(self.__ui_range_changed)
        #self.ui_ds_stop.valueChanged.connect(self.__ui_range_changed)
        #self.ui_ds_points.valueChanged.connect(self.__ui_range_changed)
        #self.ui_gs_start.valueChanged.connect(self.__ui_range_changed)
        #self.ui_gs_stop.valueChanged.connect(self.__ui_range_changed)
        #self.ui_gs_points.valueChanged.connect(self.__ui_range_changed)
        self.ui_measurement_type.currentIndexChanged.connect(self.__ui_measurement_type_changed)
        

    def __initialize_control_buttons(self):
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        
    def __set_ui_experiment_started(self):
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)

    
        #config = configparser.ConfigParser()
        #config.read(self.config_filename)

    def __ui_measurement_type_changed(self):
        meas_type = self.__get_ui_measurement_type()
        indep_var = "Drain"
        if meas_type == OUTPUT_MEASUREMENT:
            self.__ui_range_changed(TRANSFER_MEASUREMENT)
        elif meas_type == TRANSFER_MEASUREMENT:
            indep_var = "Gate"
            self.__ui_range_changed(OUTPUT_MEASUREMENT)
        else:
            raise ValueError("wrong measurement type")
        
        self.__setup_ui_range_from_config()
        
        #indep_var = "Drain" if meas_type == OUTPUT_MEASUREMENT else "Gate"
        self.ivPlotWidget.set_independent_variable_name(indep_var, "V")

    def __set_combobox_index_corresponding_to_text(self,combobox, text):
        index = combobox.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
           combobox.setCurrentIndex(index)

    def __setup_ui_range_from_config(self):
        config = self.configuration
        main_section = MainView.config_file_section_name
        measurement_type = self.__get_ui_measurement_type() #config[main_section][self.measurement_type_option]
        if config.has_section(measurement_type):
            #ds_start = float(config[measurement_type][self.drain_start_option])
            #self.ui_ds_start.setValue(ds_start)
            ds_start = config[measurement_type][self.drain_start_option]
            self.ui_ds_start.setText(ds_start)

            #ds_stop = float(config[measurement_type][self.drain_stop_option])
            #self.ui_ds_stop.setValue(ds_stop)
            ds_stop = config[measurement_type][self.drain_stop_option]
            self.ui_ds_stop.setText(ds_stop)

            ds_points = int(config[measurement_type][self.drain_points_option])
            self.ui_ds_points.setValue(ds_points)


            #gs_start = float(config[measurement_type][self.gate_start_option])
            #self.ui_gs_start.setValue(gs_start)
            gs_start = config[measurement_type][self.gate_start_option]
            self.ui_gs_start.setText(gs_start)

            #gs_stop = float(config[measurement_type][self.gate_stop_option])
            #self.ui_gs_stop.setValue(gs_stop)
            gs_stop = config[measurement_type][self.gate_stop_option]
            self.ui_gs_stop.setText(gs_stop)
            
            gs_points = int(config[measurement_type][self.gate_points_option])
            self.ui_gs_points.setValue(gs_points)

    def __setup_ui_from_config(self):
        config = self.configuration
        #config = configparser.RawConfigParser()
        #config.read(self.config_filename)

        main_section = MainView.config_file_section_name
        if not config.has_section(main_section):
            return False
        
        measurement_type = config[main_section][self.measurement_type_option]
        self.__set_combobox_index_corresponding_to_text(self.ui_measurement_type, measurement_type)
        
        drain_keithley_resource =  config[main_section][self.drain_keithley_resource_option]
        self.__set_combobox_index_corresponding_to_text(self.ui_ds_resource, drain_keithley_resource)

        gate_keithley_resource = config[main_section][self.gate_keithley_resource_option]
        self.__set_combobox_index_corresponding_to_text(self.ui_gs_resource, gate_keithley_resource)

        hardware_sweep = bool(config[main_section][self.hardware_sweep_option])


        integration_time = config[main_section][self.integration_time_option]
        self.__set_combobox_index_corresponding_to_text(self.ui_integration_time, integration_time)

        #current_compliance = float(config[main_section][self.current_compliance_option])
        #self.ui_current_compliance.setValue(current_compliance)
        current_compliance = config[main_section][self.current_compliance_option]
        self.ui_current_compliance.setText(current_compliance)


        #set_measure_delay= float(config[main_section][self.set_measure_delay_option])
        #self.ui_set_meas_delay.setValue(set_measure_delay)
        set_measure_delay= config[main_section][self.set_measure_delay_option]
        self.ui_set_meas_delay.setText(set_measure_delay)

        experiment_name = config[main_section][self.experiment_name_option]
        self.ui_experimentName.setText(experiment_name)

        measurement_name = config[main_section][self.measurement_name_option]
        self.ui_measurementName.setText(measurement_name)

        measurement_count = int(config[main_section][self.measurement_count_option])
        self.ui_measurementCount.setValue(measurement_count)

        working_directory = config[main_section][self.working_directory_option]
        self.working_directory = working_directory
        self.set_selected_folder_context_menu_item_text(self.working_directory)

        averaging_count = config[main_section][self.averaging_count_option]
        self.__set_combobox_index_corresponding_to_text(self.ui_averaging_count, averaging_count)
        


        self.__setup_ui_range_from_config()
        
    
    def __get_ui_measurement_type(self):
        return self.ui_measurement_type.currentText()

    def __get_range_values_from_ui(self):
        ds_start = convert_value_to_volts(self.ureg, self.ui_ds_start.text()) #float(self.ui_ds_start.text())
        ds_stop = convert_value_to_volts(self.ureg, self.ui_ds_stop.text()) #float(self.ui_ds_stop.text())
        gs_start = convert_value_to_volts(self.ureg, self.ui_gs_start.text())#float(self.ui_gs_start.text())
        gs_stop = convert_value_to_volts(self.ureg, self.ui_gs_stop.text())#float(self.ui_gs_stop.text())
        drain_range = float_range(ds_start, ds_stop, len = self.ui_ds_points.value())
        gate_range =  float_range(gs_start, gs_stop, len = self.ui_gs_points.value())
        #drain_range = float_range(self.ui_ds_start.value(), self.ui_ds_stop.value(), len = self.ui_ds_points.value())
        #gate_range =  float_range(self.ui_gs_start.value(), self.ui_gs_stop.value(), len = self.ui_gs_points.value())
        return (drain_range, gate_range)



    def __get_values_from_ui(self):
        meas_type = self.ui_measurement_type.currentText()

        drain_keithley_resource = self.ui_ds_resource.currentText()
        gate_keithley_resource = self.ui_gs_resource.currentText()

        #drain_range = float_range(self.ui_ds_start.value(), self.ui_ds_stop.value(), len = self.ui_ds_points.value())
        #gate_range =  float_range(self.ui_gs_start.value(), self.ui_gs_stop.value(), len = self.ui_gs_points.value())

        hardware_sweep = self.ui_hardware_sweep.isChecked()
        integration_time = self.ui_integration_time.currentText()
        current_compliance = float(self.ui_current_compliance.text()) #.value()
        set_measure_delay = float(self.ui_set_meas_delay.text()) #.value()
        averaging_count = int(self.ui_averaging_count.currentText())

        experiment_name = self.ui_experimentName.text()
        measurement_name = self.ui_measurementName.text()
        measurement_count = self.ui_measurementCount.value()

        if self.ui_use_advanced_dialog.checkState() != QtCore.Qt.Unchecked:
            wafer_name = self.ui_wafer_name.text()
            chip_name = self.ui_chip_name.text()
            transistor_number = self.ui_transistor_number.value()
            measurement_type = self.__get_ui_measurement_type()
            if meas_type == OUTPUT_MEASUREMENT:
                measurement_type = "IVds"
            elif meas_type == TRANSFER_MEASUREMENT:
                measurement_type = "IVg"
            
            
            (experiment_name, measurement_name) = compose_wafer_chip_transistor_to_experiment_measurement_names(experiment_name, measurement_name, wafer_name,chip_name, transistor_number, measurement_type)
            
                



        return (meas_type,
                drain_keithley_resource, 
                gate_keithley_resource, 
                #drain_range, 
                #gate_range, 
                hardware_sweep, 
                integration_time, 
                current_compliance,
                set_measure_delay,
                averaging_count,
                experiment_name,
                measurement_name,
                measurement_count)

    def __ui_range_changed(self, measurement_type):
        drain_range, gate_range = self.__get_range_values_from_ui()
        #measurement_type = self.__get_ui_measurement_type()
        if not self.configuration.has_section(measurement_type):
            self.configuration.add_section(measurement_type)

        self.configuration[measurement_type][self.drain_start_option] = str(drain_range.start)
        self.configuration[measurement_type][self.drain_stop_option] = str(drain_range.stop)
        self.configuration[measurement_type][self.drain_points_option] = str(drain_range.length)
        self.configuration[measurement_type][self.gate_start_option] = str(gate_range.start)
        self.configuration[measurement_type][self.gate_stop_option] = str(gate_range.stop)
        self.configuration[measurement_type][self.gate_points_option] = str(gate_range.length)
        self.write_config_file()
        
        


    def data_arrived(self, data):
        name, x,y = data
        self.ivPlotWidget.add_curve(x,y,name)

    def on_next_file(self):
        meas_count = self.ui_measurementCount.value()
        self.ui_measurementCount.setValue(meas_count+1)

    def _on_measurement_progress_changed(self,progress):
        print("progress_changed {0}".format(progress))
        self.progressBar.setValue(progress)

    def _on_experiment_started(self, max_experiment_count):
        self.progressBar.setRange(0,max_experiment_count)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        

    def _on_experiment_finished(self):
        self.show_message("experiment finished", 1000)

        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText("Measurement completed!!!")
        msg.setInformativeText("Additional info about measurement")
        msg.setWindowTitle("Measurement completed")
        msg.setDetailedText("Data saved in folder: {0}".format(self.working_directory))
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msg.exec_()

        self.progressBar.setVisible(False)
        self.__initialize_control_buttons()
       

    def _on_measurement_started(self): #, max_experiment_count):
        self.show_message("new measurement started", 1000)
        #self.progressBar.setRange(0,max_experiment_count)
        ##self.progressBar.setValue(0)
        ##self.progressBar.setVisible(True)
        

    def _on_measurement_finished(self):
        self.show_message("measurement finished", 5000)
        
        #msg = QtGui.QMessageBox()
        #msg.setIcon(QtGui.QMessageBox.Information)
        #msg.setText("Measurement completed!!!")
        #msg.setInformativeText("Additional info about measurement")
        #msg.setWindowTitle("Measurement completed")
        #msg.setDetailedText("Data saved in folder: {0}".format(self.working_directory))
        #msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        #retval = msg.exec_()

        #self.progressBar.setVisible(False)


    def initialize_experiment(self):
        self.experiment = IV_Experiment()

        self.experiment.experimentStarted.connect(self._on_experiment_started)
        self.experiment.experimentFinished.connect(self._on_experiment_finished)

        self.experiment.measurementStarted.connect(self._on_measurement_started)
        self.experiment.measurementFinished.connect(self._on_measurement_finished)
        self.experiment.measurementProgressChanged.connect(self._on_measurement_progress_changed)

        self.experiment.measurementDataArrived.connect(self.data_arrived)
        self.experiment.measurementNextFile.connect(self.on_next_file)


        (measurement_type,
         drain_keithley_resource, 
         gate_keithley_resource, 
         #drain_range, 
         #gate_range, 
         hardware_sweep, 
         integration_time, 
         current_compliance,
         set_measure_delay,
         averaging_count,
         experiment_name,
         measurement_name,
         measurement_count) = self.__get_values_from_ui()
        (drain_range, gate_range) = self.__get_range_values_from_ui()

        
        self.experiment.init_hardware(drain_keithley_resource, gate_keithley_resource)
        self.experiment.prepare_experiment(measurement_type,
                                           gate_range,
                                           drain_range,
                                           hardware_sweep,
                                           integration_time,
                                           current_compliance,
                                           set_measure_delay,
                                           averaging_count)
        self.experiment.prepare_hardware()
        self.experiment.open_experiment(self.working_directory, experiment_name, measurement_name, measurement_count)
        #exp.prepare_experiment(TRANSFER_MEASUREMENT,float_range(0,1.5,len=101),float_range(-1,1,len=5), True, INTEGRATION_MIDDLE, 0.001, 0.001)
        #exp.prepare_hardware()


    @QtCore.pyqtSlot()
    def on_startButton_clicked(self):
        print("start")
        #x = np.linspace(-1,1,101)
        #y = np.linspace(-10,10,101)
        #self.ivPlotWidget.add_curve(x,y,"test")
        self.ivPlotWidget.clear_curves()
        self.initialize_experiment()
        self.experiment.start()
        self.__set_ui_experiment_started()
        #self.initialize_experiment()
        #self.experiment.start()
        

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        print("stop")
        if self.experiment:
            self.experiment.stop(5000)
            print("waiting for measurement stop")
            self.experiment.terminate()
            self.experiment.wait()
            print("experiment stopped")
            self.__initialize_control_buttons()
            
        #self.ivPlotWidget.clear_curves()
        #self.experiment.stop()
        
    def write_config_file(self):
        with open(self.config_filename,'w') as configfile:
            self.configuration.write(configfile)


    def closeEvent(self,event):

        (measurement_type,
                drain_keithley_resource, 
                gate_keithley_resource, 
                #drain_range, 
                #gate_range, 
                hardware_sweep, 
                integration_time, 
                current_compliance,
                set_measure_delay,
                averaging_count,
                experiment_name,
                measurement_name,
                measurement_count) = self.__get_values_from_ui()

        (drain_range, gate_range) = self.__get_range_values_from_ui()

        config = self.configuration
        
        main_section = MainView.config_file_section_name
        has_section = config.has_section(main_section)
        if not has_section:
            config.add_section(main_section)

        config[main_section] = {self.measurement_type_option: str(measurement_type),
                           self.drain_keithley_resource_option: str(drain_keithley_resource),
                            self.gate_keithley_resource_option: str(gate_keithley_resource),
                            self.hardware_sweep_option: str(hardware_sweep ),
                            self.current_compliance_option: str(current_compliance),
                            self.integration_time_option: str(integration_time ),
                            self.set_measure_delay_option: str(set_measure_delay),
                            self.averaging_count_option: str(averaging_count),
                            self.experiment_name_option: str(experiment_name),
                            self.measurement_name_option: str(measurement_name),
                            self.measurement_count_option: str(measurement_count),
                            self.working_directory_option: str(self.working_directory )}
        
        

        has_section = config.has_section(measurement_type)
        if not has_section:
            config.add_section(measurement_type)

        config[measurement_type] = {
            self.drain_start_option: str(drain_range.start),
            self.drain_stop_option: str(drain_range.stop),
            self.drain_points_option : str(drain_range.length),
            self.gate_start_option: str(gate_range.start),
            self.gate_stop_option:str( gate_range.stop),
            self.gate_points_option : str(gate_range.length),
            }
        self.write_config_file()

      
def ui_application():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyIV")
    app.setStyle("cleanlooks")
    app.setWindowIcon(QtGui.QIcon('pyiv.ico'))
    wnd = MainView()
    wnd.show()
    return app.exec_()

def console_application():
    exp = IV_Experiment()
    exp.init_hardware('GPIB0::5::INSTR', 'GPIB0::16::INSTR')
    exp.prepare_experiment(TRANSFER_MEASUREMENT,float_range(0,1.5,len=101),float_range(-1,1,len=5), True, INTEGRATION_MIDDLE, 0.001, 0.001,0)
    exp.prepare_hardware()
    exp.open_experiment("","experiment", "test_meas",1)
    #exp.start()
    #exp.stop()
    #exp.wait()
    #exp.perform_measurement()
    exp.perform_measurement()
    return 0


if __name__== "__main__":
    sys.exit(ui_application())
    #sys.exit(console_application())


   
    
   

    
    
   
