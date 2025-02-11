from flask import Flask, jsonify
from logic import is_sim800c_connected, check_serial_port

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the SMS System!"

@app.route('/check_sim800c', methods=['GET'])
def check_sim800c():
    # Check if the SIM800C is connected by GPIO
    if is_sim800c_connected():
        return jsonify({'status': 'connected', 'message': 'SIM800C is plugged in.'})
    
    # Optionally, also check serial communication
    if check_serial_port():
        return jsonify({'status': 'connected', 'message': 'SIM800C is responding to AT commands.'})
    
    return jsonify({'status': 'disconnected', 'message': 'SIM800C is not connected or not responding.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
