import serial

# Configure the serial port to communicate with the SIM800C
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

def send_at_command(command):
    ser.write((command + '\r\n').encode())
    response = ser.read(100).decode()
    return response

def process_sms(sender, message):
    if message.lower() == 'turn on':
        send_at_command('AT+RELAY=1')
        return 'Relay turned on'
    elif message.lower() == 'turn off':
        send_at_command('AT+RELAY=0')
        return 'Relay turned off'
    else:
        return 'Unknown command'

# Initialize the SIM800C module
send_at_command('AT')
send_at_command('AT+CMGF=1')  # Set SMS text mode
send_at_command('AT+CNMI=1,2,0,0,0')  # Configure to receive SMS automatically

