import RPi.GPIO as GPIO
import time
from time import sleep


SOUND_PIN_NUM = 20 #Sound module's OUT pin's GPIO num
LED_PIN_NUM = 26   # Led's long pin's GPIO num

state = 0 # led state
timeLast = time.time() #the last invoking time of the callback function
# in one sounding, the callback function will be invoked for a few times, so need wait for some time to 
validDuration = 0.1

GPIO.setmode(GPIO.BCM)
GPIO.setup(SOUND_PIN_NUM, GPIO.IN)
GPIO.setup(LED_PIN_NUM, GPIO.OUT)

def callback_fun_soundOccurred(input_pint):
    global timeLast
    timeNow = time.time()
    duration = timeNow - timeLast
    if (duration < validDuration):
        print("ignored because duration " + str(duration) + " is too short")
        timeLast = timeNow
        return
    print("accepted for valid duration " + str(duration))
    timeLast = timeNow
    switchLed()

def switchLed():
    global state
    if (state):
      turnOffLed()
      state = 0
    else:
      turnOnLed()
      state = 1

def turnOnLed():
    print("Turn on")
    GPIO.output(LED_PIN_NUM,GPIO.HIGH)

def turnOffLed():
    print("Turn off")
    GPIO.output(LED_PIN_NUM, GPIO.LOW)

GPIO.add_event_detect(SOUND_PIN_NUM, GPIO.RISING, callback=callback_fun_soundOccurred)

try:
    while True:
        sleep(0.1)
except KeyboardInterrupt:
    GPIO.remove_event_detect(SOUND_PIN_NUM)
    GPIO.cleanup()
