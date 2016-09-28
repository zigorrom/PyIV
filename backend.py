import numpy as np
import time
from PyQt4 import QtCore

class TimetraceMeasurement(QtCore.QThread):
    TimetraceStarted = QtCore.pyqtSignal()
    TimetraceStopped = QtCore.pyqtSignal()

    def __init__(self, data_storage, parent = None):
        super().__init__(parent)
        self.data_storage = data_storage
        self.alive = False
        self.process = None
        

    def stop(self):
##        self.process_stop()
        self.alive = False
        self.wait()
    
    def setup(self):
        print("setup")

    def process_start(self):
        print("process strart")

    def process_stop(self):
        print("process stop")

    def run(self):
        self.process_start()
        self.alive = True
        self.TimetraceStarted.emit()
        counter = 0.0
        length = 50000
        data = {}
        while True:
            if not self.alive:
                break
            print("count {0}".format(counter))
            cpl = counter + length
            
            data = {"t":list(np.arange(counter, cpl, dtype = float)),
                    "id":list(np.random.rand(length)),
                    "ig":list(np.random.rand(length)),
                    "vd":list(np.random.rand(length)),
                    "vg":list(np.random.rand(length))}
            self.data_storage.update(data)
            counter = cpl
            time.sleep(0.1)
            
        self.process_stop()
        self.alive = False
        self.TimetraceStopped.emit()
    
