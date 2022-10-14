#include <Arduino.h>

#ifndef RXTX_H // include guard
#define RXTX_H

void rtty_txstring (char * string);
void rtty_txbyte (char c);
void rtty_txbit (int bit);
uint16_t gps_CRC16_checksum (char *string);
void setPwmFrequency(int pin, int divisor);

#endif /* RXTX_H */