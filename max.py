import speech_recognition as sr
import pyttsx3
from openai import OpenAI
import time
import os
import serial
import threading
import sys
import select

# Environment cleanup for ALSA (reduce audio warnings)
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["ALSA_LOG_LEVEL"] = "0"

# Initialize recognizer and speech engine
r = sr.Recognizer()
r.energy_threshold = 4000
r.dynamic_energy_threshold = True
engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 1.0)

# Assistant setup
ASSISTANT_NAME = "Max"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# ===================================
# ARDUINO MEGA 2560 CONNECTION
# ===================================
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)
    print("? Arduino Mega 2560 connected successfully")
except Exception as e:
    print(f"?? Arduino Mega connection failed: {e}")
    print("Trying alternative port /dev/ttyUSB0...")
    try:
        arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        time.sleep(2)
        print("? Arduino Mega 2560 connected on /dev/ttyUSB0")
    except:
        arduino = None
        print("? Could not connect to Arduino Mega")

print(f"\n?? {ASSISTANT_NAME} is active with Arduino Mega 2560!")
print("????????????????????????????????????")
print("Voice commands: Say movement commands")
print("Keyboard commands: Type during listening")
print("  f = forward")
print("  b = backward")
print("  l = left")
print("  r = right")
print("  s = stop")
print("  q = quit")
print("Say 'exit' or type 'q' to stop.\n")

# Select your working mic device index
mic_index = 2  # DroidCam microphone

# Global flag for running
running = True
tts_lock = threading.Lock()  # Prevent overlapping speech

def send_motor_command(command):
    """Send command to Arduino Mega (DC motors)"""
    if arduino:
        try:
            arduino.write(f"{command}\n".encode())
            time.sleep(0.1)
            if arduino.in_waiting > 0:
                response = arduino.readline().decode().strip()
                print(f"  ?? Arduino Mega: {response}")
                return response
        except Exception as e:
            print(f"Error sending to Mega: {e}")
    else:
        print("Arduino Mega not connected!")
    return None

def send_to_uno_pipe(command):
    """Send command to Arduino Uno via named pipe (for arm servos)"""
    try:
        with open(PIPE_PATH, 'w') as pipe:
            pipe.write(f"{command}\n")
            pipe.flush()
        print(f"  ?? Sent to Uno via pipe: {command}")
    except Exception as e:
        print(f"Pipe error: {e}")

def send_dual_command(command):
    """Send command to BOTH Mega (motors) and Uno (arms via pipe)"""
    print(f"?? Broadcasting '{command}' to Mega + Uno...")
    
    # Send to Mega (DC motors)
    mega_thread = threading.Thread(target=send_motor_command, args=(command,), daemon=True)
    mega_thread.start()
    
    # Send to Uno via pipe (arm servos)
    send_to_uno_pipe(command)
    
    mega_thread.join(timeout=1)

def speak(text):
    """Non-blocking text-to-speech"""
    def _speak():
        with tts_lock:
            engine.say(text)
            engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

def execute_movement(command, action_text, speech_text):
    """Execute movement command with speech feedback on BOTH systems"""
    print(f"?? Command: {action_text}")
    send_dual_command(command)  # Send to BOTH Mega and Uno
    speak(speech_text)
    
def process_motor_command(user_input):
    """Check if user input contains motor command keywords and execute it"""
    user_input_lower = user_input.lower().strip()
    
    # Check for movement commands
    if any(word in user_input_lower for word in ["move forward", "go forward", "moving forward"]):
        execute_movement("F", "Moving forward", "Moving forward")
        return True
    
    elif any(word in user_input_lower for word in ["move backward", "go backward", "move back", "go back", "moving backward"]):
        execute_movement("B", "Moving backward", "Moving backward")
        return True
    
    elif any(word in user_input_lower for word in ["turn right", "turning right", "go right"]):
        execute_movement("R", "Turning right", "Turning right")
        return True
    
    elif any(word in user_input_lower for word in ["turn left", "turning left", "go left"]):
        execute_movement("L", "Turning left", "Turning left")
        return True
    
    elif any(word in user_input_lower for word in ["stop moving", "stop now", "halt", "freeze"]) or user_input_lower == "stop":
        execute_movement("S", "Stopping", "Stopping")
        return True
    
    # Single word commands
    elif "forward" in user_input_lower and "backward" not in user_input_lower:
        execute_movement("F", "Moving forward", "Moving forward")
        return True
    
    elif "backward" in user_input_lower or "back" in user_input_lower:
        execute_movement("B", "Moving backward", "Moving backward")
        return True
    
    elif "right" in user_input_lower:
        execute_movement("R", "Turning right", "Turning right")
        return True
    
    elif "left" in user_input_lower:
        execute_movement("L", "Turning left", "Turning left")
        return True
    
    return False

def keyboard_input_thread():
    """Thread to handle keyboard input with speech feedback"""
    global running
    print("??  Keyboard input thread started")
    
    while running:
        try:
            # Check if input is available (non-blocking)
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.readline().strip().lower()
                
                if key == 'f':
                    execute_movement("F", "??  Keyboard: Moving forward", "Moving forward")
                elif key == 'b':
                    execute_movement("B", "??  Keyboard: Moving backward", "Moving backward")
                elif key == 'l':
                    execute_movement("L", "??  Keyboard: Turning left", "Turning left")
                elif key == 'r':
                    execute_movement("R", "??  Keyboard: Turning right", "Turning right")
                elif key == 's':
                    execute_movement("S", "??  Keyboard: Stopping", "Stopping")
                elif key == 'q':
                    print("??  Keyboard: Quit")
                    running = False
                    break
                    
        except Exception as e:
            print(f"Keyboard input error: {e}")
            time.sleep(0.1)

# Start keyboard input thread
keyboard_thread = threading.Thread(target=keyboard_input_thread, daemon=True)
keyboard_thread.start()

while running:
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("?? Listening... (or type command)")
            r.adjust_for_ambient_noise(source, duration=1.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=8)

        try:
            user_input = r.recognize_google(audio)
            print(f"You said: {user_input}")
        except sr.UnknownValueError:
            print("Could not understand, please try again.")
            continue

        if user_input.lower() in ["exit", "quit", "stop listening"]:
            send_dual_command("S")
            print(f"Goodbye! {ASSISTANT_NAME} signing off.")
            speak("Goodbye! See you soon.")
            running = False
            break

        # Check if it's a motor command first
        if process_motor_command(user_input):
            continue
        
        if user_input.lower() in ["hi", "hello", "hey"]:
            ai_reply = f"Hello! I am {ASSISTANT_NAME}. How can I assist you today?"
            print(f"{ASSISTANT_NAME}: {ai_reply}")
            speak(ai_reply)
            continue

        # Send to OpenAI for a response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a friendly assistant named {ASSISTANT_NAME}. You can control a robot's movements."},
                {"role": "user", "content": user_input}
            ]
        )

        ai_reply = response.choices[0].message.content.strip()
        print(f"{ASSISTANT_NAME}: {ai_reply}")

        speak(ai_reply)
        time.sleep(0.5)

    except sr.WaitTimeoutError:
        print("Listening timed out, no speech detected.")
    except sr.RequestError as e:
        print("Speech Recognition error:", e)
    except KeyboardInterrupt:
        print("\nExiting...")
        send_dual_command("S")
        running = False
        break
    except Exception as e:
        print(f"Unexpected error: {e}")

# Close serial connection
if arduino:
    send_motor_command("S")  # Final stop command
    arduino.close()
    print("Arduino Mega 2560 connection closed")
