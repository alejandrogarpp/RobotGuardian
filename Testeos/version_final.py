import cv2
import RPi.GPIO as GPIO
import time
import requests
from flask import Flask, Response

# --- PINES ---
PIN_VERDE = 20
PIN_ROJO = 21

PIN_PAN = 17   # X
PIN_TILT = 14  # Y

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(PIN_ROJO, GPIO.OUT)
GPIO.setup(PIN_VERDE, GPIO.OUT)

GPIO.setup(PIN_PAN, GPIO.OUT)
GPIO.setup(PIN_TILT, GPIO.OUT)

GPIO.output(PIN_VERDE, GPIO.HIGH)
GPIO.output(PIN_ROJO, GPIO.LOW)

# --- NOTIFICACIONES ---
CANAL_NTFY = "mi_robot_guardian_2026"
URL_NOTIF = f"https://ntfy.sh/{CANAL_NTFY}"
ultimo_envio = 0
INTERVALO_NOTIFICACION = 15

def enviar_alerta(mensaje):
    global ultimo_envio
    ahora = time.time()

    if ahora - ultimo_envio > INTERVALO_NOTIFICACION:
        try:
            requests.post(
                URL_NOTIF,
                data=mensaje.encode('utf-8'),
                headers={
                    "Title": "ALERTA GUARDIAN",
                    "Priority": "4",
                    "Tags": "robot,warning"
                },
                timeout=3
            )
            ultimo_envio = ahora
        except Exception as e:
            print(f"Error notificación: {e}")

# --- SERVOS ---
pwm_pan = GPIO.PWM(PIN_PAN, 50)
pwm_tilt = GPIO.PWM(PIN_TILT, 50)

pwm_pan.start(0)
pwm_tilt.start(0)

current_x = 45
current_y = 45

def mover_servos(x, y):
    x = max(0, min(180, x))
    y = max(0, min(180, y))

    duty_x = 2 + (x / 18)
    duty_y = 2 + (y / 18)

    pwm_pan.ChangeDutyCycle(duty_x)
    pwm_tilt.ChangeDutyCycle(duty_y)

    time.sleep(0.2)

    pwm_pan.ChangeDutyCycle(0)
    pwm_tilt.ChangeDutyCycle(0)

# --- FLASK + CV2 ---
app = Flask(__name__)
face_cascade = cv2.CascadeClassifier(
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_alt.xml"
)

cap = cv2.VideoCapture(0)

def gen_frames():
    global current_x, current_y

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
            enviar_alerta("🚨 ¡Intruso detectado! 🚨")

            GPIO.output(PIN_VERDE, GPIO.LOW)
            GPIO.output(PIN_ROJO, GPIO.HIGH)

            # usar la cara más grande
            face = max(faces, key=lambda b: b[2] * b[3])
            (x, y, w, h) = face

            cx = x + w // 2
            cy = y + h // 2

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

            margen_x = 40
            margen_y = 30
            paso = 3

            # --- X ---
            if cx < center_x - margen_x:
                current_x = min(180, current_x + paso)
            elif cx > center_x + margen_x:
                current_x = max(0, current_x - paso)

            # --- Y ---
            if cy < center_y - margen_y:
                current_y = max(0, current_y - paso)
            elif cy > center_y + margen_y:
                current_y = min(180, current_y + paso)

            mover_servos(current_x, current_y)

        else:
            GPIO.output(PIN_VERDE, GPIO.HIGH)
            GPIO.output(PIN_ROJO, GPIO.LOW)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <html>
    <body style="margin:0;background:black;">
        <img src="/video_feed" style="width:100vw;height:100vh;">
    </body>
    </html>
    '''

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        pwm_pan.stop()
        pwm_tilt.stop()
        GPIO.cleanup()