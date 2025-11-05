from picamera2 import Picamera2
import cv2
import urllib.request
import os

CASCADE_PATH = 'haarcascade_frontalface_default.xml'
if not os.path.exists(CASCADE_PATH):
    urllib.request.urlretrieve(
        'https://github.com/opencv/opencv/raw/master/data/haarcascades/haarcascade_frontalface_default.xml',
        CASCADE_PATH)

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

KNOWN_FACE_WIDTH_CM = 16.0  # average human face width, adjust if needed
FOCAL_LENGTH = 800  # calibrate this for your camera setup

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888"}))
picam2.start()

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        distance = (KNOWN_FACE_WIDTH_CM * FOCAL_LENGTH) / w
        cv2.putText(frame, f"{int(distance)} cm", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    cv2.imshow("Face Detection with Distance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
