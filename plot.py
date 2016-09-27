import collections, math

from PyQt4 import QtCore
import pyqtgraph as pg

# Basic PyQtGraph settings
pg.setConfigOptions(antialias=True)

class IVplotWidget:
    def __init__(self,layout):
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        self.layout = layout
        
    


class TimetraceIVplotWidget:
    def __init__(self):
        pass
