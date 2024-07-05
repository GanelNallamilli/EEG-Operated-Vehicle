import argparse
import os
import time
from datetime import datetime
from scipy.fftpack import rfft,rfftfreq 
import numpy as np
import movement as m
import RPi.GPIO as GPIO
import distance as d

from pythonosc import dispatcher
from pythonosc import osc_server

eegTP9Array = []
eegAF7Array = []
eegAF8Array = []
eegTP10Array = []
timeArray = []
boolean = True

forward_Back = False
turn_drive_toggle = False
limitDrive = False
left_right_toggle = True
limiter = False


sample = 256

'''Starting information which is printed to the console... script stops after 90 seconds.'''
def stoppingTime():
    print("STARTED COUNT DOWN")
    print("Current state: RIGHT")
    print("Blink to change rotation")
    print("Tilt head forward to go forward")
    print("Tilt head bakcward to go backwards")
    m.run()
    time.sleep(90)
    GPIO.cleanup()
    os._exit(0)

'''Detects if the user is tilting their head forward or backwards.'''
def dataGyro(none: float,accForBack: float,accLeftRight: float,accZ: float):
    global turn_drive_toggle,left_right_toggle,limitDrive,forward_Back
    if((accForBack > 0.5)):
        turn_drive_toggle = True
        if(forward_Back == False or limitDrive == True):
            forward_Back = True
            limitDrive = False
            limiter = True
            print("Forward")
    if((accForBack < -0.5)):
        turn_drive_toggle = True
        if(forward_Back == True or limitDrive == True):
            forward_Back = False
            limitDrive = False
            limiter = True
            print("Backward")

#method called by dispatcher to receive eeg data.
def data(eeg1: float,eeg2: float,eeg3: float,eeg4: float,eeg5: float,eeg6: float):
    global boolean
    action(eeg2,eeg3,eeg4,eeg6)
    if(boolean == True):
        boolean = False
        stoppingTime()

