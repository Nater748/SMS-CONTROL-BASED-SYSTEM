import RPi.GPIO as GPIO
import serial
import time

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin to monitor
GPIO_PIN = 17

# Setup GPIO pin for input (detecting SIM800C connection)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Function to check if the SIM800C is plugged in
def is_sim800c_connected():
    # Check if the GPIO pin is HIGH (SIM800C connected)
    if GPIO.input(GPIO_PIN) == GPIO.HIGH:
        return True
    return False

# Function to check if SIM800C responds on the serial port
def check_serial_port():
    try:
        # Try to initialize the serial connection with SIM800C
        ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)
        time.sleep(2)  # Wait for SIM800C to initialize
        if ser.isOpen():
            ser.write(b'AT\r\n')  # Send basic AT command to check communication
            time.sleep(1)
            response = ser.read(100)  # Read response from the SIM800C
            if b'OK' in response:
                ser.close()
                return True
        ser.close()
    except Exception as e:
        print(f"Error: {e}")
    return False
