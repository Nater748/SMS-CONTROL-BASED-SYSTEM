import time
import logging
import serial
import RPi.GPIO as GPIO

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Relay Pin
RELAY_PIN = 17  # GPIO pin where the relay is connected

# Initialize GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay is initially OFF

class SMSControlSystem:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        """Connect to SIM800C module via serial port"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(1)  # Allow module to initialize
            logging.info(f"Connected to SIM800C module on port {self.port}.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to SIM800C: {e}")
            return False

    def send_at_command(self, command, expected_response="OK", timeout=5):
        """Send an AT command and wait for response"""
        if not self.ser:
            raise Exception("SIM800C module is not connected.")
        
        try:
            self.ser.write((command + "\r\n").encode())
            time.sleep(timeout)
            response = self.ser.read_all().decode().strip()
            if expected_response in response:
                return response
            else:
                logging.warning(f"Unexpected response: {response}")
                return None
        except Exception as e:
            logging.error(f"Error sending AT command: {e}")
            return None

    def check_inbox(self):
        """Check the SMS inbox for new messages"""
        response = self.send_at_command('AT+CMGL="ALL"')  # List all messages in the inbox
        if response:
            messages = self.parse_sms(response)
            for message in messages:
                if message.get("message"):
                    self.process_sms_command(message['message'])

    def parse_sms(self, response):
        """Parse the response from AT+CMGL command"""
        messages = []
        lines = response.strip().split('\r\n')
        for i in range(0, len(lines), 2):
            message_info = lines[i].split(',')
            if len(message_info) > 1:
                index = int(message_info[0].split(":")[1].strip())
                sender = message_info[1].strip('"')
                date = message_info[3].strip('"')
                message = lines[i+1].strip()
                messages.append({
                    'index': index,
                    'sender': sender,
                    'date': date,
                    'message': message
                })
        return messages

    def process_sms_command(self, command):
        """Process the SMS command to control the relay"""
        command = command.strip().lower()
        if 'turn_on' in command:
            logging.info("Turning on the relay.")
            GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn on relay
        elif 'turn_off' in command:
            logging.info("Turning off the relay.")
            GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off relay
        else:
            logging.warning(f"Unknown command: {command}")

    def listen_for_sms(self):
        """Continuously check for SMS commands"""
        logging.info("Listening for incoming SMS messages...")
        while True:
            self.check_inbox()
            time.sleep(5)  # Delay before checking again

    def close(self):
        """Clean up GPIO and close serial connection"""
        GPIO.cleanup()
        if self.ser:
            self.ser.close()
            logging.info("Disconnected from SIM800C module.")

if __name__ == "__main__":
    # Initialize and connect to SIM800C module
    sms_system = SMSControlSystem(port='/dev/ttyUSB0')
    
    if sms_system.connect():
        try:
            sms_system.listen_for_sms()  # Start listening for SMS
        except KeyboardInterrupt:
            logging.info("SMS Control System interrupted by user.")
        finally:
            sms_system.close()  # Clean up GPIO and serial connection
    else:
        logging.error("Failed to connect to SIM800C.")
