from flask import Flask, request
from logic import process_sms

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms():
    sender = request.form.get('sender')
    message = request.form.get('message')
    response = process_sms(sender, message)
    return response

if __name__ == '__main__':
    app.run(debug=True)
