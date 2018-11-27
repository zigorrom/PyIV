import os
import sys
import pickle
from PyQt4 import QtGui, QtCore, uic

import pyfans.ranges.modern_range_editor as mredit

import pyfans.utils.ui_helper as uih
import pyfans.utils.utils as util

from pyiv_model import CharacterizarionMode, PyIV_model, SweepMode


mainViewBase, mainViewForm = uic.loadUiType("UI/UI_IV_Measurement_v4.ui")
class PyIVmainView(mainViewBase, mainViewForm, uih.DataContextWidget):
    settings_filename = "config.cfg"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = None
        self.load_settings()
        self.setupUi()
        self.setupBindings()
        self.dataContext = self.settings
        
        

    def setupUi(self):
        super().setupUi(self)
        integration_count_list = list(map(str,[0,1,5,10,20,40,50,80,100]))
        self.ui_averaging_count.addItems(integration_count_list)
        # self.set_sweepping_mode(self.settings.sweep_mode)
        self.set_mode(self.settings.characterization_mode)
        self.set_exdended_save_dialog(self.settings.use_extended_save_dialog)
        # self.set_mode(self.settings.characterization_mode)
        # self.on_ui_use_advanced_dialog_toggled(False)

    def setupBindings(self):
        sourceObject = None
        #self.calibrate_before_measurement = uih.Binding(self.ui_calibrate, "checked", sourceObject, "calibrate_before_measurement", converter=uih.AssureBoolConverter()) # uih.bind("ui_calibrate", "checked", bool)
        self.drain_source_voltage = uih.Binding(self.ui_drain_source_voltage, "text", sourceObject, "drain_source_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        self.gate_source_voltage = uih.Binding(self.ui_gate_source_voltage, "text", sourceObject, "gate_source_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        self.ds_smu = uih.Binding(self.ui_ds_resource, "currentText", sourceObject, "drain_source_smu")
        self.gs_smu = uih.Binding(self.ui_gs_resource, "currentText", sourceObject, "gate_source_smu")
        # # self.bg_smu = uih.Binding(self.ui_gate_source_voltage, "currentText", sourceObject, "drain_source_smu")

        self.integration_time = uih.Binding(self.ui_integration_time, "currentText", sourceObject, "integration_time")
        self.current_compliance = uih.Binding(self.ui_current_compliance, "text", sourceObject, "current_compliance", converter=uih.StringToCurrentConverter(), validator=uih.CurrentValidator())
        self.set_meas_delay = uih.Binding(self.ui_set_meas_delay, "text", sourceObject, "set_meas_delay", converter=uih.StringToFloatConverter())
        self.average_count = uih.Binding(self.ui_averaging_count, "currentText", sourceObject, "ui_averaging_count", converter=uih.StringToIntConverter())

        self.use_extended_save_dialog = uih.Binding(self.ui_use_advanced_dialog, "checked", sourceObject, "use_extended_save_dialog", converter=uih.AssureBoolConverter())
        self.experiment_name = uih.Binding(self.ui_experimentName, "text", sourceObject, "experiment_name", validator=uih.NameValidator())
        self.measurement_name = uih.Binding(self.ui_measurementName, "text", sourceObject, "measurement_name", validator=uih.NameValidator())
        self.measurement_count = uih.Binding(self.ui_measurementCount, "value", sourceObject, "measurement_count")
        
        self.wafer_name = uih.Binding(self.ui_wafer_name, "text", sourceObject, "wafer_name")
        self.chip_name = uih.Binding(self.ui_chip_name, "text", sourceObject, "chip_name")
        self.transistor_number = uih.Binding(self.ui_transistor_number, "value", sourceObject, "transistor_number")

        self.transfer_button_checked = uih.Binding(self.ui_transfer_radiobutton, "checked", sourceObject, "transfer_button_checked", converter=uih.AssureBoolConverter())
        self.output_button_checked = uih.Binding(self.ui_output_radiobutton, "checked", sourceObject, "output_button_checked", converter=uih.AssureBoolConverter())
        self.timetrace_button_checked = uih.Binding(self.ui_timetrace_radiobutton, "checked", sourceObject, "timetrace_button_checked", converter=uih.AssureBoolConverter())
        self.hw_sweep_radiobutton = uih.Binding(self.ui_hw_sweep_radiobutton, "checked", sourceObject, "hw_sweep_button_checked", converter=uih.AssureBoolConverter())
        self.sw_sweep_radiobutton = uih.Binding(self.ui_sw_sweep_radiobutton, "checked", sourceObject, "sw_sweep_button_checked", converter=uih.AssureBoolConverter())



        # self.ds_smu = uih.Binding(self.ui_gate_source_voltage, "text", sourceObject, "drain_source_smu", validator=uih.NameValidator())

    def load_settings(self):
        if not os.path.isfile(self.settings_filename):
            print("creating new settings")
            self.settings = PyIV_model()
            
        else:
            print("loading settings from file")
            with open(self.settings_filename,"rb") as f:
                settings = pickle.load(f)
                self.settings = settings


    def save_settings(self):
        with open(self.settings_filename,"wb") as f:
            pickle.dump(self.settings, f)

    def setSweepMode(self):
        self.sweep_config_widget.show()
        self.timetrace_config_widget.hide()

    def setTimetraceMode(self):
        self.sweep_config_widget.hide()
        self.timetrace_config_widget.show()

    def set_mode(self, mode):
        if mode == CharacterizarionMode.Output:
            self.setSweepMode()

        elif mode == CharacterizarionMode.Transfer:
            self.setSweepMode()

        elif mode == CharacterizarionMode.Timetrace:
            self.setTimetraceMode()

        else:
            # raise ValueError()
            mode = CharacterizarionMode.Transfer
            self.setSweepMode()

        self.settings.characterization_mode = mode

    def set_sweepping_mode(self, mode):
        if mode == SweepMode.Hardware:
            print("selecting hardware sweeping mode")
        elif mode == SweepMode.Software:
            print("selecting software sweeping mode")
        else:
            #raise ValueError("wrong sweeping mode")
            mode = SweepMode.Hardware

        self.settings.sweep_mode = mode

    def set_exdended_save_dialog(self, state):
        self.ui_advanced_dialog_widget.setVisible(state)

    @QtCore.pyqtSlot()
    def on_ui_drain_source_voltage_range_clicked(self):
        print("vds")
        rng = self.settings.drain_source_voltage_range
        
        try:
            mredit.assert_range_info(rng)
        except AssertionError as e:
            print("assertion error occured")
            rng = mredit.RangeInfo(start=0, end=1, step=1, handler=mredit.HandlersEnum.normal, repeats=1)
        
        dialog = mredit.RangeEditorView()
        dialog.setRange(rng)
        res = dialog.exec_()
        if res:
            self.settings.drain_source_voltage_range = dialog.generateRangeInfo()
            print(self.settings.drain_source_voltage_range)
            
        # mredit.assert_range_info()
    
    @QtCore.pyqtSlot()
    def on_ui_gate_source_voltage_range_clicked(self):
        print("vgs")
        rng = self.settings.gate_source_voltage_range
        
        try:
            mredit.assert_range_info(rng)
        except AssertionError as e:
            print("assertion error occured")
            rng = mredit.RangeInfo(start=0, end=1, step=1, handler=mredit.HandlersEnum.normal, repeats=1)
        
        dialog = mredit.RangeEditorView()
        dialog.setRange(rng)
        res = dialog.exec_()
        if res:
            self.settings.gate_source_voltage_range = dialog.generateRangeInfo()
            print(self.settings.gate_source_voltage_range)
    
    @QtCore.pyqtSlot()    
    def on_ui_transfer_radiobutton_clicked(self):
        print("transfer characteristic")
        self.set_mode(CharacterizarionMode.Transfer)

    @QtCore.pyqtSlot()    
    def on_ui_output_radiobutton_clicked(self):
        print("output characteristic")
        self.set_mode(CharacterizarionMode.Output)

    @QtCore.pyqtSlot()    
    def on_ui_timetrace_radiobutton_clicked(self):
        print("timetrace characteristic")
        self.set_mode(CharacterizarionMode.Timetrace)

    @QtCore.pyqtSlot(bool)
    def on_ui_use_advanced_dialog_toggled(self, enabled):
        print("extended transistor save dialog")
        self.set_exdended_save_dialog(enabled)

    @QtCore.pyqtSlot()    
    def on_ui_hw_sweep_radiobutton_clicked(self):
        print("hardware sweeping mode")
        self.set_sweepping_mode(SweepMode.Hardware)

    @QtCore.pyqtSlot()    
    def on_ui_sw_sweep_radiobutton_clicked(self):
        print("software sweeping mode")
        self.set_sweepping_mode(SweepMode.Software)

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        if self._settings == value:
            return 

        if not isinstance(value, PyIV_model):
            raise TypeError("the model object has wrong type")
    
        self._settings = value
        
    
    def closeEvent(self, event):
        # self.updateSourceData()
        self.save_settings()




def ui_application():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyIV")
    app.setStyle("cleanlooks")
    app.setWindowIcon(QtGui.QIcon('pyiv.ico'))
    wnd = PyIVmainView()
    wnd.show()
    return app.exec_()


if __name__== "__main__":
    sys.exit(ui_application())