# EEG-Operated-Vehicle

This project demonstrates controlling a Raspberry Pi (model 4b) vehicle using EEG data from a Muse headband. The vehicle responds to jaw clenching and head orientation, enabling it to move forward, backward, and turn left or right.

## Table of Contents

1. [Introduction](#introduction)
2. [Setup](#setup)
3. [Hardware Connections](#hardware-connections)
4. [Software Installation](#software-installation)
5. [Usage](#usage)
6. [How it Works](#how-it-works)
7. [Code Snippets](#code-snippets)
8. [Expected Output](#expected-output)
9. [Future Work](#future-work)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

## Introduction

### Motivation

The primary motivation behind this project is to create an assistive technology that allows individuals with certain disabilities to operate a vehicle using simple, non-invasive EEG signals. By utilizing the Muse headband, we aim to demonstrate that advanced control mechanisms can be achieved with relatively simple and affordable technology. This project showcases how EEG data can be harnessed to enable mobility solutions, contributing to the field of assistive technologies.

### Project Overview

This project uses a Muse headband to read EEG signals and send them to a Raspberry Pi via the OSC protocol. By detecting jaw clenching and head orientation, the system controls the movement of a small vehicle. The vehicle can move forward, backward, and turn left or right based on the user's actions.

## Setup

### Prerequisites

- Muse headband
- Raspberry Pi (model 4b)
- Motor driver
- Ultrasonic sensor
- Mind Monitor app on a smartphone
- Local computer for data transfer

### Mind Monitor App Configuration

1. Install the Mind Monitor app on your smartphone.
2. Connect the Muse headband to your smartphone via Bluetooth.
3. Configure the app to send EEG data to your local computer using the OSC protocol.

### Updating Pin Numbers

- **Motors**: Connect the motor pins and update the pin numbers in `movement.py`.
- **Ultrasonic Sensors**: Connect the ultrasonic sensor's trig and echo pins to the Raspberry Pi, and update the pin numbers in `distance.py`.
- **Local IP Address**: Set the `local_ip` in `main.py` to the IP address of the computer running the `main.py` script and configure the port (line 232).

## Hardware Connections

### Motor Driver

Connect the motor driver pins to the Raspberry Pi GPIO as follows:
- Forward Left: GPIO 20
- Forward Right: GPIO 26
- Backward Left: GPIO 16
- Backward Right: GPIO 19

### Ultrasonic Sensors

Connect the ultrasonic sensors to the Raspberry Pi GPIO:
- Front Sensor Trigger: GPIO 4
- Front Sensor Echo: GPIO 17
- Back Sensor Trigger: GPIO 3
- Back Sensor Echo: GPIO 18

## Software Installation

1. Install the required Python libraries:
    ```bash
    pip install numpy scipy python-osc RPi.GPIO
    ```

2. Clone the repository to your local computer:
    ```bash
    git clone https://github.com/yourusername/eeg-operated-raspberry-pi-vehicle.git
    cd eeg-operated-raspberry-pi-vehicle
    ```

3. Update the IP address and port in `main.py` (line 232) to match your local computer's settings.

## Usage

1. Ensure the Muse headband is connected to your smartphone and the Mind Monitor app is configured to send EEG data to your local computer.
2. Run the `main.py` script on your local computer:
    ```bash
    python main.py --ip YOUR_LOCAL_IP --port YOUR_PORT
    ```

3. The script will run for 90 seconds once started. During this time, you can control the vehicle using the following gestures:
    - **Move Forward**: Tilt your head forward and clench your teeth.
    - **Move Backward**: Tilt your head backward and clench your teeth.
    - **Turn Left or Right**: Blink to toggle between turning left and right, then clench your teeth to make the car turn.

## How it Works

### EEG Data Processing

The Muse headband measures EEG signals, which are transmitted to the Raspberry Pi via the Mind Monitor app and the OSC protocol. The `main.py` script processes these signals to detect specific patterns indicating jaw clenching and head orientation.

### Motor Control

The `movement.py` script controls the vehicle's motors based on the processed EEG data:
- **Forward Movement**: Activates the forward motor pins.
- **Backward Movement**: Activates the backward motor pins.
- **Turning**: Activates the appropriate motor pins to turn left or right.

### Distance Measurement

The `distance.py` script uses ultrasonic sensors to measure the distance to obstacles in front of and behind the vehicle. If an obstacle is detected within 10 cm, the vehicle will not move to prevent collisions.

## Code Snippets

### Detecting Head Rotation

The `dataGyro` function in `main.py` detects if the user is tilting their head forward or backward:

```python
def dataGyro(none: float, accForBack: float, accLeftRight: float, accZ: float):
    global turn_drive_toggle, forward_Back, limitDrive, limiter
    if accForBack > 0.5:  # Detect head tilting forward
        turn_drive_toggle = True
        if not forward_Back or limitDrive:
            forward_Back = True
            limitDrive = False
            limiter = True
            print("Forward")
    elif accForBack < -0.5:  # Detect head tilting backward
        turn_drive_toggle = True
        if forward_Back or limitDrive:
            forward_Back = False
            limitDrive = False
            limiter = True
            print("Backward")
```
In this function, the `accForBack` parameter represents the forward-backward tilt of the head. If the value is greater than 0.5, it indicates a forward tilt; if less than -0.5, it indicates a backward tilt. The function then sets the appropriate global variables and prints the direction of movement.

### Detecting Jaw Clenching

Jaw clenching is detected through FFT analysis of EEG signals:

```python
def action(eegTP9, eegAF7, eegAF8, eegTP10):
    global eegAF7Array, timeArray, turn_drive_toggle, left_right_toggle, limitDrive, forward_Back, limiter

    average = 0

    yf = rfft(eegAF7Array[:sample])
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

    #...

    if average >= 25:
        if turn_drive_toggle:
            if forward_Back:
                m.forward(1)
            else:
                m.reverse(1)
        else:
            if left_right_toggle:
                m.right(1)
            else:
                m.left(1)
```
In this function, EEG data is continuously collected and stored in arrays. When the length of the array exceeds 2048, older data is discarded to keep the array size constant. The FFT is performed on the EEG data to analyze its frequency components. The power spectral density (PSD) is calculated, and the average power in the 20-30 Hz range is used to detect jaw clenching. If the average power exceeds a threshold (25 in this case), the vehicle moves based on the current mode (forward/backward or left/right).

### Detecting Blinks

A blink is detected by identifying a high EEG signal followed by a low signal:

```python
for i in range(len(eegAF7Array)):
    if float(eegAF7Array[i]) > 1050.0:  # Detect high EEG signal
        high1000 = True
        indexRemember = i
        break
if high1000:
    for i in range(indexRemember, len(eegAF7Array)):
        if float(eegAF7Array[i]) < 700.0:  # Detect subsequent low EEG signal
            low9000 = True
            break
if high1000 and low9000 and not limiter:
    turn_drive_toggle = False
    limitDrive = True
    left_right_toggle = not left_right_toggle
    print("Left" if not left_right_toggle else "Right")
```
This code iterates through the EEG data to detect a blink by finding a high signal (greater than 1050.0) followed by a low signal (less than 700.0). If both conditions are met and the limiter is not active, it toggles the turning mode (left or right) and prints the current direction.

## Expected Output

When running `main.py`, you should observe the following behaviors:

1. **Connection Confirmation**:
   - The script should print a confirmation that it has connected to the Muse headband and is receiving EEG data:
   ```
    Staring now!
    Serving on ('192.168.1.100', 5000)
    STARTED COUNT DOWN
    Current state: RIGHT
    Blink to change rotation
    Tilt head forward to go forward
    Tilt head backward to go backwards
    Forward
    Right
    Backward
    Left
    ```

2. **Vehicle Movement**:
   - **Forward Movement**: When you tilt your head forward and clench your teeth, the vehicle should move forward. The script should print "Forward".
   - **Backward Movement**: When you tilt your head backward and clench your teeth, the vehicle should move backward. The script should print "Backward".
   - **Turning**: When you blink, the vehicle should toggle between turning left and right. Clenching your teeth will then make the vehicle turn in the chosen direction. The script should print "Left" or "Right" based on the toggle state.

3. **Obstacle Detection**:
   - The ultrasonic sensors should detect obstacles and prevent the vehicle from moving if an obstacle is within 10 cm. This will help avoid collisions and will be reflected in the script's output.

## Future Work

### Integration of Accelerometer

To enhance the functionality and safety of the vehicle, an accelerometer could be integrated. The accelerometer would help in dynamically adjusting the stopping distance based on the speed of the vehicle. For instance, the faster the vehicle is moving, the greater the stopping distance required. This can prevent collisions and improve overall control. Here’s how it can be implemented:

1. **Hardware Integration**: Connect an accelerometer to the Raspberry Pi and calibrate it to measure the vehicle's speed.
2. **Software Update**: Modify the `distance.py` script to adjust the stopping distance based on the accelerometer readings.

### Other Improvements

1. **Enhanced Signal Processing**: Improve the signal processing algorithms for more accurate detection of jaw clenching and head orientation, possibly incorporating machine learning techniques to better interpret EEG data.
2. **User Feedback**: Implement a feedback system (e.g., LED indicators or audio alerts) to notify the user of successful command recognition or errors.
3. **Extended Control Mechanisms**: Introduce additional control gestures, such as nodding or shaking the head, for more complex vehicle maneuvers.
4. **Battery Management**: Integrate a battery management system to monitor and optimize the power usage of the Raspberry Pi and connected peripherals.

## Troubleshooting

- Ensure the Muse headband is properly connected to your smartphone via Bluetooth.
- Verify the Mind Monitor app is correctly configured to send data to your local computer (raspberry pi).
- Check the pin connections for motors and ultrasonic sensors on the Raspberry Pi.
- Ensure the local IP address and port in `main.py` are correctly set.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
