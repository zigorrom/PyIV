import sys
import os
import time
import traceback
from PyQt4 import QtCore
from PyQt4.QtCore import QRunnable
from pyiv_model import PyIV_model, CharacterizarionMode, SweepMode, CustomizationEnum
import pyfans.ranges.modern_range_editor as mredit
from keithley24xx import Keithley24XX

class StopExperimentException(Exception):
    pass

class SweepMeasurement():
    def __init__(self, devices):
        pass
    
    def add_device(self, device):
        pass

    
class ExperimentSignals(QtCore.QObject):
    sigExperimentStarted = QtCore.pyqtSignal()
    sigExperimentFinished = QtCore.pyqtSignal()
    sigMeasurementStarted = QtCore.pyqtSignal()
    sigMeasurementFinished = QtCore.pyqtSignal()
    sigMeasurementProgressChanged = QtCore.pyqtSignal()
    sigExperimentProgressChanged = QtCore.pyqtSignal()
    sigMeasurementDataPointReady = QtCore.pyqtSignal()
    sigMeasurementDataCurveReady = QtCore.pyqtSignal()



class PyIVexperiment(QRunnable):
    sigExperimentStarted = QtCore.pyqtSignal()
    sigExperimentFinished = QtCore.pyqtSignal()
    sigMeasurementStarted = QtCore.pyqtSignal()
    sigMeasurementFinished = QtCore.pyqtSignal()
    
    sigNewMeasurementCurveStarted = QtCore.pyqtSignal()
    sigNewMeasurementCurveFinished = QtCore.pyqtSignal()
    
    sigNewMeasuredCurveAquired = QtCore.pyqtSignal()
    sigNewMeasuredPointAquired = QtCore.pyqtSignal()



    def __init__(self):
        super().__init__()
        self.setings = None
        self._stop_request = False
        self.signals = ExperimentSignals()


    def initialize_settings(self, settings):
        if not isinstance(settings, PyIV_model):
            raise TypeError("Settings object has wrong type!")
        
        self.settings = settings

    def assert_is_running(self):
        if self._stop_request:
            raise StopExperimentException()

    def __del__(self):
        print("Deleting object")

    @QtCore.pyqtSlot()
    def run(self):
        self.perform_experiment()

    def stop(self):
        self._stop_request = True
        # self.wait()

    def init_hardware(self):
        pass

    def open_experiment(self):
        pass

    def close_experiment(self):
        pass

    def __prepare_device(self, device):
        pass

    def __prepare_hardware_sweep(self):
        pass

    def __prepare_software_sweep(self):
        pass

    def __configure_device_trigger_link(self):
        pass

    def __make_beep(self, device):
        device.SwitchBeeperOn()
        device.PerformBeep()
        device.SwitchBeeperOff()

    def __activate_minimal_sensing_range(self, device):
        assert isinstance(device, Keithley24XX), "Wrong type for independent device"
        device.SetCurrentSenseRange(Keithley24XX.MIN_RANGE)
        device.SwitchCurrentAutoSenseRangeOn()

    def __increment_file_count(self):
       pass

    def test(self):
        prev_time = time.time()
        while True:
            self.assert_is_running()
            current_time = time.time()
            time_diff = current_time - prev_time
            if time_diff > 1:
                print(current_time)
                prev_time = current_time

    def perform_two_terminal_software_sweep(self, independent_device, independent_range, dependent_device, dependent_range, independent_variable_name, dependent_variable_name):
        # self.test()
        print("running software sweep")
        for i, dependent_voltage in enumerate(dependent_range):
            self.assert_is_running()
            print("{0} voltage = {1}".format(dependent_variable_name, dependent_voltage))
            print("|\t{0}".format(independent_variable_name))
            for j, independent_voltage in enumerate(independent_range):
                self.assert_is_running()
                print("|\t{0}".format(independent_voltage))
                time.sleep(0.01)


    def perform_two_terminal_hardware_sweep(self, independent_device, independent_range, dependent_device, dependent_range, independent_variable_name, dependent_variable_name):
        print("running hardware sweep")
        for i, dependent_voltage in enumerate(dependent_range):
            self.assert_is_running()
            print("{0} voltage = {1}".format(dependent_variable_name, dependent_voltage))
            print("|\t{0}".format(independent_variable_name))
            for j, independent_voltage in enumerate(independent_range):
                self.assert_is_running()
                print("|\t{0}".format(independent_voltage))
                time.sleep(0.01)
    

    def initialize_hardware_sweep(self, independent_device, dependent_device):
        pass
    
    def initialize_software_sweep(self, independent_device, dependent_device):
        pass


    def perform_transfer_measurement(self):
        drain_smu = None
        drain_range = mredit.RangeHandlerFactory.createHandler(self.settings.drain_source_voltage_range)
        gate_smu = None
        gate_range = mredit.RangeHandlerFactory.createHandler(self.settings.gate_source_voltage_range)
        sweep_mode = self.settings.sweep_mode

        if sweep_mode is SweepMode.Hardware:
            self.initialize_hardware_sweep(gate_smu, drain_smu)
            self.perform_two_terminal_hardware_sweep(
                gate_smu,
                gate_range,
                drain_smu,
                drain_range,
                "Gate",
                "Drain"
            )

        elif sweep_mode is SweepMode.Software:
            self.initialize_software_sweep(gate_smu, drain_smu)
            self.perform_two_terminal_software_sweep(
                gate_smu,
                gate_range,
                drain_smu,
                drain_range,
                "Gate",
                "Drain"
            )

        else:
            raise ValueError("wrong sweep mode")


    def perform_output_measurement(self):
        drain_smu = None
        drain_range = mredit.RangeHandlerFactory.createHandler(self.settings.drain_source_voltage_range)
        gate_smu = None
        gate_range = mredit.RangeHandlerFactory.createHandler(self.settings.gate_source_voltage_range)
        sweep_mode = self.settings.sweep_mode

        if sweep_mode is SweepMode.Hardware:
            self.initialize_hardware_sweep(drain_smu, gate_smu)
            self.perform_two_terminal_hardware_sweep(
                drain_smu,
                drain_range,
                gate_smu,
                gate_range,
                "Drain",
                "Gate"
            )

        elif sweep_mode is SweepMode.Software:
            self.initialize_software_sweep(drain_smu, gate_smu)
            self.perform_two_terminal_software_sweep(
                drain_smu,
                drain_range,
                gate_smu,
                gate_range,
                "Drain",
                "Gate"
            )

        else:
            raise ValueError("wrong sweep mode")

    


    def perform_custom_measurement(self):
        order_list = self.settings.custom_order
        print(order_list)
        custom_list = list()
        for item in order_list:
            if item is CustomizationEnum.Vbg:
                device = None #Keithley24XX(self.settings.back_gate_source_smu)
                rng = self.settings.back_gate_voltage_range
                name = "Back Gate"
                val_tuple = (device, rng, name)
                custom_list.append(val_tuple)
            
            elif item is CustomizationEnum.Vds:
                device = None #Keithley24XX(self.settings.drain_source_smu)
                rng = self.settings.drain_source_voltage_range
                name = "Drain Source"
                val_tuple = (device, rng, name)
                custom_list.append(val_tuple)
            
            elif item is CustomizationEnum.Vgs:
                device = None #Keithley24XX(self.settings.gate_source_smu)
                rng = self.settings.gate_source_voltage_range
                name = "Gate Source"
                val_tuple = (device, rng, name)
                custom_list.append(val_tuple)
        
        




        # self.test()

    def perform_timetrace_measurement(self):
        self.test()

    def perform_experiment(self):
        try:
            self.signals.sigExperimentStarted.emit()

            characterization_mode = self.settings.characterization_mode
            if characterization_mode is CharacterizarionMode.Transfer:
                self.perform_transfer_measurement()

            elif characterization_mode is CharacterizarionMode.Output:
                self.perform_output_measurement()

            elif characterization_mode is CharacterizarionMode.Timetrace:
                self.perform_timetrace_measurement()

            elif characterization_mode is CharacterizarionMode.Custom:
                self.perform_custom_measurement()

            else:
                raise ValueError("No such characterization mode")

        except StopExperimentException:
            print("experiment stop requested")

        except Exception as e:
            traceback.print_exc()

        finally:
            print("Finilizing experiment")
            self.signals.sigExperimentFinished.emit()




        




    
    