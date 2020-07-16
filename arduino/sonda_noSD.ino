// CODI SONDA.
// Aquest és el codi que portarà la sonda durant el vol.
// Mesurarà la temperatura interior, l'exterior, humitat, pressió,
// posició, altitud i hora.
// Després, "empaquetarà" aquestes dades en una cadena
// que es desarà en una targeta SD i s'enviarà per ràdio.
// La cadena està estructurada de la següent manera:
// Temperatura exterior; temperatura interior; humitat, temperatura BMP, pressió, altitud BMP, latitud, longitud, altitud, hora, checksum.
// 
// [X]TEMPERATURA EXTERIOR (DS18B20)
// [X]TEMPERATURA INTERIOR (DHT22)
// [X]HUMITAT              (DHT22)
// [X]PRESSIÓ              (BMP180) (+ temperatura, + altitud)
// [X]LOCALITZACIÓ GPS     (u-blox MAX-M8C)
//      [X]COORDENADES
//      [X]ALTITUD
//      [X]DATA I HORA
// [X]EMMAGATZEMATGE SD    (Catalex MicroSD Card Adapter)
// [X]TRANSMISSIÓ RÀDIO    (Radiometrix NTX2B-FA)
// 
// PROBLEMES CONEGUTS:
// -No hi ha mesures on la part decimal sigui 1, 3, 6 o 8 (aproximen a l'alça)
// -El localitzador GPS arribarà fins una altitud de 18 km.
// 
// Començat el 23-8-2015.
// Acabat el 23-9-2015.
// Fonts: Parts del codi estan extretes directament de:
// Exemple "DS18x20_Temperature" de la llibreria OneWire. (mesura de temperatura exterior)
// Exemple "KitchenSink" de la llibreria TinyGPS++ (localització GPS)
// -https://ukhas.org.uk/guides:linkingarduinotontx2 (transmissió via ràdio)

// Aquest codi s'ha provat sobre una placa Arduino Uno.
// Aquesta placa té una memòria insuficient per al codi; la funció d'emmagatzematge SD quedarà desactivada.
// La intenció és utilitzar una placa Arduino Mega pel vol, que té més memòria
// i podrà fer servir totes les característiques del codi.
// El codi per a l'Arduino Mega és idèntic, tret de la distribució d'alguns pins.

//LLIBRERIES:

#include <OneWire.h> //llibreria del sensor DS18B20.
#include "DHT.h" //llibreria del sensor DHT
#include <SFE_BMP180.h> //incloure la llibreria del sensor BMP180
#include <Wire.h> //incloure la llibreria I2C, ja que el sensor BMP180 es comunica per I2C
//#include <TinyGPS++.h> //llibreria per a interpretar dades del GPS
//#include <SoftwareSerial.h> //llibreria per a comunicació entre el GPS i l'Arduino
//#include <util/crc16.h> //llibreria per calcular verificacions
#include <SD.h> //llibreria per utilitzar targeta SD
#include <SPI.h> //llibreria per comunicar-se amb la targeta SD

//SENSORS:

//DS18B20:

OneWire ds(8); //el sensor DS es troba al pin digital 8

//DHT22:

#define DHTPIN 2 //el sensor DHT es troba al pin digital 2
#define DHTTYPE DHT22 //el sensor DHT és el DHT22

DHT dht(DHTPIN, DHTTYPE); //objecte "dht" per referir-nos al sensor DHT: és un DHT22 i es troba al pin digital 2

//BMP180:

SFE_BMP180 pressio; //objecte "pressio" per referir-nos al sensor BMP180
#define ALTITUD 330.0 //altitud des de la qual es comença a mesurar la pressió

//localitzador GPS:

/*TinyGPSPlus gps; //objecte "gps" per referir-nos al localitzador GPS

//el GPS es comunica amb la placa Arduino
//per un port sèrie mitjançant programari (en aquest cas, pins 4 i 3).
SoftwareSerial ss(4, 3); //objecte "ss" per referir-nos al port sèrie per programari

*///targeta SD:

#define TARGETA 10 //pin de targeta SD (pin CS del mòdul) al pin digital 10 de l'Arduino
File SondaSD; //objecte "SondaSD" per referir-nos a l'arxiu de la targeta SD on desarem dades

/*//Radiometrix NTX2B-FA:

#define RADIOPIN 9 //pin de transmissió (pin 7 del transmissor) al pin digital 9 de l'Arduino*/

//VARIABLES:

//float=nombre decimal ; int=nombre enter (2 bytes) ; long=nombre enter (4 bytes) ; char = cadena

//variables dels sensors

float tDS = 0; //temperatura exterior (graus Celsius)

