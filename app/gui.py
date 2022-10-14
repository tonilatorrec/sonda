from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import pyqtgraph as pg
from time import sleep
import threading

import styles
from cfg import *
import getdata


class FirstCfgWindow(QWidget):

    def __init__(self, test, mode, port, api, channel):
        super().__init__()

        self.setWindowTitle("Weather")

        layout = QVBoxLayout()

        self.b1 = QPushButton("Enter the app")
        layout.addWidget(self.b1)

        self.setLayout(layout)


class App(QMainWindow):

    def __init__(self, test, mode, port, api, channel):

        super().__init__()

        self.test = test
        self.mode = mode
        self.port = port
        self.api = api
        self.channel = channel

        self.firstcfg = FirstCfgWindow(test, mode, port, api, channel)
        self.firstcfg.b1.clicked.connect(self.init_ui)
        self.firstcfg.show()

    def init_ui(self):

        self.title = 'Weather station'
        if self.mode == 'test':
            self.title += " [test mode]"
        self.setStyleSheet(styles.windowStyle)

        grid = QGridLayout()
        grid.setSpacing(5)
        widget = QWidget(self)
        widget.setLayout(grid)

        self.setCentralWidget(widget)

        # plot canvas

        self.canvas = pg.GraphicsLayoutWidget()
        self.canvas.setContentsMargins(20, 10, 20, 10)
        self.canvas.setBackground(styles.bgCanvas)
        grid.addWidget(self.canvas, 0, 0, 1, 2)

        for var in weatherVarsList:
            if var != time:
                # variable name displayed in the GUI
                var.title = QLabel('{} ({})'.format(var.name, var.units))
                var.title.setStyleSheet(styles.titleStyle)
                var.title.setAlignment(QtCore.Qt.AlignCenter)
                # TODO: Add (systematic) uncertainties due to the components' resolution.
                # var.error = var.systError
                # var.errorLabel = QLabel('± {}{}'.format(var.error, var.units))
                var.valueLabel = QLabel("??")
                var.valueLabel.setStyleSheet(styles.valueLabelStyle)
                var.valueLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.add_value_widgets(grid)
        self.add_subplots()

        thr_gui = threading.Thread(target=self.update_data)
        thr_gui.daemon = True
        thr_gui.start()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(0)

        self.setWindowTitle(self.title)

        self.firstcfg.close()        
        self.show()

    def add_value_widgets(self, grid):
        nvar = len(weatherVars)
        j = 1
        for line in config['var_grid']:
            row = config['var_grid'][line].split(';')
            row_length = len(row)
            for i in range(row_length):
                n = int(row[i][-1])
                # title widget
                grid.addWidget(weatherVarsList[n - 1].title, j, i)
                grid.addWidget(weatherVarsList[n - 1].valueLabel, j + 1, i)
            j += 2

    def add_subplots(self):
        grid_nrows = len(config['plot_grid'])
        for i in range(1, grid_nrows + 1):
            j = 0
            row = config['plot_grid']['row{}'.format(i)].split(';')
            for var_type in row:
                self.init_subplot(var_type, (i, j, 1, 1))
                j += 1

    def init_subplot(self, var_type, pos):

        v1 = weatherVars[var_type][0]

        pn = pg.mkPen(color=styles.plotPenColor)
        r, c, h, w = pos
        p = self.canvas.addPlot(r, c, h, w)
        p.setAxisItems({'bottom': pg.DateAxisItem(pen=pn, textPen=pn),
                        'left': pg.AxisItem(orientation='left', pen=pn,
                                            textPen=pn)})
        p.setLabel('left', text=v1.type, units=v1.units)

        if len(weatherVars[var_type]) > 1:
            p.addLegend()

        i = 0
        for v in weatherVars[var_type]: 
            v.line = p.plot(time.array, v.array,
                            pen=pg.mkPen(color=styles.linePenColors[i]),
                            name=v.name)
            i += 1

    def update_data(self):
        '''
        Updates the plots and the GUI with new data.
        '''
        while True:
            if self.mode == 'test':
                data, stat = getdata.from_rand()
            elif self.mode == 'api':
                upd = False
                while not upd:
                    try:
                        data, stat = getdata.from_ts(channel=self.channel,
                                                     key=self.api)
                        if data[-1] != time.value:
                            upd = True
                    except:
                        continue
            for i in range(len(weatherVarsList)):
                weatherVarsList[i].updateVal(data[i], stat[i])
            time.updateVal(data[-1], stat[-1])
            sleep(10)

    def update_gui(self):

        for var in weatherVarsList:
            try:
                var.valueLabel.setText("{:.1f}".format(var.value))
                var.line.setData(time.array, var.array)
            except:
                pass

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # TODO: Save data in a CSV file
            event.accept()
        else:
            event.ignore()
