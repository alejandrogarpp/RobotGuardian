import RPi.GPIO as GPIO
import time

# --- PINES ---
PIN_VERDE = 20
PIN_ROJO = 21

PIN_PAN = 17   # X
PIN_TILT = 14  # Y

pwm_pan = None
pwm_tilt = None

current_x = 45
current_y = 45

def setup():
    global pwm_pan, pwm_tilt

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(PIN_ROJO, GPIO.OUT)
    GPIO.setup(PIN_VERDE, GPIO.OUT)

    GPIO.setup(PIN_PAN, GPIO.OUT)
    GPIO.setup(PIN_TILT, GPIO.OUT)

    GPIO.output(PIN_VERDE, GPIO.HIGH)
    GPIO.output(PIN_ROJO, GPIO.LOW)

    pwm_pan = GPIO.PWM(PIN_PAN, 50)
    pwm_tilt = GPIO.PWM(PIN_TILT, 50)

    pwm_pan.start(0)
    pwm_tilt.start(0)

def set_leds(face_detected):
    if face_detected:
        GPIO.output(PIN_VERDE, GPIO.LOW)
        GPIO.output(PIN_ROJO, GPIO.HIGH)
    else:
        GPIO.output(PIN_VERDE, GPIO.HIGH)
        GPIO.output(PIN_ROJO, GPIO.LOW)

def mover_servos(x, y):
    global current_x, current_y
    
    x = max(0, min(180, x))
    y = max(0, min(180, y))

    current_x = x
    current_y = y

    duty_x = 2 + (x / 18)
    duty_y = 2 + (y / 18)

    pwm_pan.ChangeDutyCycle(duty_x)
    pwm_tilt.ChangeDutyCycle(duty_y)

    time.sleep(0.2)

    pwm_pan.ChangeDutyCycle(0)
    pwm_tilt.ChangeDutyCycle(0)

def track_face(cx, cy, center_x, center_y):
    global current_x, current_y
    
    margen_x = 40
    margen_y = 30
    paso = 3

    new_x = current_x
    new_y = current_y

    # --- X ---
    if cx < center_x - margen_x:
        new_x = min(180, current_x + paso)
    elif cx > center_x + margen_x:
        new_x = max(0, current_x - paso)

    # --- Y ---
    if cy < center_y - margen_y:
        new_y = max(0, current_y - paso)
    elif cy > center_y + margen_y:
        new_y = min(180, current_y + paso)

    if new_x != current_x or new_y != current_y:
        mover_servos(new_x, new_y)

def cleanup():
    if pwm_pan:
        pwm_pan.stop()
    if pwm_tilt:
        pwm_tilt.stop()
    GPIO.cleanup()