float tDHT = 0; //temperatura interior del sensor DHT (graus Celsius)
int hDHT = 0; //humitat (%)

int tBMP; //temperatura interior del sensor BMP (graus Celsius)
int pBMP; //pressió (mbar)
int p0; //pressió (relativa, a nivell de mar)
int altBMP; //altitud (calculada pel sensor BMP)

//variables GPS

/*long latE = 0; //latitud (graus, part entera)
long latD = 0; //latitud (graus, part decimal)

long lngE = 0; //longitud (graus, part entera)
long lngD = 0; //longitud (graus, part decimal)

int alt = 0; //altitud

int hora = 0; //hores (en temps UTC!)
int min = 0; //minuts
int seg = 0; //segons*/

//CADENES:

//com que no es pot afegir directament el signe positiu o negatiu a les coordenades,
//es desaran en cadenes separades i després s'afegiran a la cadena final.

//char GPS1[20];
//char GPS2[30];
char SONDA [90]; //cadena final

void setup() { 
  
  //AQUESTA PART SERVEIX PER PREPARAR TOT EL QUE FARÀ L'ORDINADOR DE VOL.
  //NOMÉS S'EXECUTARÀ UN COP, A L'INICI.

  //OBRIR COMUNICACIÓ AMB PORT SÈRIE
  //la comunicació amb el port sèrie és només per preparar-se abans del vol.

  Serial.begin(38400); //obrir comunicació amb port sèrie
  Serial.println(F("TEST SONDA"));

//OBRIR COMUNICACIÓ AMB TARGETA SD

  //preparar comunicació amb targeta SD

  Serial.println(F("Preparant SD"));
  pinMode(TARGETA,OUTPUT);

  //començar comunicació amb targeta SD.
  //si no es pot comunicar en aquest moment, no es podran desar dades durant el vol.

  if(!SD.begin(10)){
    Serial.println(F("ERROR SD")); 
  }
  else{
  Serial.println(F("SD OK"));
  }

  //PREPARAR COMUNICACIÓ VIA RÀDIO

/*  pinMode(RADIOPIN,OUTPUT);
  setPwmFrequency(RADIOPIN, 1);*/

  //INICIAR SENSOR DHT22

  dht.begin();

  //INICIAR SENSOR BMP180
  
  if (pressio.begin()) { //si el sensor s'inicia,
    Serial.println(F("BMP OK"));
  }
  else{ //si no s'inicia,
    Serial.println(F("BMP ERROR"));
  }

}

void loop() { 
  
  //AQUESTA PART ES REPETIRÀ CÍCLICAMENT, DURANT TOTA L'ESTONA. 
  //TOTES LES ACCIONS QUE FARÀ L'ORDINADOR DE VOL S'INCLOUEN AQUÍ.

  //DS18B20

  //OBTENIR TEMPERATURA EXTERIOR.
  //Extret de l'exemple "DS18x20_Temperature" de la llibreria OneWire.
  //No és elaboració pròpia; s'ha deixat intacte.

  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];
  byte addr[8];
  
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
  tDS = (float)raw / 16.0;

  //convertir valor decimal en dos enters (E=part entera; 2=valor menys part entera; D=part decimal)
  //s'aproxima a un decimal per truncament.
  //el valor tDS es dividirà en tDSE (part entera) i tDSD (part decimal)

  int tDSE = tDS;
  float tDS2 = tDS - tDSE;
  int tDSD = trunc(tDS2*10);

  //DHT
  
  //OBTENIR TEMPERATURA INTERIOR.

  tDHT = dht.readTemperature(); //llegir temperatura interior

  //convertir valor decimal en dos enters (E=part entera; 2=valor menys part entera; D=part decimal)
  //s'aproxima a un decimal per truncament.
  //el valor tInt es dividirà en tIntE (part entera) i tIntD (part decimal)

  int tDHTE = tDHT;
  float tDHT2 = tDHT - tDHTE;
  int tDHTD = trunc(tDHT2*10);

  //OBTENIR HUMITAT.
     
  hDHT = dht.readHumidity(); //llegir el valor de la humitat i anomenar-lo "h"

  //convertir valor decimal en dos enters (E=part entera; 2=valor menys part entera; D=part decimal)
  //s'aproxima a un decimal per truncament.
  //el valor h es dividirà en hE (part entera) i hD (part decimal)
  
  int hDHTE = hDHT;
  float hDHT2 = hDHT - hDHTE;
  int hDHTD = trunc(hDHT2*10);

  //BMP180
  //aquesta part està copiada del codi
  //de l'apartat 2 de l'annex 1 (prova 2. sensor de pressió bmp180)

  char status; //introduir variable estat (retornarà 1 si no hi ha problemes, 0 si n'hi ha)
  double T,P;
  
  //T: introduir variable T (temperatura en ºC)
  //P: introduir variable P (pressió absoluta en mbar)

  //mesurar temperatura.
   
  status = pressio.startTemperature();
  if (status != 0) //si es pot mesurar la temperatura...
  {
    // esperar fins acabar de mesurar la temperatura
    delay(status);

    // rebre mesura de temperatura
    // i desar-la a la variable T

    status = pressio.getTemperature(T);
    if (status != 0) //si es pot rebre la mesura...
    {
      // mesurar pressió.
      // el "3" indica la resolució.
      // pot ser entre 0 i 3. 0 és la més baixa, 3 la més alta, però trigarà més.

      status = pressio.startPressure(3);
      if (status != 0) //si es pot mesurar la pressió...
      {
        // esperar fins acabar de mesurar la pressió.
        delay(status);

        // rebre mesura de pressió
        // i desar-la a la variable P.
        // aquesta pressió està calibrada amb la temperatura,
        // per tant cal tenir una mesura prèvia de temperatura.

        status = pressio.getPressure(P,T);
        if (status != 0) //si es pot rebre la mesura...
        {

          //obtenir pressió relativa a nivell de mar,
          //a partir de la pressió i l'altitud inicial
          
          p0 = pressio.sealevel(P,ALTITUD);

          //obtenir altitud a partir de la diferència de pressions.
          //no és totalment fiable, perquè la temperatura no és constant.
          
          altBMP = pressio.altitude(P,p0);
        }
      }
    }
  }

  //convertir les mesures de temperatura i pressió en nombres enters.
  //la mesura de temperatura és complementària a la del DHT.
  //no és necessari que la mesura de pressió tingui una precisió d'un decimal, amb un enter ja n'hi ha prou.

  tBMP = T;
  pBMP = P;

