#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Wire.begin(21, 22); // SDA = 21, SCL = 22
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 allocation failed");
    for (;;);
  }
  display.clearDisplay();
  display.display();
  delay(500);
}

void loop() {
  // Eye open
  display.clearDisplay();
  drawEyeOpen();
  display.display();
  delay(800);

  // Eye blink (closed)
  display.clearDisplay();
  drawEyeClosed();
  display.display();
  delay(200);
}

void drawEyeOpen() {
  // Eye outline
  display.drawCircle(64, 32, 20, SSD1306_WHITE);
  display.drawCircle(64, 32, 21, SSD1306_WHITE);

  // Pupil (larger, centered)
  display.fillCircle(64, 32, 12, SSD1306_WHITE);
}

void drawEyeClosed() {
  // Eyelid line (horizontal)
  display.drawLine(44, 32, 84, 32, SSD1306_WHITE);
  display.drawLine(44, 33, 84, 33, SSD1306_WHITE);
}