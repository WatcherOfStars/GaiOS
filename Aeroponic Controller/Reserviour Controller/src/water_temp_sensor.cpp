#include <OneWireNg_CurrentPlatform.h>
#include <drivers/DSTherm.h>
#include <utils/Placeholder.h>
#include <water_temp_sensor.h>

//using the Dallas DS18S20 temperature chip, which uses the OneWire protocol

// Temperature driver objects are initialized once from the configured pin.
static OneWireNg_CurrentPlatform *ow = nullptr;
static DSTherm *dsth = nullptr;
static PlaceholderInit<DSTherm::Scratchpad> scrpd;

WaterTempSensor::WaterTempSensor(int pin){
  if (dsth != nullptr) {
    delete dsth;
    dsth = nullptr;
  }
  if (ow != nullptr) {
    delete ow;
    ow = nullptr;
  }

  // Use standard power mode (non-parasitic) unless your wiring requires it.
  ow = new OneWireNg_CurrentPlatform(pin, false);
  dsth = new DSTherm(*ow);
}

float WaterTempSensor::readTemperature(){
  // returns the temperature from one DS18x20 in DEG Celsius
  if (ow == nullptr || dsth == nullptr) {
    Serial.println("Error: OneWire or DSTherm not initialized.");
    return -1000;
  }

  OneWireNg::ErrorCode ec = dsth->convertTempAll(DSTherm::MAX_CONV_TIME, false);
  if (ec != OneWireNg::EC_SUCCESS) {
    Serial.print("Error: Failed to convert temperature.");
    Serial.print(" Error code: ");
    Serial.println(ec);
    return -1000;
  }

  ec = dsth->readScratchpadSingle(&scrpd);
  if (ec != OneWireNg::EC_SUCCESS) {
    Serial.print("Error: Failed to read scratchpad.");
    Serial.print(" Error code: ");
    Serial.println(ec);
    return -1000;
  }

  long temp16 = scrpd->getTemp2();
  return (float)temp16 / 16.0f;

}
