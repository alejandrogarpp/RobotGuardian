import RPi.GPIO as GPIO

PIN_VERDE, PIN_ROJO = 20, 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in [PIN_VERDE, PIN_ROJO]:
    GPIO.setup(pin, GPIO.OUT)

GPIO.output(PIN_VERDE, GPIO.LOW)
GPIO.output(PIN_ROJO, GPIO.LOW)