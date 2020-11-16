// libraries

#include "DHT.h"  // DHT sensor library
#include <SFE_BMP180.h>  // BMP180 sensor library
#include <ESP8266WiFi.h>

SFE_BMP180 bmp;  // BMP180 sensor
#define ALT 330.0  // ground elevation (in meters)

#define DHTPIN D6  // Digital pin the DHT "out" pin is connected to 
#define DHTTYPE DHT22  // our DHT sensor is a DHT22 type
DHT dht(DHTPIN, DHTTYPE); // DHT sensor

// WiFi parameters
// replace wifi-ssid with your wifi network's name
String AP = "wifi-ssid";
// replace wifi-password with your network's password
String PASS = "wifi-password";

// ThingSpeak parameters
String HOST = "184.106.153.149"; // api.thingspeak.com
int PORT = 80;
// replace api with the API key of your ThingSpeak channel
String API = "api"; 
// four fields: temperature 1, temperature 2, sea-level pressure, relative humidity
String fields[] = {"&field1=", "&field2=", "&field3=", "&field4="};

WiFiClient client;

// variables
float T1 = 0;  // DHT22 temperature (ºC)
double T2 = 0;  // BMP180 temperature (ºC)
double p = 0;  // BMP180 absolute pressure (hPa)
double p0 = 0; // BMP180 sea-level pressure (hPa)
float U = 0;   // DHT22 relative humidity (%)

byte i;  // counter

void setup() {

  Serial.begin(9600);
  bmp.begin();  // initializes BMP180 sensor
  dht.begin();  // initializes DHT22 sensor
  
  WiFi.begin(AP, PASS); // initializes WiFi
  i = 0;
  while (WiFi.status() != WL_CONNECTED and i < 10) { 
    // checks 10 times for a connection
    delay(500);
    i++;
  }

  Serial.println("CONNECTED");

  if (i < 10) 
  {

    delay(7000);

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
  
    // convert each measurement to string
  
    char buf_T1[16];
    String strT1 = dtostrf(T1, 4, 1, buf_T1);
  
    char buf_T2[16];
    String strT2 = dtostrf(T2, 4, 1, buf_T2);
  
    char buf_p[16];
    String strp = dtostrf(p0, 5, 1, buf_p);
  
    char buf_U[16];
    String strU = dtostrf(U, 4, 1, buf_U);
  
    String strData[] = {strT1, strT2, strp, strU};
  
    // send data
  
    if (client.connect(HOST, PORT)) {
  
      // prepares string to send
      String sendData = API;
      for (int j = 0; j < 4; j++) {
        sendData += fields[j];
        sendData += String(strData[j]);
      }
      sendData += "\r\n\r\n";
      
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
  
    Serial.print("T");
    Serial.print(T1);
    Serial.print("T");
    Serial.print(T2);
    Serial.print("P");
    Serial.print(p0, 2);
    Serial.print("U");
    Serial.println(U);
  }
  
  delay(200);
  // puts the board into deep sleep mode for 20 minutes
  ESP.deepSleep(20*60*1e6);
  

}

void loop() {

}
