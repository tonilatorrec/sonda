from random import gauss, choice
from cfg import *
import datetime
import requests
import json


def rand(mu, sigma, min=False, max=False):
    '''
    Creates a random value from a single variable
    using a Gaussian distribution.
    Used for testing.
    '''

    stat = choice([0, 1])  # whether the value will be valid
    val = gauss(mu, sigma)
    if val < min:
        val = min
    elif val > max:
        val = max

    return val, stat

def from_rand():

    t1, stat_t1 = rand(mu=20, sigma=0.1, min=float(temp1.minVal), max=float(temp1.maxVal))
    t2, stat_t2 = rand(mu=21, sigma=0.3, min=float(temp2.minVal), max=float(temp2.maxVal))
    p, stat_p = rand(mu=1000, sigma=0.8, min=float(pres.minVal), max=float(pres.maxVal))
    u, stat_u = rand(mu=65, sigma=3, min=float(hum.minVal), max=float(hum.maxVal))
    rectime = datetime.datetime.now().timestamp()

    data = [t1, t2, p, u, rectime]
    stat = [stat_t1, stat_t2, stat_p, stat_u, 0]
    return data, stat

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
    rectime = datetime.datetime.now().timestamp()
    data = str(serial.readline(), 'utf-8').split(';')
    data.append(rectime)  # appends data reception time
    stat = check_data(data)
    return data, stat

def from_ts(channel, key):
    '''
    Receives data from a ThingSpeak™ channel.
    '''
    
    url = 'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&results=2'.format(
          channel, key)
    response = requests.get(url)
    txt = response.json()['feeds'][1]

    # fields: temp1, temp2, pres, hum
    data = []
    for i in range(1, 5):
        data.append(float(txt['field{}'.format(i)]))
    rectime = datetime.datetime.strptime(txt['created_at'], '%Y-%m-%dT%H:%M:%SZ').timestamp()
    data.append(rectime)
    stat = check_data(data)
    return data, stat


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