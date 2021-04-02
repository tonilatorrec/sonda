# sonda

Data logging with Arduino and Python.

## Arduino sketches

The `weather` script contains the code for basic data logging. The output is shown as a formatted table via serial port, and is best used with a serial port monitor.

The `weather-esp-serial` script is based on `weather` but designed for **ESP8266 devices**. The output is raw-formatted, which may be useful when the data is sent to another program, for example the `sonda.js` script included in the repository.

The `weather-esp-wifi` script is based on `weather-esp-serial` but also sends the data to a ThingSpeak server. Note that some parameters (ThingSpeak API, WiFi network name and password) have to be changed by the corresponding values.
