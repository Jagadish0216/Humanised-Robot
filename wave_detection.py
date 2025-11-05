import cv2
import mediapipe as mp
from picamera2 import Picamera2
import pyttsx3
import math
import serial
import threading
import time
import os

# ===================================
# ARDUINO UNO CONNECTION
# ===================================
try:
    arduino_uno = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)
    print(f"? Arduino Uno connected on /dev/ttyUSB0")
except Exception as e:
    print(f"? Arduino Uno connection failed: {e}")
    exit(1)

# ===================================
# NAMED PIPE SETUP
# ===================================
PIPE_PATH = '/tmp/arm_commands'

# Auto-create pipe if it doesn't exist
if not os.path.exists(PIPE_PATH):
    os.mkfifo(PIPE_PATH)
    print(f"? Created named pipe: {PIPE_PATH}")
else:
    print(f"? Named pipe ready: {PIPE_PATH}")

def send_to_uno(command):
    """Send command to Arduino Uno"""
    if arduino_uno:
        try:
            arduino_uno.write(f"{command}\n".encode())
            time.sleep(0.05)
            if arduino_uno.in_waiting > 0:
                response = arduino_uno.readline().decode().strip()
                print(f"  ?? Uno: {response}")
        except Exception as e:
            print(f"Error sending to Uno: {e}")
            
def listen_to_pipe():
    """Thread to listen for movement commands from max.py via named pipe"""
    print("?? Listening for arm commands from max.py...")
    
    while True:
        try:
            # Open pipe for reading (blocking until max.py writes)
            with open(PIPE_PATH, 'r') as pipe:
                for line in pipe:
                    command = line.strip()
                    if command:
                        print(f"?? Received from max.py: {command}")
                        send_to_uno(command)
        except Exception as e:
            print(f"Pipe error: {e}")
            time.sleep(1)

# Start pipe listener thread
pipe_thread = threading.Thread(target=listen_to_pipe, daemon=True)
pipe_thread.start()

# ===================================
# MEDIAPIPE & CAMERA SETUP
# ===================================
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Configure camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)

tts_engine = pyttsx3.init()
tts_lock = threading.Lock()

def say_hello():
    """Non-blocking TTS"""
    def speak():
        with tts_lock:
            tts_engine.say("Hello!")
            tts_engine.runAndWait()
    threading.Thread(target=speak, daemon=True).start()
    

def angle_between_points(a, b, c):
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)
    dot_product = ba[0]*bc[0] + ba[1]*bc[1]
    mag_ba = math.sqrt(ba[0]*ba[0] + ba[1]*ba[1])
    mag_bc = math.sqrt(bc[0]*bc[0] + bc[1]*bc[1])
    if mag_ba * mag_bc == 0:
        return 0
    cos_angle = dot_product / (mag_ba * mag_bc)
    angle_rad = math.acos(min(max(cos_angle, -1), 1))
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def draw_arm(frame, landmarks, shoulder_idx, elbow_idx, wrist_idx):
    h, w, _ = frame.shape
    shoulder = landmarks[shoulder_idx]
    elbow = landmarks[elbow_idx]
    wrist = landmarks[wrist_idx]

    shoulder_xy = (int(shoulder.x * w), int(shoulder.y * h))
    elbow_xy = (int(elbow.x * w), int(elbow.y * h))
    wrist_xy = (int(wrist.x * w), int(wrist.y * h))

    cv2.circle(frame, shoulder_xy, 8, (0, 255, 0), -1)
    cv2.circle(frame, elbow_xy, 8, (0, 255, 0), -1)
    cv2.circle(frame, wrist_xy, 8, (0, 255, 0), -1)

    cv2.line(frame, shoulder_xy, elbow_xy, (0, 255, 0), 4)
    cv2.line(frame, elbow_xy, wrist_xy, (0, 255, 0), 4)

def is_hand_raised(wrist, elbow, shoulder):
    wrist_above_shoulder = wrist.y < shoulder.y
    elbow_angle = angle_between_points(shoulder, elbow, wrist)
    return wrist_above_shoulder and elbow_angle < 160

# State variables
hand_raised_last_frame = False
last_wave_time = -10
WAVE_COOLDOWN = 10  # 10 seconds cooldown
command_sent_this_cycle = False

print("\n?? Wave Detection Active")
print("?? Raise your hand to trigger wave")
print("?? Arms will move when max.py sends movement commands")
print("??  Wave cooldown: 10 seconds")
print("Press 'q' to quit\n")

try:
    while True:
        frame = picam2.capture_array()
        
        results = pose.process(frame)
        
        current_time = time.time()
        time_since_last_wave = current_time - last_wave_time

        if time_since_last_wave >= WAVE_COOLDOWN:
            command_sent_this_cycle = False

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Draw arms
            draw_arm(frame, landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER,
                     mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST)
            draw_arm(frame, landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER,
                     mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST)

            # Check if either hand is raised
            left_hand_raised = is_hand_raised(
                landmarks[mp_pose.PoseLandmark.LEFT_WRIST],
                landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            )
            right_hand_raised = is_hand_raised(
                landmarks[mp_pose.PoseLandmark.RIGHT_WRIST],
                landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW],
                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            )

            hand_raised = left_hand_raised or right_hand_raised

            if hand_raised and not hand_raised_last_frame and not command_sent_this_cycle:
                if time_since_last_wave >= WAVE_COOLDOWN:
                    say_hello()
                    send_to_uno("WAVE")
                    last_wave_time = current_time
                    command_sent_this_cycle = True
                    print(f"?? Wave detected! Sending WAVE command.")
                else:
                    remaining = WAVE_COOLDOWN - time_since_last_wave
                    print(f"??  Cooldown active. Wait {remaining:.1f}s")

            hand_raised_last_frame = hand_raised
        else:
            hand_raised_last_frame = False

        # Display cooldown status
        if time_since_last_wave < WAVE_COOLDOWN:
            remaining = WAVE_COOLDOWN - time_since_last_wave
            status_text = f"Cooldown: {remaining:.0f}s"
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "Ready to wave!", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Wave Detection - Arms Only", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    pose.close()
    if arduino_uno:
        send_to_uno("S")  # Return to neutral
        arduino_uno.close()
        print("? Arduino Uno connection closed")
