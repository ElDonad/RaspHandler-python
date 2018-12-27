import RPi.GPIO as GPIO

class gpio:

    OUT = GPIO.OUT
    IN = GPIO.IN
    LOW = GPIO.LOW
    HIGH = GPIO.HIGH
    def init():
        gpio.setMode()

    def setMode():
        GPIO.setmode(GPIO.BCM)

    def setup(pin, mode= OUT):
        GPIO.setup(pin, mode)
        print('[GPIO]setting ' + str(pin) + 'to ' + str(mode))

    def output(pin, state):
        print('[GPIO]setting pin ' + str(pin) + ' at state : ' + str(state))
        GPIO.output(pin, state)
