#include <Servo.h>

// RIGHT ARM servos
Servo rightElbowServo;
Servo rightHandServo;

// LEFT ARM servos
Servo leftElbowServo;
Servo leftHandServo;

// RIGHT ARM pins
const int RIGHT_ELBOW_PIN = 9;
co  nst int RIGHT_HAND_PIN = 10;

// LEFT ARM pins
const int LEFT_ELBOW_PIN = 11;
const int LEFT_HAND_PIN = 12;

// Arm positions
const int ELBOW_NEUTRAL = 90;
const int ELBOW_FORWARD = 60;   // Arm swings forward
const int ELBOW_BACKWARD = 120; // Arm swings back
const int HAND_NEUTRAL = 90;

// State tracking for continuous movement
bool isWalking = false;
char currentMovement = 'S';  // S = stopped, F = forward, B = backward, L = left, R = right

void setup() {
  Serial.begin(9600);
  
  // Attach RIGHT ARM servos
  rightElbowServo.attach(RIGHT_ELBOW_PIN);
  rightHandServo.attach(RIGHT_HAND_PIN);
  
  // Attach LEFT ARM servos
  leftElbowServo.attach(LEFT_ELBOW_PIN);
  leftHandServo.attach(LEFT_HAND_PIN);

  // Initial neutral position for BOTH arms
  rightElbowServo.write(ELBOW_NEUTRAL);
  rightHandServo.write(HAND_NEUTRAL);
  leftElbowServo.write(ELBOW_NEUTRAL);
  leftHandServo.write(HAND_NEUTRAL);

  Serial.println("Arduino Uno - Dual Arm Controller Ready");
  Serial.println("Right Arm: Pins 9, 10");
  Serial.println("Left Arm: Pins 11, 12");
}

void loop() {
  // Check for serial commands
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "WAVE") {
      Serial.println("Command: WAVE - Right hand only");
      isWalking = false;  // Stop walking to wave
      waveGesture();
    } 
    else if (cmd == "F") {
      Serial.println("Command: FORWARD - Continuous walking arms");
      currentMovement = 'F';
      isWalking = true;
    }
    else if (cmd == "B") {
      Serial.println("Command: BACKWARD - Continuous walking arms");
      currentMovement = 'B';
      isWalking = true;
    }
    else if (cmd == "L") {
      Serial.println("Command: LEFT - Continuous turning arms");
      currentMovement = 'L';
      isWalking = true;
    }
    else if (cmd == "R") {
      Serial.println("Command: RIGHT - Continuous turning arms");
      currentMovement = 'R';
      isWalking = true;
    }
    else if (cmd == "S") {
      Serial.println("Command: STOP - Arms to neutral");
      isWalking = false;
      currentMovement = 'S';
      bothArmsNeutral();
    }
    else {
      Serial.println("Unknown command: " + cmd);
    }
  }

  // Execute continuous walking motion based on current state
  if (isWalking) {
    switch (currentMovement) {
      case 'F':
        walkingCycleForward();
        break;
      case 'B':
        walkingCycleBackward();
        break;
      case 'L':
        walkingCycleLeft();
        break;
      case 'R':
        walkingCycleRight();
        break;
    }
  }
}

// ==========================================
// WAVE GESTURE (RIGHT HAND ONLY) - Your specific code
// ==========================================
void waveGesture() {
  Serial.println("Lifting elbow...");

  // Step 1: Lift elbow gradually (90° → 0°)
  for (int pos = 90; pos >= 0; pos -= 2) {
    rightElbowServo.write(pos);
    delay(15);
  }

  Serial.println("Waving hand...");
  // Step 2: Wave hand 3 times (60° ↔ 120°)
  for (int i = 0; i < 3; i++) {
    for (int pos = 90; pos <= 120; pos += 3) {
      rightHandServo.write(pos);
      delay(15);
    }
    for (int pos = 120; pos >= 60; pos -= 3) {
      rightHandServo.write(pos);
      delay(15);
    }
  }

  // Return hand to neutral
  rightHandServo.write(90);

  Serial.println("Lowering elbow...");
  // Step 3: Return elbow to 90° gradually
  for (int pos = 0; pos <= 90; pos += 2) {
    rightElbowServo.write(pos);
    delay(15);
  }

  Serial.println("Wave gesture complete!");
}

// ==========================================
// CONTINUOUS WALKING MOTIONS (Until stopped)
// ==========================================

void walkingCycleForward() {
  // One walking cycle: alternating arms
  // Right forward, Left backward
  for (int pos = 0; pos <= 30; pos++) {
    int rightPos = ELBOW_NEUTRAL - pos;  // Right swings forward (90->60)
    int leftPos = ELBOW_NEUTRAL + pos;   // Left swings backward (90->120)
    
    rightElbowServo.write(rightPos);
    leftElbowServo.write(leftPos);
    delay(15);
    
    // Check for stop command during motion
    if (!isWalking) return;
  }
  
  // Right backward, Left forward
  for (int pos = 0; pos <= 30; pos++) {
    int rightPos = 60 + pos;  // Right swings backward (60->90)
    int leftPos = 120 - pos;  // Left swings forward (120->90)
    
    rightElbowServo.write(rightPos);
    leftElbowServo.write(leftPos);
    delay(15);
    
    if (!isWalking) return;
  }
}

