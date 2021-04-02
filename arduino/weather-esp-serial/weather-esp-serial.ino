// Version to use with ESP8266 devices (serial output)
// Date: 11/03/2021

// Components used:
/*
	- Temperature and humidity: DHT22
	- Pressure: BMP180
*/

// Libraries
// Sensor libraries
#include "DHT.h"  // DHT sensor library
#include <SFE_BMP180.h>  // BMP180 sensor library

SFE_BMP180 bmp;  // BMP180 sensor

#define DHTPIN D6  // Digital pin the DHT "out" pin is connected to 
#define DHTTYPE DHT22  // our DHT sensor is a DHT22 type
DHT dht(DHTPIN, DHTTYPE); // DHT sensor

// Constants
#define ALT 330.0  // ground elevation (in meters)

// Variables
float T = 0;  // DHT22 temperature (ºC)
double p0 = 0; // BMP180 sea-level pressure (hPa)
float U = 0;   // DHT22 relative humidity (%)

void setup() {
  Serial.begin(9600);
  bmp.begin();  // initializes BMP180 sensor
  dht.begin();  // initializes DHT22 sensor

 // DHT22 measurements
  
	// Measurements
	T = get_temperature();
	U = get_humidity();
	p0 = get_pressure();
	
  	// Output
	// The data format (temperature, pressure, humidity) is as follows:
	// T+xx.xxPxxxx.xxUxx.x
    Serial.print("T");
    Serial.print(T);
    Serial.print("P");
    Serial.print(p0, 2);
    Serial.print("U");
    Serial.println(U);
    delay(5000);

// Puts the board into sleep mode for 80 seconds
    ESP.deepSleep(80*1e6);
}

void loop() {
 
}  

float get_temperature() {
	// Temperature measured by DHT22
	return dht.readTemperature();
}

float get_temperature() {
	// Humidity measured by DHT22
	return dht.readHumidity();
}

double get_pressure() {
	// Sea-level pressure measured by BMP180
	
	// In order to make a correction to the absolute pressure,
	// the BMP180 requires measuring the temperature.
	double T2;
	double p; // Absolute pressure (depends on the ground elevation)
	
    char status;
    status = bmp.startTemperature();
    if (status != 0)
    {
      delay(status);
      status = bmp.getTemperature(T2);
      if (status != 0)
      {
        status = bmp.startPressure(3);
        if (status != 0)
        {
          delay(status);
          status = bmp.getPressure(p, T2);
          // corrects pressure to sea level
          p0 = bmp.sealevel(p, ALT);
        }
      }
    }
	return p0;
}
