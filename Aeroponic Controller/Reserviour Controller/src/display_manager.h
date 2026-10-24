#include <Arduino.h>

static unsigned int line_spacing = 20;
static const unsigned int max_display_items = 10;

#define BLACK 0x0000
#define WHITE 0xFFFF
#define RED 0xF800
#define GREEN 0x07E0
#define BLUE 0x001F
#define CYAN 0x07FF
#define MAGENTA 0xF81F
#define YELLOW 0xFFE0
#define ORANGE 0xFC00

// External SPI TFT configuration.
// Update these values to match your display wiring.
#define DISP_WIDTH 320
#define DISP_HEIGHT 240
#define DISP_ROTATION 3
#define DISP_SCK 21
#define DISP_MOSI 19
#define DISP_MISO -1
#define DISP_CS 18
#define DISP_DC 6
#define DISP_RST 7
// Set to -1 if your display backlight is always-on or not MCU controlled.
#define DISP_BL -1

void setupDisplay();
void manageDisplay();
void addText(char *tag, char *text, uint16_t color);
void clearText(char *tag);