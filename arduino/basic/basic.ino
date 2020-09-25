// libraries

#include "DHT.h"  // DHT sensor library
#include <SFE_BMP180.h>  // BMP180 sensor library
#include "LowPower.h"  // power saving library
#include <SoftwareSerial.h>
#include <stdlib.h>

SFE_BMP180 bmp;  // BMP180 sensor
#define ALT 330.0  // ground elevation (in meters)

#define DHTPIN 5  // Arduino digital pin the DHT "out" pin is connected to 
#define DHTTYPE DHT22  // our DHT sensor is a DHT22 type
DHT dht(DHTPIN, DHTTYPE); // DHT sensor

// ESP8266 serial ports
#define RX 2
#define TX 3
#define DEBUG true
String HOST = "184.106.153.149";
String PORT = "80";
String AP = "vodafone5940";
String PASS = "94C6QW6WDKMDDC";

String API = "HH33RKFT8EWT7SQX";
String fields[] = {"&field1=", "&field2=", "&field3=", "&field4="};

int sendVal;

SoftwareSerial espSerial(RX, TX);

// variables
float T1 = 0;  // DHT22 temperature (ºC)
double T2 = 0;  // BMP180 temperature (ºC)
double p = 0;  // BMP180 absolute pressure (hPa)
double p0 = 0; // BMP180 sea-level pressure (hPa)
float U = 0;   // DHT22 relative humidity (%)

byte j;  // counter

void setup() {
  
  Serial.begin(115200);
  
  // initializes ESP8266 module
  espSerial.begin(115200);

  espData("AT+RST", 1000, DEBUG);
  espData("AT+CWMODE=1", 1000, DEBUG);
  espData("AT+CWJAP=\""+ AP +"\",\""+ PASS +"\"", 1000, DEBUG);  

  while(!espSerial.find("OK")) { //wait for connection
  Serial.println("Connecting...");} 
  Serial.println("Connected!");
  
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
        status = bmp.getPressure(p,T2);
        // corrects pressure to sea-level 
        p0 = bmp.sealevel(p,ALT);
      }
    }
  }
    Serial.print(T1);
    Serial.print(";");
    Serial.print(T2);
    Serial.print(";");
    Serial.print(p0,2);
    Serial.print(";");
    Serial.println(U);

    delay(2000);

    // convert measurements to string

    char buf_T1[16];
    String strT1 = dtostrf(T1, 4, 1, buf_T1);

    char buf_T2[16];
    String strT2 = dtostrf(T2, 4, 1, buf_T2);

    char buf_p[16];
    String strp = dtostrf(p, 5, 1, buf_p);

    char buf_U[16];
    String strU = dtostrf(U, 4, 1, buf_U);
    
    String strData[] = {strT1, strT2, strp, strU};

    // send data 

    String cmd = "AT+CIPSTART=\"TCP\",\"" + HOST + "\"," + PORT;
    espSerial.println(cmd);
    //Serial.println(cmd);

    //check for connection error
    if(espSerial.find("Error")||espSerial.find("closed")){
      Serial.println("AT+CIPSTART error");
      return;
      }

    // prepare GET string

    String getStr = "GET /update?key=" + API;
    for (j = 0; j < 4; j++){
      getStr += fields[j];
      getStr += String(strData[j]);
    }
    getStr += "\r\n";
    
    // send data length 
    cmd = "AT+CIPSEND=";
    cmd += String(getStr.length());
    Serial.println(cmd);
    espSerial.println(cmd);
    Serial.println(getStr);
    if (espSerial.find(">")){
      espSerial.print(getStr);
      Serial.println(getStr);
    }


    for (j = 0; j < 5; j++){  // shuts down the board for 40 s
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF); 
    }
  
}

  String espData(String command, const int timeout, boolean debug)
{
  Serial.print("AT Command ==> ");
  Serial.print(command);
  Serial.println("     ");
  
  String response = "";
  espSerial.println(command);
  long int time = millis();
  while ( (time + timeout) > millis())
  {
    while (espSerial.available())
    {
      char c = espSerial.read();
      response += c;
    }
  }
  if (debug)
  {
    Serial.print(response);
  }
  return response;
}
