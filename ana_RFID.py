# KODE RFID yang di hubungkan ke RFID dan jetson nano dengan maksud untuk mengontrol kecepatan motor 

import Jetson.GPIO as GPIO
import time
from serial import Serial

# Pin definitions
ENA = 33  # PWM-1, channel-0
IN1 = 35  # PWM-1, channel-1
IN2 = 37  # This needs to be an ordinary GPIO (non-PWM)
ENB = 32  # PWM-0, channel-1
IN3 = 40  # This needs to be an ordinary GPIO (non-PWM)
IN4 = 38  # This needs to be an ordinary GPIO (non-PWM)

# Set GPIO mode
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# Initialize PWM for motors A and B
pwm_A = GPIO.PWM(ENA, 100)  # PWM frequency: 100Hz
pwm_B = GPIO.PWM(ENB, 100)

# Start PWM with a duty cycle of 0%
pwm_A.start(0)
pwm_B.start(0)

# Set direction of motors to forward
GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)
GPIO.output(IN3, GPIO.HIGH)
GPIO.output(IN4, GPIO.LOW)

# Initialize Serial Port for RFID
rfid_serial = Serial('/dev/ttyUSB0', 115200, timeout=0.1) # Serial can be set according to the set up, then to see the serial can use "ls -l /dev/" (pay attention to the date)

# Function to send RFID command and read response
def send_rfid_cmd(cmd):
    data = bytes.fromhex(cmd)
    rfid_serial.write(data)
    response = rfid_serial.read(512)
    response_hex = response.hex().upper()
    hex_list = [response_hex[i:i+2] for i in range(0, len(response_hex), 2)]
    hex_space = ' '.join(hex_list)
    return hex_space

try:
    while True:
        # Read RFID tag
        tag_data = send_rfid_cmd('BB 00 22 00 00 22 7E')
        # Convert RFID response to detected tag
        if '6C DC B9 33' in tag_data:  # Tag 1
            speed = 30
        elif '88 DD 43 D1' in tag_data:  # Tag 2
            speed = 10
        elif 'E8 DC 42 5E' in tag_data:  # Tag 3
            speed = 0
        else:
            # If tag is not recognized, use default speed
            speed = 30
        
        # Set speed for motors A and B
        pwm_A.ChangeDutyCycle(speed)
        pwm_B.ChangeDutyCycle(speed)

except KeyboardInterrupt:
    # Stop PWM and clean up GPIO pins when the program stops
    pwm_A.stop()
    pwm_B.stop()
    GPIO.cleanup()
