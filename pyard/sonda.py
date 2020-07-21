#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import datetime
import atexit
import locale
import time
import sys

import threading

# gui modules
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

# import matplotlib
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# import matplotlib.dates as mdates
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure

# matplotlib.rcParams['backend'] = 'Qt5Agg'
# matplotlib.rcParams['text.usetex'] = False

# matplotlib.use('Qt5Agg')

class PyArd():

    def get_data(self, old_data):
        '''
        Receives data from the board and checks whether the values
        are correct. The data is stored as a list:
            [ temp1, temp2, temp3, pres, hum, time ].
        The stat list contains the quality of the measures in the
        same order (0: correct, 1: incorrect).

        Args:
            old_data (list): values from the last measurements;
                             (empty list for first measurement)

        Returns:
            new_data (list): values from the current measurement
            stat (list): quality of the new measures
                0 -- data with errors
                1 -- correct data
        '''

        stat = [1, 1, 1, 1, 1, 1]

        def from_ard(old_data):
            upd = False
            while self.ard.inWaiting() == 0:
                pass
            ard_data = str(self.ard.readline(), 'utf-8').split(';')
            if len(ard_data) <= 2:
                return from_ard(old_data)
            else:
                return ard_data

        new_data = from_ard(old_data)
        # adds reception time, not measurement time
        new_data.append(datetime.datetime.now().timestamp())
        # checks if some quantity has not been measured
        for i in range(0, 5):
            if new_data[i] == 'nan':
                stat[i] = 0

        # zero humidity
        if abs(float(new_data[4])) == 0:
            stat[4] = 0

        # the DS18B20 sensor may record a temperature of 85.00ºC
        # or suddenly drop to 0ºC, if the difference between consecutive
        # temperatures is greater than 10ºC the measure is considered incorrect
        try:
            if (abs(float(old_data[1]) - float(new_data[1])) > 10) or float(new_data[1]) > 84:
                stat[1] = 0
        except IndexError:  # first data, nothing to compare
            pass

        return new_data, stat

    def __init__(self, ard):
        global t1Array, t2Array, t3Array, pArray, hArray, timeArray
        super().__init__()
        self.ard = ard  # arduino board
        self.counter = 0

        t1Array = list()
        t2Array = list()
        t3Array = list()
        pArray = list()
        hArray = list()
        timeArray = list()

        # defines what to do after exiting
        atexit.register(self.exit_handler)

        app = QApplication(sys.argv)
        plot = ArdPlot(self)
        sys.exit(app.exec_())

    def update_data(self):
        """
        Updates data from the Arduino board.
        """

        global t1Array, t2Array, t3Array, pArray, hArray, timeArray

        while True:

            if not self.counter:
                data = []
            data, stat = self.get_data(data)
            timeArray.append(data[5])

            t1Array.append(float(data[0]))
            t2Array.append(float(data[1]))
            t3Array.append(float(data[2]))
            pArray.append(float(data[3]))
            hArray.append(float(data[4]))

    def exit_handler(self):
        global t1Array, t2Array, t3Array, pArray, hArray, timeArray
        '''
        Stores measured data in a .dat file when exiting the app
        '''

        exit_time = datetime.datetime.now()
        ofilename = 'res_{}.dat'.format(exit_time.strftime("%d%m%y_%H%M%S"))

        with open('./res/' + ofilename, 'w+', newline='') as self.ofile:
            self.ofile.write('#{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                'time', 'Temp. 1 (ºC)', 'Temp. 2 (ºC)', 'Temp. 3 (ºC)',
                 'Pressure (hPa)', 'Rel. humidity (%)'))
            locale.setlocale(locale.LC_ALL, '')
            for i in range(len(t1Array)):
                self.ofile.write('{}\t{:.1f}\t{:.2f}\t{:.1f}\t{:.1f}\t{:.1f}\n'.format(
                    datetime.datetime.fromtimestamp(timeArray[i]).strftime("%d/%m/%y %H:%M:%S"),
                    t1Array[i], t2Array[i],
                    t3Array[i], pArray[i],
                    hArray[i]))

        print('Exit!')

