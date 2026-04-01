import RPi.GPIO as GPIO
import time

PIN_ARRIBA = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ARRIBA, GPIO.OUT)

pwm = GPIO.PWM(PIN_ARRIBA, 50)  # 50Hz (frecuencia típica servo)
pwm.start(0)

def set_angle(angle):
    duty = 2 + (angle / 18)
    GPIO.output(PIN_ARRIBA, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(PIN_ARRIBA, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        set_angle(0)
        time.sleep(1)
        set_angle(90)
        time.sleep(1)
        set_angle(180)
        time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()