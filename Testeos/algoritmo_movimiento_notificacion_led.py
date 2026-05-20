import cv2
import RPi.GPIO as GPIO
import time
import requests  # Importante: pip install requests
from flask import Flask, Response

PIN_VERDE = 20  # Pin físico 40
PIN_ROJO = 21  # Pin físico 38
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ROJO, GPIO.OUT)
GPIO.setup(PIN_VERDE, GPIO.OUT)

GPIO.output(PIN_VERDE, GPIO.HIGH)
GPIO.output(PIN_ROJO, GPIO.LOW)

# --- CONFIGURACIÓN NOTIFICACIONES ---
CANAL_NTFY = "mi_robot_guardian_2026" 
URL_NOTIF = f"https://ntfy.sh/{CANAL_NTFY}"
ultimo_envio = 0  
INTERVALO_NOTIFICACION = 15 

def enviar_alerta(mensaje):
    global ultimo_envio
    ahora = time.time()
    # Solo envía si han pasado más de 30 segundos desde la última vez
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
            print(f"✅ Notificación enviada. Siguiente disponible en 30s.")
        except Exception as e:
            print(f"⚠️ Error al enviar notificación: {e}")

# --- CONFIGURACIÓN SERVO ---
PIN_PAN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_PAN, GPIO.OUT)
pwm_pan = GPIO.PWM(PIN_PAN, 50)
pwm_pan.start(0)
current_x = 45

def mover_base(angulo):
    duty = 2 + (angulo / 18)
    pwm_pan.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm_pan.ChangeDutyCycle(0)

# --- CONFIGURACIÓN FLASK Y CV2 ---
app = Flask(__name__)
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

        # SI SE DETECTA AL MENOS UNA CARA
        if len(faces) > 0:
            enviar_alerta("🚨 ¡Intruso detectado! 🚨")
            GPIO.output(PIN_VERDE, GPIO.LOW)
            GPIO.output(PIN_ROJO, GPIO.HIGH)

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

        elif len(faces) == 0:
            GPIO.output(PIN_VERDE, GPIO.HIGH)
            GPIO.output(PIN_ROJO, GPIO.LOW)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Guardian AI - Control Panel</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: #121212;
                color: white;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                overflow: hidden;
            }
            .header {
                padding: 15px;
                text-align: center;
                background: rgba(0, 0, 0, 0.8);
                width: 100%;
                position: absolute;
                top: 0;
                z-index: 10;
                border-bottom: 2px solid #2ecc71;
            }
            h1 {
                margin: 0;
                font-size: 1.5rem;
                letter-spacing: 2px;
                text-transform: uppercase;
                color: #2ecc71;
            }
            .video-container {
                width: 1344vw;
                height: 756vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #000;
            }
            .video-feed {
                max-width: 100%;
                max-height: 100%;
                width: auto;
                height: auto;
                object-fit: contain;
                border: 2px solid #333;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
            }
            .status-overlay {
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(0,0,0,0.6);
                padding: 10px 20px;
                border-radius: 5px;
                border-left: 4px solid #2ecc71;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RASTREADOR GUARDIÁN ACTIVO</h1>
        </div>
        
        <div class="video-container">
            <img src="/video_feed" class="video-feed">
        </div>

        <div class="status-overlay">
            <span>SISTEMA: EN LÍNEA</span>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        pwm_pan.stop()
        GPIO.cleanup()