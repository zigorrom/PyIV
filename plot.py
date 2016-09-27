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
    def __init__(self, layout):
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        self.layout = layout
        self.max_points = 1000
        
        self.create_plot()

    def create_plot(self):
        self.posLabel = self.layout.addLabel(row=0, col=0, justify="right")
        self.plot = self.layout.addPlot(row=1,col =0)
        self.plot.showGrid(x=True, y=True)
        self.plot.setLabel("left", "Current", units="A")
        self.plot.setLabel("bottom", "Time", units="s")
        self.plot.setLimits(xMin=0)
        self.plot.showButtons()

    def clear_plot(self):
        self.curve.clear()
