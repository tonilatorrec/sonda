import configparser
import datetime
import re

from numpy import nan

validVarNames =  ['temp', 'slp', 'pres', 'hum', 'lat', 'lng', 'alt',
                  'ws', 'wd']

def parse_variable_name(s):

    try:
        match, = re.findall(r'(\w+)(\d+)', s)
        if match:
            if match[0] in validVarNames:
                var_type = match[0]
                number = match[1]
            else:
                print('Invalid variable name: {}'.format(s))
                quit()
    except ValueError:
        match = re.search(r'(\w+)', s)
        if match:
            g = match.group
            if g(0) in validVarNames:
                var_type = s
                number = 0
            else:
                print('Invalid variable name: {}'.format(s))
                quit()
        else:
            print('Invalid variable name: {}'.format(s))
            quit()
    return var_type, number

class WeatherVar():

    # Altitude is actually a weather variable,
    # but it works like weather variables

    def __init__(self, type, number):

        self.type = type
        self.number = number
        if self.number:
            self.name = self.type + ' {}'.format(number)
        else:
            self.name = self.type
        self.units = config[name]['units']
        self.resolution = config[name]['resolution']
        self.systError = config[name]['systError']
        self.minVal = float(config[name]['minVal'])
        self.maxVal = float(config[name]['maxVal'])

        self.array = [nan]  # list where all data is stored
        self.status = 0  # status of the current variable
        self.value = 50  # variable value in the GUI

    def updateVal(self, value, status):
        '''
        Updates a variable with new data.
        '''
        self.value = value
        self.array.append(self.value)
        self.status = status

class TimeVar():

    def __init__(self, name):

        self.name = 'Time'
        self.array = [datetime.datetime.now().timestamp()]
        self.value = datetime.datetime.now().timestamp()

    def updateVal(self, value, status):
        '''
        Updates a variable with new data.
        '''
        self.value = value
        self.array.append(float(self.value))

config = configparser.ConfigParser()
config.read('arduino.cfg')

nvar = len(config['vars'])
dict_weather_vars = dict()
list_weather_vars = []

for i in range(1, nvar + 1):
    name = config['vars']['var{}'.format(i)]
    var_type, number = parse_variable_name(name)
    if var_type not in dict_weather_vars.keys():
        dict_weather_vars.update({var_type: []})
    dict_weather_vars[var_type].append(WeatherVar(var_type, number))
    list_weather_vars.append(dict_weather_vars[var_type][-1])

time = TimeVar('time')

weatherVarTypes = list(dict_weather_vars.keys())
