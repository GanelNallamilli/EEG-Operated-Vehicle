import time
import RPi.GPIO as GPIO

class MotorControl:
    def __init__(self, forward_left, backward_left, forward_right, backward_right):
        self.forward_left = forward_left
        self.backward_left = backward_left
        self.forward_right = forward_right
        self.backward_right = backward_right
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.forward_left, GPIO.OUT)
        GPIO.setup(self.backward_left, GPIO.OUT)
        GPIO.setup(self.forward_right, GPIO.OUT)
        GPIO.setup(self.backward_right, GPIO.OUT)

    def forward(self, duration):
        GPIO.output(self.forward_right, GPIO.HIGH)
        GPIO.output(self.forward_left, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.forward_right, GPIO.LOW)
        GPIO.output(self.forward_left, GPIO.LOW)

    def reverse(self, duration):
        GPIO.output(self.backward_left, GPIO.HIGH)
        GPIO.output(self.backward_right, GPIO.HIGH)
        print("Moving Backward")
        time.sleep(duration)
        GPIO.output(self.backward_left, GPIO.LOW)
        GPIO.output(self.backward_right, GPIO.LOW)
    
    def left(self, duration):
        GPIO.output(self.forward_right, GPIO.HIGH)
        GPIO.output(self.backward_left, GPIO.LOW)
        print("Turning Left")
        time.sleep(duration)
        GPIO.output(self.forward_right, GPIO.LOW)
    
    def right(self, duration):
        GPIO.output(self.forward_left, GPIO.HIGH)
        GPIO.output(self.backward_right, GPIO.LOW)
        print("Turning right")
        time.sleep(duration)
        GPIO.output(self.forward_left, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()

if __name__ == "__main__":
    motor = MotorControl(forward_left=20, backward_left=16, forward_right=26, backward_right=19)
    try:
        motor.forward(1)
        motor.reverse(1)
        motor.left(1)
        motor.right(1)
    finally:
        motor.cleanup()
