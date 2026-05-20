import cv2
import hardware
import notifications

face_cascade = cv2.CascadeClassifier(
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_alt.xml"
)

cap = cv2.VideoCapture(0)

def gen_frames():
    frames_sin_cara = 0
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.resize(frame, (480, 360))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        center_x = 480 // 2
        center_y = 360 // 2

        if len(faces) > 0:
            frames_sin_cara = 0
            notifications.enviar_alerta("🚨 ¡Intruso detectado! 🚨")
            hardware.set_leds(True)

            # usar la cara más grande
            face = max(faces, key=lambda b: b[2] * b[3])
            (x, y, w, h) = face

            cx = x + w // 2
            cy = y + h // 2

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
            hardware.track_face(cx, cy, center_x, center_y)

        else:
            frames_sin_cara += 1
            if frames_sin_cara > 10:
                hardware.set_leds(False)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

def cleanup():
    if cap.isOpened():
        cap.release()
