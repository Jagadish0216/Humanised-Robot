#include <AccelStepper.h>

#define STEP_PIN     2
#define DIR_PIN      5
#define ENABLE_PIN   8

AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

void setup() {
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW);  // Enable driver

  Serial.begin(9600);
  Serial.println("Commands:");
  Serial.println("l = turn left 40 steps and return");
  Serial.println("r = turn right 40 steps and return");
  Serial.println("f = full clockwise rotation (200 steps)");

  stepper.setMaxSpeed(80);       // adjust if needed
  stepper.setAcceleration(40);   // smooth ramping
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();

    if (cmd == 'l') {
      Serial.println("Turning left...");
      turnAndReturn(true, 40);
    } 
    else if (cmd == 'r') {
      Serial.println("Turning right...");
      turnAndReturn(false, 40);
    } 
    else if (cmd == 'f') {
      Serial.println("Full rotation...");
      rotateFull(200);
    }
  }

  stepper.run();
}

// Turn and return to center
void turnAndReturn(bool left, long steps) {
  if (left)
    stepper.move(steps);
  else
    stepper.move(-steps);

  while (stepper.distanceToGo() != 0)
    stepper.run();

  delay(300); // pause at end

  // Return to center
  if (left)
    stepper.move(-steps);
  else
    stepper.move(steps);

  while (stepper.distanceToGo() != 0)
    stepper.run();

  Serial.println("Returned to center!");
}

// Full rotation (one direction)
void rotateFull(long steps) {
  stepper.move(-steps);
  while (stepper.distanceToGo() != 0)
    stepper.run();
  Serial.println("Full rotation done!");
}