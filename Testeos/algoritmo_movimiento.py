import cv2
import RPi.GPIO as GPIO
import time
from flask import Flask, Response

# --- CONFIGURACIÓN SERVO ---
PIN_PAN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_PAN, GPIO.OUT)
pwm_pan = GPIO.PWM(PIN_PAN, 50)
pwm_pan.start(0)
current_x = 90

def mover_base(angulo):
    duty = 2 + (angulo / 18)
    pwm_pan.ChangeDutyCycle(duty)
    time.sleep(0.03)
    pwm_pan.ChangeDutyCycle(0)

# --- CONFIGURACIÓN FLASK Y CV2 ---
app = Flask(__name__)
# ASEGÚRATE DE QUE ESTE ARCHIVO EXISTE O CAMBIA LA RUTA
face_cascade = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_alt.xml")
cap = cv2.VideoCapture(0)

def gen_frames():
    global current_x
    while True:
        success, frame = cap.read()
        if not success: break
        
        frame = cv2.resize(frame, (480, 360))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w_f, h_f) in faces:
            centro_cara_x = x + (w_f // 2)
            centro_pantalla_x = 480 // 2
            cv2.rectangle(frame, (x, y), (x + w_f, y + h_f), (0, 255, 0), 2)

            margen = 40
            paso = 3
            if centro_cara_x < (centro_pantalla_x - margen):
                current_x = min(180, current_x + paso)
            elif centro_cara_x > (centro_pantalla_x + margen):
                current_x = max(0, current_x - paso)
            
            mover_base(current_x)
            break 

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h1>Rastreador Activo</h1><img src="/video_feed" width="480">'

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        pwm_pan.stop()
        GPIO.cleanup()