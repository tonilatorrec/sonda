# sonda

Data logging with Arduino and Python.

## Arduino sketches

The `basic.ino` sketch contains the code for basic data logging (two temperatures, pressure and humidity). It is best used as a weather station with the `weather.py` script. 

The `sonda.ino` sketch contains the code for a high-altitude balloon's flight computer (requires tracking by radio, see the tracking guide [here](https://ukhas.org.uk/guides:tracking_guide)).

### Wiring
For both sketches:

| Component | Component pin | Arduino pin |
| --------- | ------------- | ----------- |
| BMP180 (temp&pres sensor) | SCL | A5 |
| BMP180 (temp&pres sensor) | SDA | A4 |
| DHT22 (temp&hum sensor) | out | D2 |

Additional components for the `sonda.ino` sketch:

Component | Component pin | Arduino pin
--------- | ------------- | -----------
LC Studio SD card module | CS | D10
U-blox MAX-M8C (GPS) | TXD | D4
Radiometrix NTX2B | 7 | D9
DS18B20 (temp sensor) | yellow | D8 |


## Data structure

For each measurement, the `weather.py` script reads a string of the form `VAR1;VAR2;...;VARN` (N variables separated by semicolons). By default, it will parse this string according to the `basic.ino` sketch, `temp1;temp2;slp;hum` (temperature 1, temperature 2, sea-level pressure, relative humidity).

The string format can be changed in the `variables.json` file.
<!-- (see Configuration for instructions on how to declare the variables) -->
For instance, the `sonda.ino` sketch returns a string of the form `temp1;temp2;temp3;slp;hum;alt1;lat;lng;alt;HH:MM:SS` (temperatures 1, 2, 3; sea-level pressure, relative humidity, altitude computed by the pressure sensor, latitude, longitude, GPS altitude, time).

## Dependencies

For the `basic.ino` sketch:

* a
* b

For the `sonda.ino` sketch:

* a
* b

For the `weather.py` script:

* a
* b

## Running the `weather.py` script

```
python weather.py [-h] [-t] [-p PORT] [-b BAUD] [-a API]
```
where:

* `-h` shows the help message.
* `-t` executes the program in test mode (the values will be random numbers sampled from Gaussian distributions).
* `PORT` is the serial port address where the Arduino board is connected. If both `PORT` and `BAUD` are given, the program receives data from this serial port.
* `BAUD` is the baud rate at which the program will listen to the board. Only needed when `PORT` is specified.
* `API` is the ThingSpeak API from which the data is collected. If specified, the program receives data from a ThingSpeak channel.