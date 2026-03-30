#!/usr/bin/env python3
import RPi.GPIO as GPIO  # type: ignore
import time
import pyaudio
import numpy as np
from core.state import state
from config.settings import OBSTACLE_WARN_DISTANCE_CM

from config.gpio_map import (
    US_FRONT_TRIG, US_FRONT_ECHO,
    US_LEFT_TRIG, US_LEFT_ECHO,
    US_RIGHT_TRIG, US_RIGHT_ECHO
)

def setup():
    """ Setup the GPIO pins for the ultrasonic sensors """
    GPIO.setmode(GPIO.BCM) # Using BCM numbering for Pi
    
    sensors = [
        (US_FRONT_TRIG, US_FRONT_ECHO),
        (US_LEFT_TRIG, US_LEFT_ECHO),
        (US_RIGHT_TRIG, US_RIGHT_ECHO)
    ]
    for trig, echo in sensors:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

def distance(trig_pin, echo_pin):
    """ Measure the distance using an ultrasonic sensor in cm """
    GPIO.output(trig_pin, 0)
    time.sleep(0.000002)
    GPIO.output(trig_pin, 1)
    time.sleep(0.00001)
    GPIO.output(trig_pin, 0)

    start_time = time.time()
    end_time = time.time()

    # Prevent infinite loops if sensor disconnects (timeout of 40ms = ~7m max range)
    timeout = start_time + 0.04 
    
    while GPIO.input(echo_pin) == 0 and time.time() < timeout:
        start_time = time.time()
    
    while GPIO.input(echo_pin) == 1 and time.time() < timeout:
        end_time = time.time()

    duration = end_time - start_time
    return (duration * 340 / 2) * 100  

# PyAudio setup for speaker beep synthesis
p = pyaudio.PyAudio()

def play_beep(duration_sec, frequency=800):
    """ Play a beep sound through the speaker using PyAudio """
    sample_rate = 44100
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)
    
    # Generate a sine wave tone
    tone = np.sin(frequency * t * 2 * np.pi)
    
    # Smooth edges to prevent speaker clicking or popping
    fade = min(int(sample_rate * 0.01), len(tone)//2)
    tone[:fade] *= np.linspace(0, 1, fade)
    tone[-fade:] *= np.linspace(1, 0, fade)
    
    # Convert to 16-bit PCM and play
    audio_data = (tone * 32767).astype(np.int16).tobytes()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()

def loop():
    """ Main loop checking distances from all sensors and outputting to speaker """
    while True:
        if not state.nav_mode_active:
            time.sleep(0.5)
            continue
            
        # Temporarily mute the sonar beeps if the system is currently talking
        if state.is_speaking:
            time.sleep(0.1)
            continue
            
        dis_front = distance(US_FRONT_TRIG, US_FRONT_ECHO)
        dis_left = distance(US_LEFT_TRIG, US_LEFT_ECHO)
        dis_right = distance(US_RIGHT_TRIG, US_RIGHT_ECHO)

        # Select the smallest distance from the 3 sensors
        min_distance = min(dis_front, dis_left, dis_right)
        
        # Determine closest direction
        if min_distance == dis_front: direction = "Front"
        elif min_distance == dis_left: direction = "Left"
        else: direction = "Right"

        print(f"Closest object: {min_distance:.1f} cm ({direction})")

        if min_distance < 5:  
            # If the object is within 5 cm, output long continuous-like buzz
            play_beep(0.5, 1000)
            time.sleep(0.1)
        elif min_distance < OBSTACLE_WARN_DISTANCE_CM:  
            # If within threshold, beep with decreasing interval
            beep_interval = (min_distance - 5) / 50.0  
            play_beep(0.1, 800)
            time.sleep(beep_interval)
        else:
            # Turn off speaker (just sleep)
            time.sleep(0.3)

def destroy():
    """ Cleanup function to reset GPIO settings """
    GPIO.cleanup()
    p.terminate()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
