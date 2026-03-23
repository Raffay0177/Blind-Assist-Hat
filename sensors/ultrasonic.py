import RPi.GPIO as GPIO  # type: ignore
import time

def setup(trig_pin, echo_pin):
    # Set up the GPIO mode and pins
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(trig_pin, GPIO.OUT)
    GPIO.setup(echo_pin, GPIO.IN)

def distance(trig_pin, echo_pin):
    # Ensure trigger is low
    GPIO.output(trig_pin, 0)
    time.sleep(0.000002)
    
    # Send a 10 microsecond pulse to trigger the sensor
    GPIO.output(trig_pin, 1)
    time.sleep(0.00001)
    GPIO.output(trig_pin, 0)
    
    start_time = time.time()
    end_time = time.time()
    
    # Wait for the echo to start
    while GPIO.input(echo_pin) == 0:
        start_time = time.time()
    
    # Wait for the echo to end
    while GPIO.input(echo_pin) == 1:
        end_time = time.time()
    
    duration = end_time - start_time
    # Calculate distance: (duration * speed of sound (340 m/s) / 2) * 100 to convert to cm
    return duration * 340 / 2 * 100
