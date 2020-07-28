# sonda

Data logging with Arduino and Python.

## Arduino

The `pysonda.ino` file contains the basic data logging code. Coupled with the Python script `sonda.py`, can also be used as a weather station.

The `sonda.ino` file contains the full flight computer code for a high-altitude balloon (requires tracking by radio, see the tracking guide [here](https://ukhas.org.uk/guides:tracking_guide))

### Data structure
`pysonda.ino`:
```
T1;T2;T3;P0;U
```

`sonda.ino`:
```
T1;T2;T3;P0;U;ALT(BMP);LAT;LNG;ALT(GPS);HH:MM:SS
```
### Wiring
Specifical wiring for this code (apart from VIN/GND connections).

| Component | Component pin | Arduino pin |
| --------- | ------------- | ----------- |
| BMP180 (temp&pres sensor) | SCL | A5 |
| BMP180 (temp&pres sensor) | SDA | A4 |
| DHT22 (temp&hum sensor) | out | D2 |
| DS18B20 (temp sensor) | yellow | D8 |

For the flight computer code, the additional components are:

Component | Component pin | Arduino pin
--------- | ------------- | -----------
LC Studio SD card module | CS | D10
U-blox MAX-M8C (GPS) | TXD | D4
Radiometrix NTX2B | 7 | D9

## Python
`sonda.py` usage:

```
python sonda.py [-m MODE] [-p PORT]
```

* `MODE` is the mode in which the program will run (for now only test mode; for normal mode, leave this argument blank)
* `PORT` is the serial port address where the Arduino board is connected.

Test mode: 
```
python sonda.py -m test
```
