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
    def __init__(self, layout, x_axis = "t", ly_axis = "id",ry_axis ="vd"):
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        self.layout = layout
        self.x_axis = x_axis
        self.ly_axis = ly_axis
        self.ry_axis = ry_axis
##        self.max_points = 1000
        self.current_curve = None
        self.current_color = pg.mkColor("y")
        
        self.voltage_curve = None
        self.voltage_color = pg.mkColor("g")

        #for plot resizing
        self.p1 = None
        self.p2 = None
                

##        print("Attr names: {0},{1},{2}".format(self.x_axis,self.ly_axis,self.ry_axis))
        
        
        self.create_plot()

    def create_plot(self):
        self.posLabel = self.layout.addLabel(row=0, col=0, justify="right")
        self.plot = self.layout.addPlot(row=1,col =0)
        print(self.plot)
##        self.plot.showGrid(x=True, y=True)
        p1 = self.plot
        p1.setLabel("left","Current",units="A")
        p1.setLabel("bottom",'Time',units="s")
        
        p2 = pg.ViewBox()
        p1.showAxis('right')
        p1.scene().addItem(p2)
        p1.getAxis('right').linkToView(p2)
        p2.setXLink(p1)
        p1.getAxis('right').setLabel("Voltage")

##        p1.setYRange(0.1,0.2)
##        p2.setYRange(0.1,0.2)

        self.current_curve = p1.plot(pen=self.current_color)
        self.current_curve.setZValue(900)

        self.voltage_curve = pg.PlotCurveItem(pen=self.voltage_color)
        self.voltage_curve.setZValue(800)
        p2.addItem(self.voltage_curve)

# for resizong handling
        self.p1 = p1
        self.p2 = p2
        self.p1.vb.sigResized.connect(self.updateViews)

    def updateViews(self):
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())

    def clear_plot(self):
        self.curve.clear()

    def update_plot(self,data_storage,force = False):
        try:
            
            time = data_storage.data[self.x_axis]
            current =data_storage.data[self.ly_axis]
            voltage = data_storage.data[self.ry_axis]
            if time and current and voltage:
                self.current_curve.setData(time,current)
                self.voltage_curve.setData(time,voltage)
                print("updating plot")
        except Exception as e:
            print(str(e))
##            print("Error attribute not found: {0},{1},{2}".format(self.x_axis,self.ly_axis,self.ry_axis))
            
        

        

        
