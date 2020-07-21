// libraries

#include "DHT.h"  // DHT sensor library
#include <OneWire.h>  // needed for DS18B20 sensor
#include <SFE_BMP180.h>  // BMP180 sensor library
#include "LowPower.h"  // power saving library

SFE_BMP180 bmp;  // BMP180 sensor
#define ALT 330.0  // ground elevation (in meters)

#define DHTPIN 2  // Arduino digital pin the DHT "out" pin is connected to 
#define DHTTYPE DHT22  // our DHT sensor is a DHT22 type
DHT dht(DHTPIN, DHTTYPE); // DHT sensor

OneWire ds(8); // Arduino digital pin the DS18B20 "yellow" pin is connected to

// variables
float T1 = 0;  // DHT22 temperature (ºC)
float T2 = 0;  // DS18B20 temperature (ºC)
double T3 = 0; // BMP180 temperature (ºC)
double p = 0;  // BMP180 absolute pressure (hPa)
double p0 = 0; // BMP180 sea-level pressure (hPa)
float U = 0;   // DHT22 relative humidity (%)

byte j;  // counter

void setup() {
  
  Serial.begin(9600);
  bmp.begin();  // initializes BMP180 sensor
  dht.begin();  // initializes DHT22 sensor
}

void loop() {

    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);  

  // DS18B20 measurements
  // extracted from the "DS18x20_Temperature" example in the OneWire library.

  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];
  byte addr[8];
  
  // searches the address of the DS18B20 sensor
  if ( !ds.search(addr)) {
    ds.reset_search();
    delay(250);
    return;
  }
  
  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end
  
  delay(1000);     // maybe 750ms is enough, maybe not
  // we might do a ds.depower() here, but the reset will take care of it.
  
  present = ds.reset();
  ds.select(addr);    
  ds.write(0xBE);         // Read Scratchpad

  for ( i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
  }

  // Convert the data to actual temperature
  // because the result is a 16 bit signed integer, it should
  // be stored to an "int16_t" type, which is always 16 bits
  // even when compiled on a 32 bit processor.
  int16_t raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3; // 9 bit resolution default
    if (data[7] == 0x10) {
      // "count remain" gives full 12 bit resolution
      raw = (raw & 0xFFF0) + 12 - data[6];
    }
  } else {
    byte cfg = (data[4] & 0x60);
    // at lower res, the low bits are undefined, so let's zero them
    if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
    else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
    else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
    //// default is 12 bit resolution, 750 ms conversion time
  }
  
  T2 = (float)raw / 16.0;

  // DHT22 measurements

  T1 = dht.readTemperature();
  U = dht.readHumidity();

  // BMP180 measurements
  
   char status;
  status = bmp.startTemperature();
  if (status != 0)
  {
    delay(status);
    status = bmp.getTemperature(T3);
    if (status != 0)
    {
      status = bmp.startPressure(3);
      if (status != 0)
      {
        delay(status);
        status = bmp.getPressure(p,T3);
        // corrects pressure to sea-level 
        p0 = bmp.sealevel(p,ALT);
      }
    }
  }
    Serial.print(T1);
    Serial.print(";");
    Serial.print(T2);
    Serial.print(";");
    Serial.print(T3);
    Serial.print(";");
    Serial.print(p0,2);
    Serial.print(";");
    Serial.println(U);
    delay(2000);
    for (j = 0; j < 3; j++){  // shuts down the board for 24 s
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF); 
    }
  
}
