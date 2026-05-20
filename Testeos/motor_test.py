import RPi.GPIO as GPIO
import time

PIN_ARRIBA = 17
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ARRIBA, GPIO.OUT)


pwm_pan = GPIO.PWM(PIN_ARRIBA, 50)  # 50Hz (frecuencia típica servo)
pwm_pan.start(0)
current_y = 45
current_x = 90

def mover_base(angulo):
    duty = 2 + (angulo / 18)
    pwm_pan.ChangeDutyCycle(duty)
    time.sleep(0.3)
    pwm_pan.ChangeDutyCycle(0)

mover_base(45)

