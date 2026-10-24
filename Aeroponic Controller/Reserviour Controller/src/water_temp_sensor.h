#ifndef WATER_TEMP_SENSOR_H
#define WATER_TEMP_SENSOR_H
#include <Arduino.h>

class WaterTempSensor {
public:
    WaterTempSensor(int pin);
    float readTemperature();
private:
    int pin;
};

#endif