#include "pressure_transducer.h"

// for www.amazon.com/dp/B0CRQWHS7H?th=1

PressureTransducer::PressureTransducer(int pin) : pin(pin) {
    pinMode(pin, INPUT);
}

float PressureTransducer::readPressure() {
    int sensorValue = analogRead(pin);
    float voltage = (sensorValue * 3.3) / 8192.0; // Convert the analog reading to voltage
    float output = ((voltage - 0.21) / (1.08 - 0.21)) * (80 - 0) + 0; // Convert voltage to pressure. 0 psi reads 0.21V, 80 psi reads 1.08V. Linear relationship between voltage and pressure.
    Serial.print("Pressure Sensor Value: ");
    Serial.print(sensorValue);
    Serial.print(", Voltage: ");
    Serial.print(voltage);
    Serial.print("V, Pressure: ");
    Serial.print(output);
    Serial.println(" psi");
    return output;
}