from random import gauss, choice
from typing import Tuple, List, Optional
from cfg import *
import datetime

from datetime import datetime as dt

import requests
import json


def gen_random_measurement(
        mu: float, sigma: float, min_val: Optional[float],
        max_val: Optional[float]) -> Tuple[float, bool]:
    """Generates a random measurement (value and flag, i.e. whether the
    measurement is valid or not). The value is generated using a Gaussian
    distribution.

    Args:
        mu, sigma: mean and variance of the Gaussian
            distribution
        
    Returns:
        meas: tuple (value, validity) of the measurement
    """
    flag = choice([True, False])
    value = gauss(mu, sigma)

    if min_val is not None and value < min_val:
        value = min_val 
    if min_val is not None and value > max_val:
        value = max_val

    measurement = (value, flag)
    return measurement


# def rand(mu, sigma, min=False, max=False):
#     '''
#     Creates a random value from a single variable
#     using a Gaussian distribution.
#     Used for testing.
#     '''

#     stat = choice([0, 1])  # whether the value will be valid
#     val = gauss(mu, sigma)
#     if val < min:
#         val = min
#     elif val > max:
#         val = max

#     return val, stat

def gen_all_random_measurements() -> Tuple[List[float], List[float]]:
    temp1, val_temp1 = gen_random_measurement(20, 0.1, None, None)
    temp2, val_temp2 = gen_random_measurement(21, 0.3, None, None)
    pres, val_pres = gen_random_measurement(1000, 0.8, None, None)
    hum, val_hum = gen_random_measurement(65, 3, None, None)
    recep_time = dt.now().timestamp() # reception time

    list_of_values = [temp1, temp2, pres, hum, recep_time]
    list_of_flags = [val_temp1, val_temp2, val_pres, val_hum, True]

    return list_of_values, list_of_flags

# def from_rand():

#     # t1, stat_t1 = rand(mu=20, sigma=0.1, min=float(temp1.minVal), max=float(temp1.maxVal))
#     t1, stat_t1 = rand(mu=20, sigma=0.1, min=0, max=10)
#     t2, stat_t2 = rand(mu=21, sigma=0.3, min=0, max=10)
#     p, stat_p = rand(mu=1000, sigma=0.8, min=0, max=10)
#     u, stat_u = rand(mu=65, sigma=3, min=0, max=100)
#     rec_time = datetime.datetime.now().timestamp()

#     data = [t1, t2, p, u, rec_time]
#     stat = [stat_t1, stat_t2, stat_p, stat_u, 0]
#     return data, stat

def from_serial(serial):
    """
    Receives data from a serial port.
    Data must be sent in the following format:
        temp1;temp2;pres;hum

    Args:
        serial (serial.Serial): Serial port which sends the data

    Returns:
        data (list): values of each mesure + reception time
        stat (list): status of each measure
    """
    while serial.inWaiting() == 0:
        pass  # waits for new data
    rec_time = dt.now().timestamp()

    list_of_values = str(serial.readline(), encoding='utf-8').split(';')
    list_of_values.append(rec_time)  # appends data reception time
    list_of_flags = check_data(list_of_values)
    return list_of_values, list_of_flags

def recv_from_thingspeak(channel, key):
    '''
    Receives data from a ThingSpeak™ channel.
    '''
    
    url = f'https://api.thingspeak.com/channels/{channel}/feeds.json?api_key={key}&results=2'
    response = requests.get(url)
    recv_string = response.json()['feeds'][1]

    # fields: temp1, temp2, pres, hum
    list_of_values = []
    for i in range(1, 5):
        list_of_values.append(float(recv_string[f'field{i}']))
    rec_time = datetime.datetime.strptime(
        recv_string['created_at'], '%Y-%m-%dT%H:%M:%SZ').timestamp()

    list_of_values.append(rec_time)
    list_of_flags = check_data(list_of_values)
    return list_of_values, list_of_flags


def from_rss():
    '''
    Receives data from a RSS feed.
    '''
    pass


def check_data(data):
    '''
    Checks the quality of the measures.
    '''
    return [0, 0, 0, 0, 0]