# sonda

Data logging with Arduino and Python

## Python
Usage:

```
python sonda.py [-m MODE] [-p PORT]
```

* `MODE` is the mode in which the program will run (for now only test mode; for normal mode, leave this argument blank)
* `PORT` is the serial port address where the Arduino board is connected.

Test mode: 
```
python sonda.py -m test
```
## Arduino

The board must have the `pysonda.ino` file in order to use the Python script.


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

The `sonda.ino` file contains the whole flight computer code. The additional components are:
Component | Component pin | Arduino pin
--------- | ------------- | -----------
LC Studio SD card module | CS | D10
U-blox MAX-M8C (GPS) | TXD | D4
Radiometrix NTX2B | 7 | D9
