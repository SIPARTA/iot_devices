import logging
import time

try:
    import RPi.GPIO as GPIO
    IS_RPI = True
except ImportError:
    IS_RPI = False

logger = logging.getLogger("siparta.hardware_output")

LED_GREEN = 27
LED_YELLOW = 22
LED_RED = 23
BUZZER = 24

if IS_RPI:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in [LED_GREEN, LED_YELLOW, LED_RED, BUZZER]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def set_level(level: str):
    """Set the hardware indication level: AMAN, WASPADA, BAHAYA"""
    if not IS_RPI:
        return
        
    GPIO.output(LED_GREEN, GPIO.LOW)
    GPIO.output(LED_YELLOW, GPIO.LOW)
    GPIO.output(LED_RED, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.LOW)
    
    if level == "AMAN":
        GPIO.output(LED_GREEN, GPIO.HIGH)
    elif level == "WASPADA":
        GPIO.output(LED_YELLOW, GPIO.HIGH)
    elif level == "BAHAYA":
        GPIO.output(LED_RED, GPIO.HIGH)
        GPIO.output(BUZZER, GPIO.HIGH)

def start_alarm():
    if IS_RPI:
        GPIO.output(BUZZER, GPIO.HIGH)

def stop_alarm():
    if IS_RPI:
        GPIO.output(BUZZER, GPIO.LOW)

def beep(n: int = 1):
    if not IS_RPI:
        return
    for _ in range(n):
        GPIO.output(BUZZER, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(BUZZER, GPIO.LOW)
        time.sleep(0.1)

def cleanup():
    if IS_RPI:
        GPIO.cleanup()
