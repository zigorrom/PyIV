import sys, signal, time

from PyQt4 import QtCore, QtGui

from plot import TimetraceIVplotWidget

from timetrace_view import Ui_TimetraceView


class TimetraceMainWindow(QtGui.QMainWindow, Ui_TimetraceView):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)

        
        self.update_buttons()
        self.load_settings()

    def save_settings(self):
        """Save spectrum analyzer settings and window geometry"""
        settings = QtCore.QSettings()
        settings.setValue("ds_voltage", self.dsVoltageSet.value())
        settings.setValue("gs_voltage", self.gsVoltageSet.value())
        settings.setValue("pulsed_gate", int(self.pulsedVoltageCheckBox.isChecked()))
        settings.setValue("pulse_width", self.pulseWidth.value())
        settings.setValue("pulse_delay", self.pulseDelay.value())
        settings.setValue("pulse_count", self.pulseCount.value())
        settings.setValue("gate_cutoff", self.gateIcutoff.value())
        settings.setValue("gate_cutoff_units", self.gateIcutoffUnits.currentIndex())
        

        # Save window state and geometry
        settings.setValue("window_geometry", self.saveGeometry())
        settings.setValue("window_state", self.saveState())
        settings.setValue("plotsplitter_state", self.plotSplitter.saveState())

    def load_settings(self):
        """Restore spectrum analyzer settings and window geometry"""
        settings = QtCore.QSettings()
        self.dsVoltageSet.setValue(settings.value("ds_voltage", 0, float))
        self.gsVoltageSet.setValue(settings.value("gs_voltage", 0, float))
        self.pulsedVoltageCheckBox.setChecked(settings.value("pulsed_gate",0 , int))
        self.pulseWidth.setValue(settings.value("pulse_width", 0, float))
        self.pulseDelay.setValue(settings.value("pulse_delay", 0, float))
        self.pulseCount.setValue(settings.value("pulse_count", 0, int))
        self.gateIcutoff.setValue(settings.value("gate_cutoff", 0, float))
        self.gateIcutoffUnits.setCurrentIndex(settings.value("gate_cutoff_units", 0, int))
        

        # Restore window state
        if settings.value("window_state"):
            self.restoreState(settings.value("window_state"))
        if settings.value("plotsplitter_state"):
            self.plotSplitter.restoreState(settings.value("plotsplitter_state"))

##        # Migration from older version of config file
##        if settings.value("config_version", 1, int) < 2:
##            # Make tabs from docks when started for first time
##            self.tabifyDockWidget(self.settingsDockWidget, self.levelsDockWidget)
##            self.settingsDockWidget.raise_()
##            self.set_dock_size(self.controlsDockWidget, 0, 0)
##            self.set_dock_size(self.frequencyDockWidget, 0, 0)
##            # Update config version
##            settings.setValue("config_version", 2)

        # Window geometry has to be restored only after show(), because initial
        # maximization doesn't work otherwise (at least not in some window managers on X11)
        self.show()
        if settings.value("window_geometry"):
            self.restoreGeometry(settings.value("window_geometry"))


    def update_buttons(self):
        pass

    def closeEvent(self, event):
        """Save settings when main window is closed"""
##        self.stop()
        self.save_settings()

    
        
def main():
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("TimetraceMeasurementModule")
    app.setOrganizationDomain("fz.juelich.de")
    app.setApplicationName("TimetraceMeasurementModule")
    window = TimetraceMainWindow()
    sys.exit(app.exec_())

if __name__== "__main__":
    main()
