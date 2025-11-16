#define RPWM_A 5
#define LPWM_A 6
#define R_EN_A 7
#define L_EN_A 8

// ============ Motor B Pins (Right Side Motors) ============
#define RPWM_B 44
#define LPWM_B 45
#define R_EN_B 46
#define L_EN_B 47

void setup() {
  Serial.begin(9600);

  pinMode(RPWM_A, OUTPUT);
  pinMode(LPWM_A, OUTPUT);
  pinMode(R_EN_A, OUTPUT);
  pinMode(L_EN_A, OUTPUT);

  pinMode(RPWM_B, OUTPUT);
  pinMode(LPWM_B, OUTPUT);
  pinMode(R_EN_B, OUTPUT);
  pinMode(L_EN_B, OUTPUT);

  // Enable both sides
  digitalWrite(R_EN_A, HIGH);
  digitalWrite(L_EN_A, HIGH);
  digitalWrite(R_EN_B, HIGH);
  digitalWrite(L_EN_B, HIGH);

  Serial.println("Motor control ready. Enter commands: F, B, L, R, S");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();   // Read one character command
    int speed = 200;            // Default speed (safe value)

    // For debugging
    Serial.print("Command received: ");
    Serial.println(cmd);

    // Movement handling
    if (cmd == 'F' || cmd == 'f') moveForward(speed);
    else if (cmd == 'B' || cmd == 'b') moveBackward(speed);
    else if (cmd == 'L' || cmd == 'l') turnLeft(speed);
    else if (cmd == 'R' || cmd == 'r') turnRight(speed);
    else if (cmd == 'S' || cmd == 's') stopMotors();
  }
}

// ======== Movement Functions =========
void moveForward(int speed) {
  analogWrite(RPWM_A, speed); analogWrite(LPWM_A, 0);
  analogWrite(RPWM_B, speed); analogWrite(LPWM_B, 0);
  Serial.println("Moving Forward");
}

void moveBackward(int speed) {
  analogWrite(RPWM_A, 0); analogWrite(LPWM_A, speed);
  analogWrite(RPWM_B, 0); analogWrite(LPWM_B, speed);
  Serial.println("Moving Backward");
}

void turnLeft(int speed) {
  analogWrite(RPWM_A, 0); analogWrite(LPWM_A, speed);  // Left side backward
  analogWrite(RPWM_B, speed); analogWrite(LPWM_B, 0);  // Right side forward
  Serial.println("Turning Left");
}

void turnRight(int speed) {
  analogWrite(RPWM_A, speed); analogWrite(LPWM_A, 0);  // Left side forward
  analogWrite(RPWM_B, 0); analogWrite(LPWM_B, speed);  // Right side backward
  Serial.println("Turning Right");
}

void stopMotors() {
  analogWrite(RPWM_A, 0); analogWrite(LPWM_A, 0);
  analogWrite(RPWM_B, 0); analogWrite(LPWM_B, 0);
  Serial.println("Stopped");
}