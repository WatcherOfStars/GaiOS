#include <Arduino.h>
#ifndef ADDR_LATCH_H
#define ADDR_LATCH_H

class AddrLatch {
public:
    static void begin();
    static void reset();
    static void write(uint8_t n, bool value);
    static void writeAll(uint8_t value);
    static bool read(uint8_t n);
    static uint8_t state;
    static const uint8_t PIN_A0    = 1;
    static const uint8_t PIN_A1    = 2;
    static const uint8_t PIN_A2    = 3;
    static const uint8_t PIN_DATA  = 0;
    static const uint8_t PIN_WD    = 23;
    static const uint8_t PIN_RESET = 22;
};

#endif // ADDR_LATCH_H

