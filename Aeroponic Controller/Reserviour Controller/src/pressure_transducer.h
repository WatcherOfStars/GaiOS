#ifndef PRESSURE_TRANSDUCER_H
#define PRESSURE_TRANSDUCER_H

#include "Arduino.h"

class PressureTransducer {
public:
    PressureTransducer(int pin);
    float readPressure();
private:
    int pin;
};

#endif