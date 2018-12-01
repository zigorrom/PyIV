import sys
import os
import time

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
from pyiv_model import PyIV_model, CharacterizarionMode, SweepMode, CustomizationEnum

from keithley24xx import Keithley24XX

class StopExperimentException(Exception):
    pass

class SweepMeasurement():
    def __init__(self, devices):
        pass
    
    def add_device(self, device):
        pass

    


class PyIVexperiment(QThread):
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


    def initialize_settings(self, settings):
        if isinstance(settings, PyIV_model):
            raise TypeError("Settings object has wrong type!")
        
        self.settings = settings

    def assert_is_running(self):
        if self._stop_request:
            raise StopExperimentException()

    def run(self):
        self.perform_experiment()

    def stop(self):
        self._stop_request = True

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

    def perform_two_terminal_software_sweep(self, independent_device, independent_range, dependent_device, dependent_range, independent_variable_name, dependent_variable_name):
        pass

    def perform_two_terminal_hardware_sweep(self, independent_device, independent_range, dependent_device, dependent_range, independent_variable_name, dependent_variable_name):
        pass

    def perform_transfer_measurement(self):
        drain_smu = None
        drain_range = None
        gate_smu = None
        gate_range = None
        sweep_mode = self.settings.sweep_mode
        if sweep_mode is SweepMode.Hardware:
            self.perform_two_terminal_hardware_sweep(
                gate_smu,
                gate_range,
                drain_smu,
                drain_range,
                "Gate",
                "Drain"
            )

        elif sweep_mode is SweepMode.Software:
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
        drain_range = None
        gate_smu = None
        gate_range = None
        sweep_mode = self.settings.sweep_mode
        if sweep_mode is SweepMode.Hardware:
            self.perform_two_terminal_hardware_sweep(
                drain_smu,
                drain_range,
                gate_smu,
                gate_range,
                "Drain",
                "Gate"
            )

        elif sweep_mode is SweepMode.Software:
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
        

    def perform_timetrace_measurement(self):
        raise NotImplementedError()

    def perform_experiment(self):
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



    
    