#include "addr_latch.h"

// Shadow copy of the latch outputs (bit n = Qn) so you can read state back.
uint8_t AddrLatch::state = 0;

// Call once from AddrLatch::begin() in setup(). Leaves the latch in hold mode with all outputs low.
void AddrLatch::begin() {
  pinMode(PIN_A0, OUTPUT);
  pinMode(PIN_A1, OUTPUT);
  pinMode(PIN_A2, OUTPUT);
  pinMode(PIN_DATA, OUTPUT);
  pinMode(PIN_WD, OUTPUT);
  pinMode(PIN_RESET, OUTPUT);

  digitalWrite(PIN_WD, HIGH);    // hold mode first, so nothing gets written
  digitalWrite(PIN_RESET, LOW);
  AddrLatch::reset();
}

// Clear all eight outputs to LOW.
void AddrLatch::reset() {
  digitalWrite(PIN_WD, HIGH);    // WD must be HIGH during a reset
  digitalWrite(PIN_RESET, HIGH);
  delayMicroseconds(1);
  digitalWrite(PIN_RESET, LOW);
  AddrLatch::state = 0;
}

// Set output Qn (n = 0..7) HIGH or LOW. Other outputs are unchanged.
void AddrLatch::write(uint8_t n, bool value) {
  if (n > 7) return;

  digitalWrite(PIN_WD, HIGH);    // hold while changing address/data to avoid glitches
  digitalWrite(PIN_A0, n & 0x01);
  digitalWrite(PIN_A1, (n >> 1) & 0x01);
  digitalWrite(PIN_A2, (n >> 2) & 0x01);
  digitalWrite(PIN_DATA, value ? HIGH : LOW);
  delayMicroseconds(1);          // address/data setup time

  digitalWrite(PIN_WD, LOW);     // latch follows DATA
  delayMicroseconds(1);
  digitalWrite(PIN_WD, HIGH);    // latch holds the value

  if (value) AddrLatch::state |=  (1 << n);
  else       AddrLatch::state &= ~(1 << n);
}

// Write all eight outputs at once (bit n of value -> Qn).
void AddrLatch::writeAll(uint8_t value) {
  for (uint8_t n = 0; n < 8; n++) {
    AddrLatch::write(n, (value >> n) & 0x01);
  }
}

// Return the last value written to Qn (from the shadow register).
bool AddrLatch::read(uint8_t n) {
  return (n <= 7) && ((AddrLatch::state >> n) & 0x01);
}