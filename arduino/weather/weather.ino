// libraries

#include "DHT.h"  // DHT sensor library
#include <SFE_BMP180.h>  // BMP180 sensor library

SFE_BMP180 bmp;  // BMP180 sensor
#define ALT 330.0  // ground elevation (in meters)

#define DHTPIN D6  // Digital pin the DHT "out" pin is connected to 
#define DHTTYPE DHT22  // our DHT sensor is a DHT22 type
DHT dht(DHTPIN, DHTTYPE); // DHT sensor

// variables
float T1 = 0;  // DHT22 temperature (ºC)
double T2 = 0;  // BMP180 temperature (ºC)
double p = 0;  // BMP180 absolute pressure (hPa)
double p0 = 0; // BMP180 sea-level pressure (hPa)
float U = 0;   // DHT22 relative humidity (%)

void setup() {

  Serial.begin(9600);
  bmp.begin();  // initializes BMP180 sensor
  dht.begin();  // initializes DHT22 sensor
}

void loop() {

    // DHT22 measurements
  
    T1 = dht.readTemperature();
    U = dht.readHumidity();
  
    // BMP180 measurements
  
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
  
    Serial.print("T"); // DHT
    Serial.print(T1);
    Serial.print("T"); // BMP
    Serial.print(T2);
    Serial.print("P");
    Serial.print(p0, 2);
    Serial.print("U");
    Serial.println(U);

    delay(5000);
}  
