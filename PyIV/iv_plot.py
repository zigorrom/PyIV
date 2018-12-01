import pyqtgraph as pg

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', None) #'w')
pg.setConfigOption('foreground','k')


class IV_PlotWidget:
    def __init__(self, layout):
        if not isinstance(layout, pg.GraphicsLayoutWidget):
            raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

        self.layout = layout
        self.curve_count = 0
        self.create_plot()
        
    

    def set_independent_variable_name(self, name, units = "V"):
        self.plot.setLabel("bottom", "{0} Voltage".format(name.title()), units = units)

    def create_plot(self):
        """Create main spectrum plot"""
        self.posLabel = self.layout.addLabel(row=0, col=0, justify="right")
        self.plot = self.layout.addPlot(row=1, col=0)
        self.plot.showGrid(x=True, y=True)
        self.plot.setLogMode(x=False, y=False)
        # self.plot.setLabel("left", "DrainCurrent", units="A")
        #self.plot.setLabel("bottom", "Frequency", units="Hz")
        self.plot.setLimits(xMin=-200,xMax = 200, yMin = -1, yMax = 1)
        #self.plot.setXRange(0.1,5)
        #self.plot.setYRange(-20,-1)

        right_axis = self.plot.getAxis("right")
        right_axis.setStyle(showValues = False)
        top_axis = self.plot.getAxis("top")
        top_axis.setStyle(showValues = False)

        left_axis = self.plot.getAxis("left")
        bottom_axis = self.plot.getAxis("bottom")
        font = pg.Qt.QtGui.QFont()
        font.setPixelSize(20)
        left_axis.tickFont = font
        left_axis.setStyle(tickTextOffset = 10)
        left_axis.setWidth(120)
        bottom_axis.tickFont = font
        bottom_axis.setStyle(tickTextOffset = 10)

        self.plot.showAxis("right", show=True)
        self.plot.showAxis("top", show=True)
        # self.plot.setLabel("left", "Power", units="V^2Hz-1")
        # self.plot.setLabel("left", "<font size=\"15\">Power Spectral Density, S<sub>V</sub> (V<sup>2</sup>Hz<sup>-1</sup>)</font>")#, units="<font size=\"15\">V^2Hz-1</font>")
        # self.setYLabel("Drain Current, I<sub>D</sub>", units="A")
        # self.plot.setLabel("bottom", "Frequency", units="Hz")
        # self.plot.setLabel("bottom", "<font size=\"15\">Frequency, f (Hz)</font>")#, units="Hz")
        #self.setXLabel("Drain-Source Voltage, V<sub>DS</sub>", units="V")
        self.setGateSourceVoltageLabels()

        self.plot.addLegend()
        self.plot.showButtons()

        # Create crosshair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.vLine.setZValue(1000)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.vLine.setZValue(1000)
        self.plot.addItem(self.vLine, ignoreBounds=True)
        self.plot.addItem(self.hLine, ignoreBounds=True)
        self.mouseProxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
                                         rateLimit=60, slot=self.mouse_moved)

    def clear_curves(self):
        self.plot.clear()
        self.plot.legend.items = []

    def add_curve(self, x_data, y_data, name, **kwargs):
        p = pg.intColor(self.curve_count,width = 5)
        self.plot.plot(x_data, y_data, name = name, pen = p, **kwargs)
        self.curve_count += 1

    def setLabelForAxis(self, axis, label, size=15, units=None, **kwargs):
        self.plot.setLabel(axis, "<font size=\"{s}\">{l}</font>".format(l=label,s=size), **kwargs)#, units="Hz")

    def setXLabel(self, label, **kwargs):
        self.setLabelForAxis("bottom", label, **kwargs)

    def setYLabel(self, label, **kwargs):
        self.setLabelForAxis("left", label, **kwargs)

    def setDrainSourceVoltageLabels(self):
        self.setXLabel("Drain-Source Voltage, V<sub>DS</sub>", units="V")
        self.setYLabel("Drain Current, I<sub>D</sub>", units="A")

    def setGateSourceVoltageLabels(self):
        self.setXLabel("Gate-Source Voltage, V<sub>GS</sub>", units="V")
        self.setYLabel("Drain Current, I<sub>D</sub>", units="A")

    def setBackGateVoltageLabels(self):
        self.setXLabel("Back-Gate Voltage, V<sub>BG</sub>", units="V")
        self.setYLabel("Drain Current, I<sub>D</sub>", units="A")

    def setTimetraceLabels(self):
        self.setXLabel("Time, t", units="s")
        self.setYLabel("Drain Current, I<sub>D</sub>", units="A")

    def mouse_moved(self, evt):
        """Update crosshair when mouse is moved"""
        pos = evt[0]
        if self.plot.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.vb.mapSceneToView(pos)
            self.posLabel.setText(
                "<span style='font-size: 12pt'>V={:.5} V, Id={:.5E} A</span>".format( #:0.3f
                    mousePoint.x() ,
                    mousePoint.y()
                )
            )
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())
