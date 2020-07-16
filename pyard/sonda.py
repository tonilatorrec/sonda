#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import datetime
import atexit
import locale
import time
import sys

# gui modules
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QToolTip, QPushButton, QApplication
from PyQt5.QtGui import QFont

class PyArd():

    def get_data(self, old_data, test):
        '''
        Receives data from the board and checks whether the values
        are correct. The data is stored as a list:
            [ temp1, temp2, temp3, pres, hum, time ].
        The stat list contains the quality of the measures in the
        same order (0: correct, 1: incorrect).

        Args:
            old_data (list): values from the last measurements;
                             (empty list for first measurement)
            test (bool): true if the mode is set to 'test' or 'test_nogui'

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
            data = str(self.ard.readline(), 'utf-8').split(';')
            if len(data) <= 2:
                return from_ard(old_data)
            else:
                return data

        new_data = from_ard(old_data)
        # adds reception time, not measurement time
        new_data.append(datetime.datetime.now())
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

    def init_cmd(self, test):
        """
        Runs the program in command line mode.
        
        Args:
            test (bool): true if the program runs in test mode
        """

        counter = 0
        rule = '|{}|{}|{}|{}|{}|{}|'.format(
              '-' * 21, '-' * 10, '-' * 10, '-' * 10, '-' * 10, '-' * 10)

        print(rule)
        # header
        print('| {:<19} | {:<8} | {:<8} | {:<8} | {:<8} | {:<8} |'.format(
              'Time', 'Temp. 1', 'Temp. 2', 'Temp. 3', 'Pres.',
              'Hum. (%)'))
        # units and sensor uncertainties
        print('| {:<19} | {:<8} | {:<8} | {:<8} | {:<8} | {:<8} |'.format(
              'dd/mm/aaaa hh:mm:ss', '± 0.5ºC', '± 0.5ºC', '± 0.5ºC',
              '± 1 hPa', '± 2%'))
        print(rule)

        # measurement loop
        while True:
            data, stat = self.update_data(counter)

            # prints the values
            self.data_line = '| {:<19} |'.format(data[5].strftime('%x %X'))
            val = lambda i : ' {:8.1f} |'.format(float(data[i])) if stat[i] else ' {:<8} '.format('nan')
            for i in range(5):
                self.data_line += val(i)
            print(self.data_line, end='\r')

            if mode == 'test_nogui':
                time.sleep(2)

            counter += 1

    def __init__(self, ard, mode):
        super().__init__()
        self.ard = ard  # arduino board

        # defines what to do after exiting
        atexit.register(self.exit_handler)

        self.data = [0, 0, 0, 0, 0, 0]
        self.temp1_arr = []
        self.temp2_arr = []
        self.temp3_arr = []
        self.pres_arr = []
        self.hum_arr = []
        self.time_arr = []

        if mode == 'gui' or mode == 'test':
            # imports modules needed for GUI

            # starts in GUI mode
            app = QApplication(sys.argv)
            plot = ArdPlot()
            sys.exit(app.exec_())
        else:
            # starts in command line mode
            self.init_cmd(test)

    def update_data(self, counter):
        '''
        Función que actualiza todos los datos de la placa Arduino.
        La diferencia con la función first_data es que esta función revisa
        si los datos recibidos tienen sentido o hemos recibido valores
        incorrectos debido a la instrumentación
        '''
        if not test:
            if not counter:
                data = []
            else:
                data = self.data
            data = self.data
            data, stat = self.get_data(data, test)
            self.time_arr.append(data[5])
        else:  # sample data in test mode
            data = ['20.0', '0.0', '-50.0', '999', '0.0', datetime.datetime.now()]
            self.time_arr.append(data[5])
            stat = [1, 1, 1, 1, 1, 1]

        return data, stat


    def exit_handler(self):
        '''
        Stores measured data in a .dat file when exiting the app
        '''

        exit_time = datetime.datetime.now()
        ofilename = 'res_{}.dat'.format(exit_time.strftime("%d%m%y_%H%M%S"))
        if test:
            ofilename += '_test'

        with open('./res/' + ofilename, 'w+', newline='') as self.ofile:
            locale.setlocale(locale.LC_ALL, '')
            for i in range(len(self.temp1_arr)):
                self.ofile.write('{}\t{:.1f}\t{:.2f}\t{:.1f}\t{:.1f}\t{:.1f}\n'.format(
                    self.time_arr[i].strftime("%d/%m/%y %H:%M:%S"),
                    self.temp1_arr[i], self.temp2_arr[i],
                    self.temp3_arr[i], self.pres_arr[i],
                    self.hum_arr[i]))

        print('Exit!')

class ArdPlot(QWidget):

    def __init__(self):
        super().__init__()

        self.init_gui(test)

    def init_gui(self, test):

        qbtn = QPushButton('Exit', self)
        qbtn.clicked.connect(QApplication.instance().quit)

        qbtn.setToolTip('Exit the program')
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(150, 150)

        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Sonda [NOT FINISHED]')

        self.show()

def main(port, mode):
    if not test:
        print("Detecting Arduino board...")
        ard_present = False

        def sendto_ard(ard, s):
            ard.write(s.encode())
            ard.write('>'.encode())  # carácter final
        while not ard_present:
            if mode != 'test' and mode != 'test_nogui':
                ard = serial.Serial(port, 9600)
                ard_present = True
            else:
                continue
            print("Arduino detected in port: {}".format(port))
            ard.flushInput()
            ard_update_interval = input(
                'Update interval (in seconds): ')
            sendto_ard(ard, str(int(ard_update_interval) // 8))
            ard_measure = input(
                '''
                Duration of the measurements (in minutes,
                0 for indefinite measurements: ''')
            sendto_ard(ard, ard_measure)
            # enviar datos a la placa por serial
            ard_present = True
    else:
        ard = 0

    pyard = PyArd(ard, mode)

    return 0

if __name__ == '__main__':
    global test
    test = True
    port = 0

    modes = ['test', 'test_nogui', 'gui', 'nogui']
    mode = ''
    while mode not in modes:
        mode = input('Mode: ')

    if mode != 'test' and mode != 'test_nogui':
        port = input('Arduino port: ')
        test = False
    main(port, mode)
