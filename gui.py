from time import sleep
import threading

from PyQt6.QtWidgets import *
from PyQt6 import QtCore
import pyqtgraph as pg

import styles
from cfg import *

from getdata import (
    gen_all_random_measurements, recv_from_thingspeak
)

class FirstCfgWindow(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.enter_app_button = QPushButton("Enter the app")
        layout.addWidget(self.enter_app_button)

        self.setLayout(layout)


class App(QMainWindow):
    """Application"""

    def __init__(self, test, mode, port, api, channel):

        super().__init__()

        self.title = "Weather station"
        self.setWindowTitle(self.title)

        self.test = test
        self.mode = mode
        self.port = port
        self.api = api
        self.channel = channel

        # Initialize first configuration window
        self.firstcfg = FirstCfgWindow()

        # Clicking on this button initializes the main GUI
        enter_app_button = self.firstcfg.enter_app_button 
        enter_app_button.clicked.connect(self.init_gui)

        self.firstcfg.show()

    def init_gui(self):
        """Initializes the GUI"""

        # Initialize GUI variables
        self.grid = QGridLayout()
        self.canvas = pg.GraphicsLayoutWidget()
        grid_widget = QWidget(self)
        grid_widget.setLayout(self.grid)
        self.setCentralWidget(grid_widget)

        if self.mode == 'test': 
            self.title += (" [test mode]")
        self.setWindowTitle(self.title)

        self.setStyleSheet(styles.windowStyle)

        # Setup grid
        self.grid.setSpacing(5)

        # Setup plot canvas
        self.canvas.setContentsMargins(20, 10, 20, 10)
        self.canvas.setBackground(styles.bgCanvas)
        self.grid.addWidget(self.canvas, 0, 0, 1, 2)

        for var in (x for x in list_weather_vars if x != time):
            # Initialize variable labels
            var.title_label = QLabel()  # variable name displayed in GUI
            var.value_label = QLabel()  # value of variable

            var.title_label.setText(f'{var.name} ({var.units})')
            var.title_label.setStyleSheet(styles.titleStyle)
            var.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            # TODO: Add (systematic) uncertainties due to the components' resolution.
            # var.error = var.systError
            # var.errorLabel = QLabel('± {}{}'.format(var.error, var.units))

            var.value_label.setText("??")
            var.value_label.setStyleSheet(styles.valueLabelStyle)
            var.value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.add_value_widgets(self.grid)
        self.add_subplots()

        gui_thread = threading.Thread(target=self.update_data)
        gui_thread.daemon = True
        gui_thread.start()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(0)

        self.firstcfg.close()
        self.show()

    def add_value_widgets(self, grid):
        j = 1
        for line in config['var_grid']:
            row = config['var_grid'][line].split(';')
            for i in range(len(row)):
                n = int(row[i][-1])
                # Add widgets for variable name (title) and value
                grid.addWidget(list_weather_vars[n-1].title_label, j, i)
                grid.addWidget(list_weather_vars[n-1].value_label, j+1, i)
            j += 2

    def add_subplots(self):
        num_rows_in_grid = len(config['plot_grid'])
        for i in range(1, num_rows_in_grid + 1):
            row = config['plot_grid'][f'row{i}'].split(';')
            
            for j, magnitude in enumerate(row):
                self.init_subplot(magnitude, (i, j, 1, 1))

    def init_subplot(self, magnitude, pos):
        """Adds a subplot for every magnitude, i.e. two measurements
        of the same magnitude will share the same subplot.

        Args:
            magnitude (_type_): _description_
            pos (_type_): _description_
        """

        pen = pg.mkPen(color=styles.plotPenColor)
        p = self.canvas.addPlot(*pos)
        p.setAxisItems({'bottom': pg.DateAxisItem(pen=pen, textPen=pen),
                        'left': pg.AxisItem(orientation='left', pen=pen,
                                            textPen=pen)})

        for i, v in enumerate(dict_weather_vars[magnitude]):
            if i == 0:
                p.setLabel('left', text=v.type, units=v.units)
            v.line = p.plot(time.array, v.array,
                            pen=pg.mkPen(color=styles.linePenColors[i]),
                            name=v.name)

        # Add legend if there is more than one variable for that magnitude
        if len(dict_weather_vars[magnitude]) > 1:
            p.addLegend()

    def update_data(self):
        '''
        Updates the plots and the GUI with new data.
        '''
        while True:
            if self.mode == 'test':
                data, stat = gen_all_random_measurements()
            elif self.mode == 'api':
                upd = False
                while not upd:
                    try:
                        data, stat = recv_from_thingspeak(channel=self.channel,
                                                     key=self.api)
                        if data[-1] != time.value:
                            upd = True
                    except:
                        continue
            for i in range(len(list_weather_vars)):
                list_weather_vars[i].updateVal(data[i], stat[i])
            time.updateVal(data[-1], stat[-1])
            sleep(10)

    def update_gui(self):
        for var in list_weather_vars:
            var.value_label.setText("{:.1f}".format(var.value))
            var.line.setData(time.array, var.array)

    def closeEvent(self, event):
        """Close event"""
        reply = QMessageBox.question(
            self, 'Message', "Are you sure to quit?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # TODO: Save data in a CSV file
            event.accept()
        else:
            event.ignore()
