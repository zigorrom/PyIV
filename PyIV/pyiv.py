import os
import sys
import pickle
from PyQt4 import QtGui, QtCore, uic

import pyfans.ranges.modern_range_editor as mredit

import pyfans.utils.ui_helper as uih
import pyfans.utils.utils as util
from communication_layer import get_available_gpib_resources, get_available_com_resources
from pyiv_model import CharacterizarionMode, PyIV_model, SweepMode, CustomizationEnum
from iv_plot import IV_PlotWidget

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
        self.ivPlotWidget = IV_PlotWidget(self.ui_plot)
        integration_count_list = list(map(str,[0,1,5,10,20,40,50,80,100]))
        self.ui_averaging_count.addItems(integration_count_list)
        # self.set_sweepping_mode(self.settings.sweep_mode)
        self.set_mode(self.settings.characterization_mode)
        self.set_exdended_save_dialog(self.settings.use_extended_save_dialog)
        self.setupCustomizationList()
        self.setupHardwareResources()
        
        # self.ui_customization_list
        # self.set_mode(self.settings.characterization_mode)
        # self.on_ui_use_advanced_dialog_toggled(False)

    def setupBindings(self):
        sourceObject = None
        #self.calibrate_before_measurement = uih.Binding(self.ui_calibrate, "checked", sourceObject, "calibrate_before_measurement", converter=uih.AssureBoolConverter()) # uih.bind("ui_calibrate", "checked", bool)
        self.drain_source_voltage = uih.Binding(self.ui_drain_source_voltage, "text", sourceObject, "drain_source_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        self.gate_source_voltage = uih.Binding(self.ui_gate_source_voltage, "text", sourceObject, "gate_source_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        self.back_gate_voltage = uih.Binding(self.ui_back_gate_voltage, "text", sourceObject, "back_gate_voltage", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
        self.ds_smu = uih.Binding(self.ui_ds_resource, "currentText", sourceObject, "drain_source_smu")
        self.gs_smu = uih.Binding(self.ui_gs_resource, "currentText", sourceObject, "gate_source_smu")
        self.bg_smu = uih.Binding(self.ui_bg_resource, "currentText", sourceObject, "back_gate_smu")
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
        self.custom_button_checked = uih.Binding(self.ui_custom_radiobutton, "checked", sourceObject, "custom_button_checked", converter=uih.AssureBoolConverter())
        self.hw_sweep_radiobutton = uih.Binding(self.ui_hw_sweep_radiobutton, "checked", sourceObject, "hw_sweep_button_checked", converter=uih.AssureBoolConverter())
        self.sw_sweep_radiobutton = uih.Binding(self.ui_sw_sweep_radiobutton, "checked", sourceObject, "sw_sweep_button_checked", converter=uih.AssureBoolConverter())
        self.folderBrowseButton.sigFolderSelected.connect(self.on_folder_selected)
        self.ui_customization_list.model().rowsMoved.connect(self.on_customization_list_changed)
        self.ui_customization_list.model().rowsRemoved.connect(self.on_customization_list_changed)

        # self.ds_smu = uih.Binding(self.ui_gate_source_voltage, "text", sourceObject, "drain_source_smu", validator=uih.NameValidator())
    def show_message(self,message, timeout = 0):
        if message:
            self.statusbar.showMessage(message, timeout)

    def on_folder_selected(self, folder):
        if self.settings:
            self.settings.working_directory = folder
    
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
        self.ui_backgate_voltage_range.hide()
        self.setVisibleVBGresource(False)
        # self.ui_bg_label.hide()
        # self.ui_bg_resource.hide()
        self.ui_customization_widget.hide()

    def setTimetraceMode(self):
        self.sweep_config_widget.hide()
        self.timetrace_config_widget.show()
        self.ui_backgate_voltage_range.hide()
        self.setVisibleVBGresource(True)
        # self.ui_bg_label.show()
        # self.ui_bg_resource.show()
        self.ui_customization_widget.hide()
    
    def setCustomMode(self):
        self.sweep_config_widget.show()
        self.timetrace_config_widget.hide()
        self.ui_backgate_voltage_range.show()
        self.setVisibleVBGresource(True)
        # self.ui_bg_label.show()
        # self.ui_bg_resource.show()
        self.ui_customization_widget.show()

    def setupCustomizationList(self):
        listVals = [e.value for e in CustomizationEnum]
        self.ui_customization_list.clear()
        self.ui_customization_list.addItems(listVals)
        self.on_customization_list_changed()

    def setupHardwareResources(self):
        print("refreshing hardware resources")
        gpib_resources = get_available_gpib_resources()
        self.ui_ds_resource.clear()
        self.ui_gs_resource.clear()
        self.ui_bg_resource.clear()
        self.ui_ds_resource.addItems(gpib_resources)
        self.ui_gs_resource.addItems(gpib_resources)
        self.ui_bg_resource.addItems(gpib_resources)


    def setVisibleVDSresource(self, visible):
        self.ui_ds_label.setVisible(visible)
        self.ui_ds_resource.setVisible(visible)

    def setVisibleVGSresource(self, visible):
        self.ui_gs_label.setVisible(visible)
        self.ui_gs_resource.setVisible(visible)

    def setVisibleVBGresource(self, visible):
        self.ui_bg_label.setVisible(visible)
        self.ui_bg_resource.setVisible(visible)

    def on_customization_list_changed(self):
        print("list changed")
        items = []
        for index in range(self.ui_customization_list.count()):
            item = self.ui_customization_list.item(index)
            val = CustomizationEnum(item.text())
            items.append(val)
            
        print(items)
        self.settings.custom_order = items
        for e in CustomizationEnum:
            is_present = e in items
            if e is CustomizationEnum.Vbg:
                self.setVisibleVBGresource(is_present)
                
            elif e is CustomizationEnum.Vds:
                self.setVisibleVDSresource(is_present)

            elif e is CustomizationEnum.Vgs:
                self.setVisibleVGSresource(is_present)

        if len(items)<1:
            return 

        inner = items[-1]
        if inner == CustomizationEnum.Vgs:
            self.ivPlotWidget.setGateSourceVoltageLabels()

        elif inner == CustomizationEnum.Vds:
            self.ivPlotWidget.setDrainSourceVoltageLabels()

        elif inner == CustomizationEnum.Vbg:
            self.ivPlotWidget.setBackGateVoltageLabels()

        else:
            raise ValueError()

        



        


    def set_mode(self, mode):
        if mode == CharacterizarionMode.Output:
            self.setSweepMode()

        elif mode == CharacterizarionMode.Transfer:
            self.setSweepMode()

        elif mode == CharacterizarionMode.Timetrace:
            self.setTimetraceMode()

        elif mode == CharacterizarionMode.Custom:
            self.setCustomMode()

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
        if state is None:
            state = False

        self.ui_advanced_dialog_widget.setVisible(state)

    @QtCore.pyqtSlot()
    def on_ui_refresh_resources_clicked(self):
        self.setupHardwareResources()

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
    def on_ui_backgate_voltage_range_clicked(self):
        print("vbg")
        rng = self.settings.back_gate_voltage_range
        
        try:
            mredit.assert_range_info(rng)
        except AssertionError as e:
            print("assertion error occured")
            rng = mredit.RangeInfo(start=0, end=1, step=1, handler=mredit.HandlersEnum.normal, repeats=1)
        
        dialog = mredit.RangeEditorView()
        dialog.setRange(rng)
        res = dialog.exec_()
        if res:
            self.settings.back_gate_voltage_range = dialog.generateRangeInfo()
            print(self.settings.back_gate_voltage_range)



    @QtCore.pyqtSlot()    
    def on_ui_transfer_radiobutton_clicked(self):
        print("transfer characteristic")
        self.set_mode(CharacterizarionMode.Transfer)
        self.ivPlotWidget.setGateSourceVoltageLabels()

    @QtCore.pyqtSlot()    
    def on_ui_output_radiobutton_clicked(self):
        print("output characteristic")
        self.set_mode(CharacterizarionMode.Output)
        self.ivPlotWidget.setDrainSourceVoltageLabels()

    @QtCore.pyqtSlot()    
    def on_ui_timetrace_radiobutton_clicked(self):
        print("timetrace characteristic")
        self.set_mode(CharacterizarionMode.Timetrace)
        self.ivPlotWidget.setTimetraceLabels()

    @QtCore.pyqtSlot()    
    def on_ui_custom_radiobutton_clicked(self):
        print("timetrace characteristic")
        self.set_mode(CharacterizarionMode.Custom)
        self.on_customization_list_changed()

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

    @QtCore.pyqtSlot()
    def on_ui_remove_smu_clicked(self):
        print("removing smu")
        selectedItems = self.ui_customization_list.selectedItems()
        for item in selectedItems:
            row = self.ui_customization_list.row(item)
            self.ui_customization_list.takeItem(row)

    @QtCore.pyqtSlot()
    def on_ui_reset_smu_list_clicked(self):
        print("reset smu")
        self.setupCustomizationList()


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
    wnd.showMaximized()
    return app.exec_()


if __name__== "__main__":
    sys.exit(ui_application())