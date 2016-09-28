import time, sys

from PyQt4 import QtCore
import numpy as np

class HistoryBuffer:
    """Fixed-size NumPy array ring buffer"""
    def __init__(self, data_size, max_history_size, dtype=float):
        self.data_size = data_size
        self.max_history_size = max_history_size
        self.history_size = 0
        self.counter = 0
        self.buffer = np.empty(shape=(max_history_size, data_size), dtype=dtype)

    def append(self, data):
        """Append new data to ring buffer"""
        self.counter += 1
        if self.history_size < self.max_history_size:
            self.history_size += 1
        self.buffer = np.roll(self.buffer, -1, axis=0)
        self.buffer[-1] = data

    def get_buffer(self):
        """Return buffer stripped to size of actual data"""
        if self.history_size < self.max_history_size:
            return self.buffer[-self.history_size:]
        else:
            return self.buffer

    def __getitem__(self, key):
        return self.buffer[key]


class TaskSignals(QtCore.QObject):
    """Task signals emitter"""
    result = QtCore.pyqtSignal(object)


class Task(QtCore.QRunnable):
    """Threaded task (run it with QThreadPool worker threads)"""
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.signals = TaskSignals()

    def run(self):
        """Run task in worker thread and emit signal with result"""
        #print('Running', self.task, 'in thread', QtCore.QThread.currentThreadId())
        result = self.task(*self.args, **self.kwargs)
        self.signals.result.emit(result)

class TimetraceDataStorage(QtCore.QObject):
    history_updated = QtCore.pyqtSignal(object)
    data_updated = QtCore.pyqtSignal(object)
    data_recalculated = QtCore.pyqtSignal(object)
    average_updated = QtCore.pyqtSignal(object)
    

    def __init__(self, max_history_size=100, parent=None):
        super().__init__(parent)
        self.max_history_size = max_history_size
        self.data = {}        
        # Use only one worker thread because it is not faster
        # with more threads (and memory consumption is much higher)
        self.threadpool = QtCore.QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        self.reset()

    def reset(self):
        """Reset all data"""
        self.wait()
        data = {}
        self.t = None
        self.history = None
        self.reset_data()

    def reset_data(self):
        """Reset current data"""
        self.wait()
        self.id = None
        self.ig = None
        self.vd = None
        self.vg = None
        self.average_counter = 0
        self.average = None
       

##    def start_recording(self, working_folder, exp_name):
##        pass
##        self.description_file = open("\\".join([working_folder,exp_name+".dat"])
##
##    def stop_recording(self):
##        pass
##

    def start_task(self, fn, *args, **kwargs):
        """Run function asynchronously in worker thread"""
        task = Task(fn, *args, **kwargs)
        self.threadpool.start(task)

    def wait(self):
        """Wait for worker threads to complete all running tasks"""
        self.threadpool.waitForDone()

    def update(self, data):
        """Update data storage"""
        self.average_counter += 1

        if self.t is None:
            self.t = data["t"]

        self.start_task(self.update_history, data.copy())
        self.start_task(self.update_data, data)

    def update_data(self, data):
        """Update main spectrum data (and possibly apply smoothing)"""
##
        self.data = data
        self.id = data["id"]
        self.ig = data["ig"]
        self.vd = data["vd"]
        self.vg = data["vg"]
        self.data_updated.emit(self)

##        self.start_task(self.update_average, data)
       

    def update_history(self, data):
        """Update spectrum measurements history"""
        pass
##        if self.history is None:
##            self.history = HistoryBuffer(len(data["y"]), self.max_history_size)
##        
##        self.history.append(data["y"])
##        self.history_updated.emit(self)

    def update_average(self, data):
        """Update average data"""
        pass
##        if self.average is None:
##            self.average = data["y"].copy()
##        else:
##            self.average = np.average((self.average, data["y"]), axis=0, weights=(self.average_counter - 1, 1))
##            self.average_updated.emit(self)

    

  

    
