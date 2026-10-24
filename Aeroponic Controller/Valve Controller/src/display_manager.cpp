#include <string.h>
#include <display_manager.h>
#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7789.h> // Hardware-specific library for ST7789
#include <Arduino.h>
#include <SPI.h>

//DISPLAY
Adafruit_ST7789 tft = Adafruit_ST7789(&SPI, DISP_CS, DISP_DC, DISP_RST); // Use dedicated hardware SPI pins

//struct for a display item on the screen
typedef struct display_item{
  char* tag;
  char* text;
  uint16_t color;
} DisplayItem;

DisplayItem display_arr[max_display_items];

//to be called on setup
void setupDisplay(){
    pinMode(DISP_CS, OUTPUT);
    pinMode(DISP_DC, OUTPUT);
    if (DISP_RST >= 0) {
      pinMode(DISP_RST, OUTPUT);
    }

    if (DISP_BL >= 0) {
      pinMode(DISP_BL, OUTPUT);
      digitalWrite(DISP_BL, HIGH);
    }

    // External display path: explicitly map hardware SPI pins.
    SPI.begin(DISP_SCK, DISP_MISO, DISP_MOSI, DISP_CS);

    // initialize TFT
    tft.init(DISP_HEIGHT, DISP_WIDTH);
    tft.setRotation(DISP_ROTATION);
    tft.fillScreen(BLACK);
    tft.cp437(true);
    tft.setTextSize(2);
}

//to be called whenever display needs updated
void manageDisplay(){
  tft.fillScreen(BLACK); //clear screen

  for (int i=0; i<max_display_items; i++){
    if(display_arr[i].tag != NULL){ //if exists, display this entry
      tft.setCursor(0, i*line_spacing);
      tft.setTextColor(display_arr[i].color);
      //char *chars = display_arr[i].text;
      tft.print(String(display_arr[i].tag) + " " + String(display_arr[i].text));
      continue;
    }
  } 
}

//add a message to the screen
void addText(char *tag, char *text, uint16_t color) {
  //check if this tag already exists, if so, update it
  for (int i=0; i<max_display_items; i++){
    if(display_arr[i].tag == NULL || display_arr[i].tag == tag){ //if exists or is empty, update this entry
      DisplayItem new_item = {tag, text, color};  //create new struct
      display_arr[i] = new_item; //update value
      Serial.print(tag);
      Serial.print(" ");
      Serial.println(text);
      return;
    }
  }
}

//clear a topic from the message array
void clearText(char *tag){
  for (int i=0; i<max_display_items; i++){
    if(display_arr[i].tag == tag){ //if exists or is empty, delete this entry
      display_arr[i] = {NULL,NULL,BLACK}; //set to empty
      return;
    }
  }
}