/*  //GPS

  //iniciar la comunicació amb el GPS (pel port sèrie "secundari")
  
  ss.begin(9600);

  //donar tres segons al GPS perquè llegeixi les mesures que rep
  //si no es fa aquest pas, la majoria de mesures del GPS no es llegiran.
  
    unsigned long start = millis();
  do 
  {
    while (ss.available())
      gps.encode(ss.read());
  } while (millis() - start < 3000);

  //latitud
  
  latE = gps.location.rawLat().deg;
  latD = gps.location.rawLat().billionths;

  //longitud

  lngE = gps.location.rawLng().deg;
  lngD = gps.location.rawLng().billionths;

  //altitud
  
  alt = gps.altitude.meters();

  //hora (UTC)
  
  hora= gps.time.hour();
  min = gps.time.minute();
  seg = gps.time.second();

  //finalitzar comunicació amb el GPS.
  //MOLT IMPORTANT NO SALTAR-SE AQUEST PAS,
  //O LA RÀDIO NO PODRÀ TRANSMETRE BÉ!

  ss.end();*/

  //ESTRUCTURAR CADENES

  //afegir mesures de sensors a la cadena SONDA

  sprintf(SONDA, "%d,%d;%d,%d;%d,%d;%d;%d;%d;", tDSE, tDSD, tDHTE, tDHTD, hDHTE, hDHTD, tBMP, pBMP, altBMP);

  //afegir mesura de latitud a la cadena GPS1.
  //una mesura de latitud negativa (sud) no mostrarà per defecte el signe.
  //per tant, cal afegir-lo manualment.

/*  if (gps.location.lat() < 0)
  {
    sprintf(GPS1, "-%ld.%ld;", latE, latD);
  }
  else
  {
    sprintf(GPS1, "%ld.%ld;", latE, latD);
  }

  //afegir mesura de longitud, altitud i hora a la cadena GPS2.
  //una mesura de longitud negativa (oest) no mostrarà per defecte el signe.
  //per tant, cal afegir-lo manualment.

  if (gps.location.lng() < 0)
  {
    sprintf(GPS2, "-%ld.%ld;%d;%02d:%02d:%02d", lngE, lngD, alt, hora, min, seg);
  }
  else
  {
    sprintf(GPS2, "%ld.%ld;%d;%02d:%02d:%02d", lngE, lngD, alt, hora, min, seg);
  }

  //afegir cadenes GPS1 i GPS2 a la cadena SONDA
  
  strcat(SONDA, GPS1);
  strcat(SONDA, GPS2);*/

  //DESAR CADENA SONDA A LA TARGETA SD

  SondaSD = SD.open("prova2.txt", FILE_WRITE);
  delay(500);

  if (SondaSD){
    SondaSD.println(SONDA);
    SondaSD.close();
  }
  else{
    Serial.println("error obrint sonda.txt");
  }



