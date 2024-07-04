
import time
import RPi.GPIO as GPIO





mode=GPIO.getmode()

GPIO.cleanup()

ForwardLeft=20
ForwardRight=26
BackwardLeft=16
BackwardRight=19
sleeptime=1
GPIO.setmode(GPIO.BCM)
GPIO.setup(ForwardLeft, GPIO.OUT)
GPIO.setup(BackwardLeft, GPIO.OUT)
GPIO.setup(ForwardRight, GPIO.OUT)
GPIO.setup(BackwardRight, GPIO.OUT)

def run():
    global ForwardLeft,BackwardLeft,ForwardRight,BackwardRight
    mode=GPIO.getmode()
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()

    ForwardLeft=20
    ForwardRight=26
    BackwardLeft=16
    BackwardRight=19
    GPIO.setup(ForwardLeft, GPIO.OUT)
    GPIO.setup(BackwardLeft, GPIO.OUT)
    GPIO.setup(ForwardRight, GPIO.OUT)
    GPIO.setup(BackwardRight, GPIO.OUT)

def forward(x):
    global ForwardLeft,BackwardLeft,ForwardRight,BackwardRight,count
    GPIO.output(ForwardRight, GPIO.HIGH)
    GPIO.output(ForwardLeft, GPIO.HIGH)
    time.sleep(x)
    GPIO.output(ForwardRight, GPIO.LOW)
    GPIO.output(ForwardLeft, GPIO.LOW)


def reverse(x):
    global ForwardLeft,BackwardLeft,ForwardRight,BackwardRight,count
    GPIO.output(BackwardLeft, GPIO.HIGH)
    GPIO.output(BackwardRight, GPIO.HIGH)
    print("Moving Backward")
    time.sleep(x)
    GPIO.output(BackwardLeft, GPIO.LOW)
    GPIO.output(BackwardRight, GPIO.LOW)
    
def left(x):
    global ForwardLeft,BackwardLeft,ForwardRight,BackwardRight
    GPIO.output(ForwardRight, GPIO.HIGH)
    GPIO.output(BackwardLeft, GPIO.LOW)
    print("Turning Left")
    time.sleep(x)
    GPIO.output(BackwardLeft, GPIO.LOW)
    GPIO.output(ForwardRight, GPIO.LOW)

def right(x):
    global ForwardLeft,BackwardLeft,ForwardRight,BackwardRight
    GPIO.output(ForwardLeft, GPIO.HIGH)
    GPIO.output(BackwardRight, GPIO.LOW)
    print("Turning right")
    time.sleep(x)
    GPIO.output(ForwardLeft, GPIO.LOW)
    GPIO.output(BackwardRight, GPIO.LOW)

# GPIO.output(ForwardRight, GPIO.LOW)
# GPIO.output(ForwardLeft, GPIO.LOW)
# GPIO.output(ForwardLeft, GPIO.LOW)
# GPIO.output(BackwardRight, GPIO.LOW)
# forwardNoSense(3)


        
    
        