#writes 550 frames of eeg to a .csv file.
def action(eegTP9,eegAF7,eegAF8,eegTP10):
    global turn_drive_toggle,left_right_toggle,limitDrive,forward_Back,limiter
    global eegTP9Array,eegAF7Array,timeArray,eegAF8Array,eegTP10Array,filename,count
    stop = False
    limiter = False
    eegTP9Array.append(str(eegTP9))
    eegAF7Array.append(str(eegAF7))
    eegAF8Array.append(str(eegAF8))
    eegTP10Array.append(str(eegTP10))
    timeArray.append(str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
    if((len(eegTP9Array) or len(eegAF7Array) or len(eegAF8Array) or len(eegTP10Array)) == sample):
        #stores the relative time elapsed per sample
        npArray = []
        startTime = 0 #Variable to start the start time in seconds.
        npArray = np.array(timeArray[:sample]) # converts the timeColumn data from to a numpy array.
        
        #loops through the unformatted time array, and replaces each element with its relative time from the start time.
        for i in range (0,len(npArray)):
            #tempArray stores the components of time, by splitting the formatted time.
            #We start with "2021-02-17 15:36:15.614" then we get the last 12 characters which gives "15:36:15.614".
            #We then split "15:36:15.614" by the colon to work with the hours,minutes and seconds separetly.
            #Therefore the tempArray will store ["15","36","15.614"] for each element in the unformated time array (npArray) in example.
            tempArray = npArray[i][-12:].split(":")

            #if i is 0, then we know we are working with the first recorded time. So we have to work out the start time in seconds, and
            # we want to set the first element of the unformatted npArray to be 0, since the start time is time 0.
            if(i ==0):
                #works out the start time in seconds by multiplying the hours and minutes by 60^2 and 60 respectively
                #then will add all the time components up, essentially turning a time like 16:01:01.002 to 57661.002 seconds.
                #This means that aslong as our data does not cross over the 24 hour mark then the alorigthm will work.
                startTime = float(tempArray[0])*(60**2) + float(tempArray[1])*60 +float(tempArray[2])
                npArray[i] = 0 #sets first element to 0.
            else:
                #if we are not working with the start time, then it translates ordinary 24 hour time into seconds like 'startTime' before.
                totalTime = float(tempArray[0])*(60**2) + float(tempArray[1])*60 +float(tempArray[2])
                #We then update the unformatted element with the relative time, slowly formatting each element as the loop tends to len(npArray)
                npArray[i] = totalTime - startTime
        
        average = 0

        #fast fourier transform of the eeg data 
        yf = rfft(eegAF7Array[:sample])
        #fast foruier transform of the time spectrum -> frequency domain
        xf = rfftfreq(len(npArray[:sample]),1/sample)
        absYF = np.abs(yf)
        power_spectrum = np.square(absYF)

        #Artifacts found between above 48 hertz and below 5 Hertz, so we set these to 0 in the power spectrum 
        for j in range(0,len(xf)):
            for j in range(0,len(xf)):
                if (xf[j]< 5 or xf[j] > 48) :
                    power_spectrum[j] = 0

        arrayPower = findMaximumFreq(power_spectrum,xf)
        #average of top 3 powerful frequencies is calculated to detect jaw cletching
        average = (arrayPower[0]+arrayPower[1]+arrayPower[2])/3

        high1000 = False
        low9000 = False
        indexRemember = -1

        #In the sample if an eeg measurement of above 1050 followed by a low of below 700, high1000 == True and low9000 == True (indicating a blink)
        for i in range(0,len(eegAF7Array)):
            if(float(eegAF7Array[i]) > 1050.0):
                high1000  = True
                indexRemember = i
                break
        if(high1000 == True):
            for i in range(indexRemember,len(eegAF7Array)):
                if(float(eegAF7Array[i]) < 700.0):
                    low9000  = True
                    break
        
        #limiter detects if the user head is tilted forward or backwards, if their head is tilted, this if statement won't run.
        #Otherwise, a registered blink as been detected so this if statement will run.
        if(high1000 == True and low9000 == True and limiter == False):
            turn_drive_toggle = False
            limitDrive = True
            if(left_right_toggle == True):
                left_right_toggle = False
            elif(left_right_toggle == False):
                left_right_toggle = True
            
            #Toggles the car to move forward or backwards
            if(left_right_toggle == False):
                print("Left")
            elif(left_right_toggle == True):
                print("Right")

        #If the vehicle is 10 cm away from an obsticle from the back or front, the car will not move.
        if d.getDistanceFront >= 10 or d.getDistanceBack >= 10:
            stop = True
        
        #if the average is greater or equal to 25, the user is cletching their jaw, which means they want the car to move.
        if not stop:
            if(average >= 25):
                #Moves the car....
                if(turn_drive_toggle == False):
                    if(left_right_toggle == False):
                        m.left(1)
                    elif(left_right_toggle == True):
                        m.right(1)
                elif(turn_drive_toggle == True):
                    if(forward_Back == True):
                        m.forward(1)
                    elif(forward_Back == False):
                        m.reverse(1)

        
        eegTP9Array = []
        eegAF7Array = []
        eegAF8Array = []
        eegTP10Array = []
        timeArray = []

'''Returns the top 80 most powerful frequencies from the power spectrum '''       
def findMaximumFreq(power_spectrum,xf):
    top80Array = []
    count = 0
    sortedPower_Spectrum = -np.sort(-power_spectrum)
    for i in range(0,len(sortedPower_Spectrum)):
        if (count == 3):
            break
        for j in range(0,len(power_spectrum)):
            if((power_spectrum[j] == sortedPower_Spectrum[i])):
                if(isInArray(xf[j],top80Array)):
                    top80Array.append(xf[j])
                    count += 1
                    break
    return top80Array

#checks to see if number is in array.
def isInArray(value,array):
        for i in range(0,len(array)):
            if(float(value) == float(array[i])):
                return False
        return True

#initalises the the port and ip to start receiving osc data packets.
if __name__ == "__main__":
    time.sleep(1)
    print("Staring now!")
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        default="192.168.119.150", help="The ip to listen on")
    parser.add_argument("--port",
        type=int, default=5000, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/muse/acc",dataGyro)
    dispatcher.map("/muse/eeg",data)

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()