class ArdPlot(QWidget):

    def __init__(self, pyard):
        super().__init__()
        self.pyard = pyard

        self.init_gui(self.pyard)

    def init_gui(self, pyard):
        global t1Array, t2Array, t3Array, pArray, hArray, timeArray

        x = threading.Thread(target=self.pyard.update_data)
        x.daemon = True
        x.start()

        # colors
        self.bgColor = 'white'  # background color
        self.setStyleSheet("background-color: {};".format(self.bgColor))

        # fonts
        self.valueFont = QFont('SansSerif', 20)
        self.valueColors = ['#000066', '#b30000', '#e67300']        
        self.titleFont = QFont('SansSerif', 9)
        self.titleColor = "#000033"

        # grid
        grid = QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)

        # exit button
        qbtn = QPushButton('Exit', self)
        qbtn.clicked.connect(QApplication.instance().quit)
        qbtn.setToolTip('Exit the program')
        qbtn.resize(qbtn.sizeHint())
        grid.addWidget(qbtn, 3, 1, 2, 1)

        # plot canvas
        self.canvas = pg.GraphicsLayoutWidget()
        self.canvas.setBackground('w')
        grid.addWidget(self.canvas, 0, 0, 1, 3)

        def init_variable(self, name, t_font=self.titleFont,
                          v_font=self.valueFont,
                          fg_color=self.titleColor,
                          bg_color=self.bgColor):
            """
            Initializes the label and values for a measured variable.
            
            Args:
                name (str): Name of the variable
                t_font (QFont, optional): Font of the title
                v_font (QFont, optional): Font of the displayed value
                fg_color (str, optional): Font color
                bg_color (str, optional): Background color
            
            Returns:
                titleLabel (QLabel): variable title
                valueLabel (QLabel): displayed value
            """

            titleLabel = QLabel(name)
            titleLabel.setStyleSheet("color: {}; background-color: {};".format(
                                     fg_color, bg_color))
            titleLabel.setFont(t_font)
            titleLabel.setAlignment(QtCore.Qt.AlignCenter)

            valueLabel = QLabel("{:.1f}".format(0))
            # the color of the value label will change depending on the measure
            valueLabel.setStyleSheet("color: {}; background-color: {};".format(
                                     fg_color, bg_color))
            valueLabel.setFont(v_font)
            valueLabel.setAlignment(QtCore.Qt.AlignCenter)         

            return titleLabel, valueLabel

        self.t1Title, self.t1Value = init_variable(self, 'Temperature 1 (ºC)')
        grid.addWidget(self.t1Title, 1, 0)
        grid.addWidget(self.t1Value, 2, 0)

        self.t2Title, self.t2Value = init_variable(self, 'Temperature 2 (ºC)')
        grid.addWidget(self.t2Title, 1, 1)
        grid.addWidget(self.t2Value, 2, 1)

        self.t3Title, self.t3Value = init_variable(self, 'Temperature 3 (ºC)')
        grid.addWidget(self.t3Title, 1, 2)
        grid.addWidget(self.t3Value, 2, 2)

        self.pTitle, self.pValue = init_variable(self, 'Pressure (hPa)')
        grid.addWidget(self.pTitle, 3, 0)
        grid.addWidget(self.pValue, 4, 0)

        self.hTitle, self.hValue = init_variable(self, 'Relative humidity (%)')
        grid.addWidget(self.hTitle, 3, 2)
        grid.addWidget(self.hValue, 4, 2)

        # temperature plot
        self.axt = self.canvas.addPlot(0, 0, 1, 2)
        self.axt.setAxisItems({'bottom': pg.DateAxisItem()})
        self.axt.setLabel('left', 'Temperature', units='ºC')
        self.axt.addLegend()
        self.t1Line = self.axt.plot(timeArray, t1Array,
                                    pen=pg.mkPen(color='#ff6600'),
                                    name='T1')
        self.t2Line = self.axt.plot(timeArray, t2Array,
                                    pen=pg.mkPen(color='#ffb380'),
                                    name='T2')
        self.t3Line = self.axt.plot(timeArray, t3Array,
                                    pen=pg.mkPen(color='#803300'),
                                    name='T3')

        self.canvas.nextRow()

        self.axp = self.canvas.addPlot(1, 0, 1, 1)
        self.axp.setAxisItems({'bottom': pg.DateAxisItem()})    
        self.axp.setLabel('left', 'Pressure', units='hPa')        
        self.pLine = self.axp.plot(timeArray, pArray,
                                   pen=pg.mkPen(color='#1ad1ff'))

        # humidity plot

        self.axh = self.canvas.addPlot(1, 1, 1, 1)
        self.axh.setAxisItems({'bottom': pg.DateAxisItem()})
        self.axh.setLabel('left', 'Relative humidity', units='%')    
        self.hLine = self.axh.plot(timeArray, hArray,
                                   pen=pg.mkPen(color='#ff0000'))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(0)

        self.resize(800, 600)
        self.center()
        self.setWindowTitle('Sonda [NOT FINISHED]')

        self.show()

    def update_gui(self):

        global t1Array, t2Array, t3Array, pArray, hArray, timeArray

        # data, err = self.pyard.update_data()

        def update_gui_value(label, array, line):
            try:
                label.setText("{:.1f}".format(array[-1]))
            except:
                label.setText("?")
            line.setData(timeArray, array)

        update_gui_value(self.t1Value, t1Array, self.t1Line)
        update_gui_value(self.t2Value, t2Array, self.t2Line)
        update_gui_value(self.t3Value, t3Array, self.t3Line)
        update_gui_value(self.pValue, pArray, self.pLine)
        update_gui_value(self.hValue, hArray, self.hLine)   

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:

            event.accept()
        else:

            event.ignore()


def main(port):
    print("Detecting Arduino board...")
    ard_present = False

    # def sendto_ard(ard, s):
    #     ard.write(s.encode())
    #     ard.write('>'.encode())  # end character
    while not ard_present:
        ard = serial.Serial(port, 9600)
        ard_present = True
        print("Arduino detected in port: {}".format(port))
        ard.flushInput()
        # ard_update_interval = input(
        #     'Update interval (in seconds): ')
        # sendto_ard(ard, str(int(ard_update_interval) // 8))
        # ard_measure = input(
        #     '''
        #     Duration of the measurements (in minutes,
        #     0 for indefinite measurements: ''')
        # sendto_ard(ard, ard_measure)
        ard_present = True

    pyard = PyArd(ard)

    return 0

if __name__ == '__main__':

    port = input('Arduino port: ')

    main(port)