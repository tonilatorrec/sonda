// Version to use with ESP8266 devices (WiFi output)
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
#include <ESP8266WiFi.h> // ESP8266 WiFi library

SFE_BMP180 bmp;  // BMP180 sensor

#define DHTPIN D6  // Digital pin the DHT "out" pin is connected to 
#define DHTTYPE DHT22  // our DHT sensor is a DHT22 type
DHT dht(DHTPIN, DHTTYPE); // DHT sensor

// WiFi parameters
// Replace with your wifi network's name
String AP = "YOUR-WIFI-NETWORK";
// Replace with your network's password
String PASS = "YOUR-WIFI-PASSWORD";

// ThingSpeak parameters
String HOST = "184.106.153.149"; // api.thingspeak.com
int PORT = 80;
// Replace with the API key of your ThingSpeak channel
String API = "YOUR-THINGSPEAK-API"; 
// Fields to be uploaded to ThingSpeak
// In this case I report three fields: temperature, pressure, and relative humidity
String fields[] = {"&field1=", "&field2=", "&field3="};

WiFiClient client;

// Constants
#define ALT 330.0  // ground elevation (in meters)

// Variables
float T = 0;  // DHT22 temperature (ºC)
double p0 = 0; // BMP180 sea-level pressure (hPa)
float U = 0;   // DHT22 relative humidity (%)

byte i;  // counter

void setup() {
  Serial.begin(9600);
  bmp.begin();  // initializes BMP180 sensor
  dht.begin();  // initializes DHT22 sensor

  WiFi.begin(AP, PASS); // initializes WiFi
  // Maximum number of times the board will try to connect to the Internet
  int max_connection_attempts = 30; 
  i = 0;
  while (WiFi.status() != WL_CONNECTED and i < max_connection_attempts) { 
    // checks 30 times for a connection
    delay(500);
    i++;
  }

  if (i < 30) 
  {
	Serial.println("CONNECTED");
    delay(7000);

  // Serial output
  Serial.flush();
  delay(1000);
  Serial.println("+----------------+----------------+---------------+");
  Serial.println("| Temp. (±0.5ºC) | Humidity (±1%) | Pres. (±1 hPa)|");
  Serial.println("+----------------+----------------+---------------+");  
	
	// Measurements
	T = get_temperature();
	U = get_humidity();
	p0 = get_pressure();

    // Send data
  
    if (client.connect(HOST, PORT)) {
  
		// Prepares the output (converts measurements to strings)
	  
		char buf_T[16];
		String strT = dtostrf(T, 4, 1, buf_T);
	  
		char buf_p[16];
		String strp = dtostrf(p0, 5, 1, buf_p);
	  
		char buf_U[16];
		String strU = dtostrf(U, 4, 1, buf_U);
	  
		String strData[] = {strT, strp, strU};
  
      String sendData = API;
      for (int j = 0; j < 4; j++) {
        sendData += fields[j];
        sendData += String(strData[j]);
      }
      sendData += "\r\n\r\n";
	  
	  // Makes the POST request
      
      client.print("POST /update HTTP/1.1\n");
      client.print("Host: api.thingspeak.com\n");
      client.print("Connection: close\n");
      client.print("X-THINGSPEAKAPIKEY: "+API+"\n");    
      client.print("Content-Type: application/x-www-form-urlencoded\n");
      client.print("Content-Length: ");
      client.print(sendData.length());
      client.print("\n\n");
      client.print(sendData);
      Serial.print("SENT: ");
    }
	
	else {
		Serial.println("UNABLE TO POST TO API");
	}
	
  // Serial output
  // The data format (temperature, pressure, humidity) is as follows:

  // "+----------------+----------------+----------------+"
  // "| Temp. (±0.5ºC) | Humidity (±1%) | Pres. (±1 hPa) |"
  // "+----------------+----------------+----------------+"
  // "|     +xx.xx     |      xxx       |     xxxx.x     |"
  // "+----------------+-----------------+---------------+"
  
  Serial.print("|     ");
  Serial.print(T);
  Serial.print("      |      ");
  Serial.print(U);
  Serial.print("     |    ");
  Serial.print(p0, 1);
  Serial.println("     |");
  Serial.println("+----------------+----------------+---------------+");
  
  }
  else {
	  Serial.println("CONNECTION FAILED");
  }
  
  delay(200);
  // Amount of time (minutes) the board will be put into deep sleep
  int deep_sleep_minutes = 5;
  ESP.deepSleep(deep_sleep_minutes*60*1e6);
}

void loop() {

}


float get_temperature() {
	// Temperature measured by DHT22
	return dht.readTemperature();
}

float get_humidity() {
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
