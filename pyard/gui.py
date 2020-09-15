from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import pyqtgraph as pg
from time import sleep
import threading

import styles
from cfg import *
import getdata

class App(QWidget):

    def __init__(self, test, mode, port, api, channel):

        super().__init__()

        self.test = test
        self.mode = mode
        self.port = port
        self.api = api
        self.channel = channel

        self.title = 'Weather station'
        if self.mode == 'test':
            self.title += " [test mode]"
        self.setStyleSheet(styles.windowStyle)

        grid = QGridLayout()
        grid.setSpacing(5)
        self.setLayout(grid)

        # plot canvas

        self.canvas = pg.GraphicsLayoutWidget()
        self.canvas.setContentsMargins(20, 10, 20, 10)
        self.canvas.setBackground(styles.bgCanvas)
        grid.addWidget(self.canvas, 0, 0, 1, 2)

        for var in weatherVars:
            if var != time:
                # variable name displayed in the GUI
                var.title = QLabel('{} ({})'.format(var.name, var.units))
                var.title.setStyleSheet(styles.titleStyle)
                var.title.setAlignment(QtCore.Qt.AlignCenter)
                # var.error = var.systError
                # var.errorLabel = QLabel('± {}{}'.format(var.error, var.units))
                var.valueLabel = QLabel("??")
                var.valueLabel.setStyleSheet(styles.valueLabelStyle)
                var.valueLabel.setAlignment(QtCore.Qt.AlignCenter)

        grid.addWidget(temp1.title, 1, 0)
        grid.addWidget(temp1.valueLabel, 2, 0)

        grid.addWidget(temp2.title, 3, 0)
        grid.addWidget(temp2.valueLabel, 4, 0)

        grid.addWidget(pres.title, 1, 1)
        grid.addWidget(pres.valueLabel, 2, 1)

        grid.addWidget(hum.title, 3, 1)
        grid.addWidget(hum.valueLabel, 4, 1)

        self.axt, temp1.line = self.init_subplot(temp1, (0, 0, 1, 2), legend=True)
        self.axt.setLabel('left', text='Temperature', units=temp1.units)
        temp2.line = self.axt.plot(time.array, temp2.array,
                            pen=pg.mkPen(color=styles.linePenColors[1]),
                            name=temp2.name)

        self.axp, pres.line = self.init_subplot(pres, (1, 0, 1, 1))
        self.axh, hum.line = self.init_subplot(hum, (1, 1, 1, 1))

        self.init_ui(mode)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(0)  

    # def center(self):

    #     qr = self.frameGeometry()
    #     cp = QDesktopWidget().availableGeometry().center()
    #     qr.moveCenter(cp)
    #     self.move(qr.topLeft())

    def init_ui(self, mode):

        thr_gui = threading.Thread(target=self.update_data)
        thr_gui.daemon = True
        thr_gui.start()

        self.setWindowTitle(self.title)
        self.show()

    def init_subplot(self, weatherVar, pos, legend=False):

        # TODO: Create a "Subplot" class

        pn = pg.mkPen(color=styles.plotPenColor)
        r, c, h, w = pos
        p = self.canvas.addPlot(r, c, h, w)
        p.setAxisItems({'bottom': pg.DateAxisItem(pen=pn, textPen=pn),
                        'left': pg.AxisItem(orientation='left', pen=pn,
                                            textPen=pn)})
        p.setLabel('left', text=weatherVar.name, units=weatherVar.units)

        if legend:
            p.addLegend()

        line = p.plot(time.array, weatherVar.array,
                      pen=pg.mkPen(color=styles.linePenColors[0]),
                      name=weatherVar.name)

        return p, line

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
            for i in range(len(weatherVars)):
                weatherVars[i].updateVal(data[i], stat[i])
            sleep(10)

    def update_gui(self):

        for var in weatherVars:
            if var != time:
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
            event.accept()
        else:

            event.ignore()