void walkingCycleBackward() {
  // Reverse of forward
  // Right backward, Left forward
  for (int pos = 0; pos <= 30; pos++) {
    int rightPos = ELBOW_NEUTRAL + pos;  // Right swings backward
    int leftPos = ELBOW_NEUTRAL - pos;   // Left swings forward
    
    rightElbowServo.write(rightPos);
    leftElbowServo.write(leftPos);
    delay(15);
    
    if (!isWalking) return;
  }
  
  // Right forward, Left backward
  for (int pos = 0; pos <= 30; pos++) {
    int rightPos = 120 - pos;  // Right swings forward
    int leftPos = 60 + pos;    // Left swings backward
    
    rightElbowServo.write(rightPos);
    leftElbowServo.write(leftPos);
    delay(15);
    
    if (!isWalking) return;
  }
}

void walkingCycleLeft() {
  // Turning left: emphasize LEFT arm movement
  // Left arm swings forward strongly
  for (int pos = ELBOW_NEUTRAL; pos >= ELBOW_FORWARD; pos -= 3) {
    leftElbowServo.write(pos);
    delay(15);
    if (!isWalking) return;
  }
  
  // Right arm slight backward
  for (int pos = ELBOW_NEUTRAL; pos <= 110; pos += 2) {
    rightElbowServo.write(pos);
    delay(15);
    if (!isWalking) return;
  }
  
  delay(200);
  
  // Return to neutral
  for (int pos = ELBOW_FORWARD; pos <= ELBOW_NEUTRAL; pos += 3) {
    leftElbowServo.write(pos);
    delay(15);
    if (!isWalking) return;
  }
  
  for (int pos = 110; pos >= ELBOW_NEUTRAL; pos -= 2) {
    rightElbowServo.write(pos);
    delay(15);
    if (!isWalking) return;
  }
}

void walkingCycleRight() {
  // Turning right: emphasize RIGHT arm movement
  // Right arm swings forward strongly
  for (int pos = ELBOW_NEUTRAL; pos >= ELBOW_FORWARD; pos -= 3) {
    rightElbowServo.write(pos);
    delay(15);
    if (!isWalking) return;
  }
  
  // Left arm slight backward
  for (int pos = ELBOW_NEUTRAL; pos <= 110; pos += 2) {
    leftElbowServo.write(pos);
    delay(15);
    if (!isWalking) return;
  }
  
  delay(200);
  
  // Return to neutral
  for (int pos = ELBOW_FORWARD; pos <= ELBOW_NEUTRAL; pos += 3) {
    rightElbowServo.write(pos);
    delay(15);
    if (!isWalking) return;
  }
  
  for (int pos = 110; pos >= ELBOW_NEUTRAL; pos -= 2) {
    leftElbowServo.write(pos);
    delay(15);
    if (!isWalking) return;
  }
}

void bothArmsNeutral() {
  // Smoothly return BOTH arms to neutral
  int rightElbowPos = rightElbowServo.read();
  int leftElbowPos = leftElbowServo.read();
  
  // Calculate steps needed
  int rightSteps = abs(rightElbowPos - ELBOW_NEUTRAL);
  int leftSteps = abs(leftElbowPos - ELBOW_NEUTRAL);
  int maxSteps = max(rightSteps, leftSteps);
  
  // Move both arms simultaneously to neutral
  for (int i = 0; i <= maxSteps; i++) {
    // Right elbow
    if (rightElbowPos < ELBOW_NEUTRAL && rightElbowPos + i <= ELBOW_NEUTRAL) {
      rightElbowServo.write(rightElbowPos + i);
    } else if (rightElbowPos > ELBOW_NEUTRAL && rightElbowPos - i >= ELBOW_NEUTRAL) {
      rightElbowServo.write(rightElbowPos - i);
    }
    
    // Left elbow
    if (leftElbowPos < ELBOW_NEUTRAL && leftElbowPos + i <= ELBOW_NEUTRAL) {
      leftElbowServo.write(leftElbowPos + i);
    } else if (leftElbowPos > ELBOW_NEUTRAL && leftElbowPos - i >= ELBOW_NEUTRAL) {
      leftElbowServo.write(leftElbowPos - i);
    }
    
    delay(10);
  }
  
  // Ensure exact neutral position
  rightElbowServo.write(ELBOW_NEUTRAL);
  leftElbowServo.write(ELBOW_NEUTRAL);
  rightHandServo.write(HAND_NEUTRAL);
  leftHandServo.write(HAND_NEUTRAL);
}
