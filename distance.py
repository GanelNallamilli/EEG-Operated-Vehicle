import RPi.GPIO as GPIO
import time

def measure_distance(trigger_pin, echo_pin):
    GPIO.setmode(GPIO.BCM)
    
    # Set GPIO direction (IN / OUT)
    GPIO.setup(trigger_pin, GPIO.OUT)
    GPIO.setup(echo_pin, GPIO.IN)
    
    # Set Trigger to HIGH
    GPIO.output(trigger_pin, True)
    
    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(trigger_pin, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    # Save StartTime
    while GPIO.input(echo_pin) == 0:
        StartTime = time.time()
    
    # Save time of arrival
    while GPIO.input(echo_pin) == 1:
        StopTime = time.time()
    
    # Time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # Multiply with the sonic speed (34300 cm/s) and divide by 2 (there and back)
    distance = (TimeElapsed * 34300) / 2
    return distance

def distanceFront():
    return measure_distance(trigger_pin=4, echo_pin=17)

def distanceBack():
    return measure_distance(trigger_pin=3, echo_pin=18)
 
distFront = distanceFront()
distBack= distanceBack()
print ("Measured Front Distance = %.1f cm" % distFront)
print ("Measured Back Distance = %.1f cm" % distBack)
#GPIO.cleanup()