from enum import Enum
import pyfans.utils.ui_helper as uih

class CharacterizarionMode(Enum):
    Output = 0
    Transfer = 1
    Timetrace = 2

class SweepMode(Enum):
    Hardware = 0
    Software = 1

def assert_characterization_type(function):
    return uih.__assert_isinstance_wrapper(function, CharacterizarionMode)

def assert_sweep_mode(function):
    return uih.__assert_isinstance_wrapper(function, SweepMode)

# def assert_voltage_range(function):
#     return uih.__assert_isinstance_wrapper(function, SweepMode)

class PyIV_model(uih.NotifyPropertyChanged):
    def __init__(self):
        super().__init__()
        self._characterization_mode = None
        self._sweep_mode = None

        self._drain_source_voltage = None
        self._gate_source_voltage = None
        self._drain_source_voltage_range = None
        self._gate_source_voltage_range = None

        self._ds_smu = None
        self._gs_smu = None
        self._bg_smu = None

        self._integration_time = None
        self._current_compliance = None
        self._set_meas_delay = None
        self._average_count = None

        self._use_extended_save_dialog = None
        self._experiment_name = None
        self._measurement_name = None
        self._measurement_count = None
        self._working_directory = None
        self._wafer_name = None
        self._chip_name = None
        self._transistor_number = None

        self._transfer_button_checked = None
        self._output_button_checked = None
        self._timetrace_button_checked = None
        self._hw_sweep_button_checked = None
        self._sw_sweep_button_checked = None


    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state
        super().__init__()
        
    
    @property
    def characterization_mode(self):
        return self._characterization_mode

    @characterization_mode.setter
    @assert_characterization_type
    def characterization_mode(self, value):
        if self._characterization_mode == value:
            return 
        
        self._characterization_mode = value
        self.onPropertyChanged("characterization_mode", self, value)

    @property
    def sweep_mode(self):
        return self._sweep_mode

    @sweep_mode.setter
    @assert_sweep_mode
    def sweep_mode(self, value):
        if self._sweep_mode == value:
            return
        
        self._sweep_mode = value
        self.onPropertyChanged("sweep_mode", self, value)

    @property
    def drain_source_voltage(self):
        return self._drain_source_voltage

    @drain_source_voltage.setter
    @uih.assert_int_or_float_argument
    def drain_source_voltage(self, value):
        if self._drain_source_voltage == value:
            return 

        self._drain_source_voltage = value
        self.onPropertyChanged("drain_source_voltage", self, value)
    
    @property
    def gate_source_voltage(self):
        return self._gate_source_voltage

    @gate_source_voltage.setter
    @uih.assert_int_or_float_argument
    def gate_source_voltage(self, value):
        if self._gate_source_voltage == value:
            return 

        self._gate_source_voltage = value
        self.onPropertyChanged("gate_source_voltage", self, value)

    @property
    def drain_source_voltage_range(self):
        return self._drain_source_voltage_range
    
    @drain_source_voltage_range.setter
    def drain_source_voltage_range(self,value):
        if self._drain_source_voltage_range == value:
            return 

        self._drain_source_voltage_range = value
        self.onPropertyChanged("drain_source_voltage_range", self, value)

    @property
    def gate_source_voltage_range(self):
        return self._gate_source_voltage_range
    
    @gate_source_voltage_range.setter
    def gate_source_voltage_range(self,value):
        if self._gate_source_voltage_range == value:
            return 

        self._gate_source_voltage_range = value
        self.onPropertyChanged("gate_source_voltage_range", self, value)

    @property
    def drain_source_smu(self):
        return self._ds_smu

    @drain_source_smu.setter
    @uih.assert_string_argument
    def drain_source_smu(self, value):
        if self._ds_smu == value:
            return 

        self._ds_smu = value
        self.onPropertyChanged("drain_source_smu", self, value)

    @property
    def gate_source_smu(self):
        return self._gs_smu

    @gate_source_smu.setter
    @uih.assert_string_argument
    def gate_source_smu(self, value):
        if self._gs_smu == value:
            return

        self._gs_smu = value
        self.onPropertyChanged("gate_source_smu", self, value)
    
    @property
    def back_gate_source_smu(self):
        return self._bg_smu

    @back_gate_source_smu.setter
    @uih.assert_string_argument
    def back_gate_source_smu(self, value):
        if self._bg_smu == value:
            return 

        self._bg_smu = value
        self.onPropertyChanged("back_gate_smu", self, value)

    @property
    def integration_time(self):
        return self._integration_time

    @integration_time.setter
    def integration_time(self, value):
        if self._integration_time == value:
            return 

        self._integration_time = value
        self.onPropertyChanged("integration_time", self, value)


    @property
    def current_compliance(self):
        return self._current_compliance
    
    @current_compliance.setter
    @uih.assert_int_or_float_argument
    def current_compliance(self, value):
        if self._current_compliance == value:
            return 

        self._current_compliance = value
        self.onPropertyChanged("current_compliance", self, value)

    @property
    def set_meas_delay(self):
        return self._set_meas_delay

    @set_meas_delay.setter
    @uih.assert_int_or_float_argument
    def set_meas_delay(self, value):
        if self._set_meas_delay == value:
            return 

        self._set_meas_delay = value
        self.onPropertyChanged("set_meas_delay", self, value)

    @property
    def average_count(self):
        return self._average_count

    @average_count.setter
    @uih.assert_integer_argument
    def average_count(self, value):
        if self._average_count == value:
            return 

        self._average_count = value
        self.onPropertyChanged("average_count", self, value)
    
    @property
    def use_extended_save_dialog(self):
        return self._use_extended_save_dialog

    @use_extended_save_dialog.setter
    @uih.assert_boolean_argument
    def use_extended_save_dialog(self, value):
        if self._use_extended_save_dialog == value:
            return 

        self._use_extended_save_dialog = value
        self.onPropertyChanged("use_extended_save_dialog", self, value)

    @property
    def experiment_name(self):
        return self._experiment_name

    @experiment_name.setter
    @uih.assert_string_argument
    def experiment_name(self, value):
        if self._experiment_name == value:
            return 
            
        self._experiment_name = value
        self.onPropertyChanged("experiment_name", self, value)

    @property
    def measurement_name(self):
        return self._measurement_name

    @measurement_name.setter
    @uih.assert_string_argument
    def measurement_name(self, value):
        if self._measurement_name == value:
            return

        self._measurement_name = value
        self.onPropertyChanged("measurement_name", self, value)
    
    @property
    def measurement_count(self):
        return self._measurement_count

    @measurement_count.setter
    @uih.assert_integer_argument
    def measurement_count(self, value):
        if self._measurement_count == value:
            return

        self._measurement_count = value
        self.onPropertyChanged("measurement_count", self, value)

    @property
    def working_directory(self):
        return self._working_directory

    @working_directory.setter
    @uih.assert_string_argument
    def working_directory(self, value):
        if self._working_directory == value:
            return 

        self._working_directory = value
        self.onPropertyChanged("working_directory", self, value)

    @property
    def wafer_name(self):
        return self._wafer_name

    @wafer_name.setter
    @uih.assert_string_argument
    def wafer_name(self, value):
        if self._wafer_name == value:
            return 

        self._wafer_name = value
        self.onPropertyChanged("wafer_name", self, value)

    @property
    def chip_name(self):
        return self._chip_name

    @chip_name.setter
    @uih.assert_string_argument
    def chip_name(self, value):
        if self._chip_name == value:
            return 

        self._chip_name = value
        self.onPropertyChanged("chip_name", self, value)
    
    @property
    def transistor_number(self):
        return self._transistor_number

    @transistor_number.setter
    @uih.assert_integer_argument
    def transistor_number(self, value):
        if self._transistor_number == value:
            return 

        self._transistor_number = value
        self.onPropertyChanged("transistor_number", self, value)


    #### UI properties
    @property
    def transfer_button_checked(self):
        return self._transfer_button_checked

    @transfer_button_checked.setter
    @uih.assert_boolean_argument
    def transfer_button_checked(self, value):
        if self._transfer_button_checked == value:
            return 

        self._transfer_button_checked = value
        self.onPropertyChanged("transfer_button_checked", self, value)

    @property
    def output_button_checked(self):
        return self._output_button_checked

    @output_button_checked.setter
    @uih.assert_boolean_argument
    def output_button_checked(self, value):
        if self._output_button_checked == value:
            return 

        self._output_button_checked = value
        self.onPropertyChanged("output_button_checked", self, value)

    @property
    def timetrace_button_checked(self):
        return self._timetrace_button_checked

    @timetrace_button_checked.setter
    @uih.assert_boolean_argument
    def timetrace_button_checked(self, value):
        if self._timetrace_button_checked == value:
            return 

        self._timetrace_button_checked = value
        self.onPropertyChanged("timetrace_button_checked", self, value)

    @property
    def hw_sweep_button_checked(self):
        return self._hw_sweep_button_checked

    @hw_sweep_button_checked.setter
    @uih.assert_boolean_argument
    def hw_sweep_button_checked(self, value):
        if self._hw_sweep_button_checked == value:
            return 

        self._hw_sweep_button_checked = value
        self.onPropertyChanged("hw_sweep_button_checked", self, value)

    @property
    def sw_sweep_button_checked(self):
        return self._sw_sweep_button_checked

    @sw_sweep_button_checked.setter
    @uih.assert_boolean_argument
    def sw_sweep_button_checked(self, value):
        if self._sw_sweep_button_checked == value:
            return 

        self._sw_sweep_button_checked = value
        self.onPropertyChanged("sw_sweep_button_checked", self, value)