/*  //AFEGIR CHECKSUM ("SUMA DE VERIFICACIÓ") A LA CADENA SONDA
  
  unsigned int CHECKSUM = gps_CRC16_checksum(SONDA); //funció per calcular suma de verificació o checksum per la cadena SONDA (definida més endavant)
  char VERIFICACIO[6]; //definir VERIFICACIO com a cadena
  sprintf(VERIFICACIO, "*%04X\n", CHECKSUM); //estructurar cadena VERIFICACIO
  strcat(SONDA, VERIFICACIO); //concatenar cadenes SONDA i VERIFICACIO (la segona cadena s'inclou al final de la primera)

  //MOSTRAR CADENA SONDA PER PORT SÈRIE

  Serial.println(SONDA);

  //ENVIAR CADENA SONDA PER RÀDIO
  
  rtty_txstring (SONDA); //funció per transmetre la cadena final de sonda per ràdio (definida més endavant)

  //FI DE LA FUNCIÓ "LOOP". TORNAR A COMENÇAR.*/

}

// FUNCIÓ DE TRANSMISSIÓ DE LA CADENA PER RÀDIO.
// Aquest codi ha estat agafat directament del codi trobat
// al tutorial "Linking an Arduino to a Radiometrix NTX2B Transmitter",
// disponible a https://ukhas.org.uk/guides:linkingarduinotontx2.
// No és elaboració pròpia; s'ha deixat intacte.

/*void rtty_txstring (char * string) {
     Simple function to sent a char at a time to    ** rtty_txbyte function.    ** NB Each char is one byte (8 Bits)    
 
    char c;
    c = *string++;
 
    while ( c != '\0') {
        rtty_txbyte (c);
        c = *string++;
    }
}
void rtty_txbyte (char c) {
     Simple function to sent each bit of a char to    ** rtty_txbit function.    ** NB The bits are sent Least Significant Bit first    **    ** All chars should be preceded with a 0 and    ** proceed with a 1. 0 = Start bit; 1 = Stop bit    **    
 
    int i;
 
    rtty_txbit (0); // Start bit
 
    // Send bits for for char LSB first
 
    for (i=0;i<7;i++) { // Change this here 7 or 8 for ASCII-7 / ASCII-8
        if (c & 1) rtty_txbit(1);
        else rtty_txbit(0);
 
        c = c >> 1;
    }
    rtty_txbit (1); // Stop bit
    rtty_txbit (1); // Stop bit
}
 
void rtty_txbit (int bit) {
    if (bit) {
        // high
        analogWrite(RADIOPIN,110);
    }
    else {
        // low
        analogWrite(RADIOPIN,100);
    }
 
    // delayMicroseconds(3370); // 300 baud
    delayMicroseconds(10000); // For 50 Baud uncomment this and the line below.
    delayMicroseconds(10150); // You can't do 20150 it just doesn't work as the
    // largest value that will produce an accurate delay is 16383
    // See : http://arduino.cc/en/Reference/DelayMicroseconds
}
 
uint16_t gps_CRC16_checksum (char *string) {
    size_t i;
    uint16_t crc;
    uint8_t c;
 
    crc = 0xFFFF;
 
    // Calculate checksum ignoring the first two $s
    for (i = 2; i < strlen(string); i++) {
        c = string[i];
        crc = _crc_xmodem_update (crc, c);
    }
 
    return crc;
}
 
void setPwmFrequency(int pin, int divisor) {
    byte mode;
    if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
        switch(divisor) {
            case 1:
                mode = 0x01;
                break;
            case 8:
                mode = 0x02;
                break;
            case 64:
                mode = 0x03;
                break;
            case 256:
                mode = 0x04;
                break;
            case 1024:
                mode = 0x05;
                break;
            default:
                return;
        }
 
        if(pin == 5 || pin == 6) {
            TCCR0B = TCCR0B & 0b11111000 | mode;
        }
        else {
            TCCR1B = TCCR1B & 0b11111000 | mode;
        }
    }
    else if(pin == 3 || pin == 11) {
        switch(divisor) {
            case 1:
                mode = 0x01;
                break;
            case 8:
                mode = 0x02;
                break;
            case 32:
                mode = 0x03;
                break;
            case 64:
                mode = 0x04;
                break;
            case 128:
                mode = 0x05;
                break;
            case 256:
                mode = 0x06;
                break;
            case 1024:
                mode = 0x7;
                break;
            default:
                return;
        }
        TCCR2B = TCCR2B & 0b11111000 | mode;
    }
}
*/
