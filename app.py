from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from utils import fetch_reply

import re

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""

    # Fetch the message
    msg = request.form.get('Body')
    sender = request.form.get('From')

    # Create reply
    resp = MessagingResponse()
    text,reply = fetch_reply(msg,sender)

    if text=='img':
        resp.message(reply).media(reply)
    else:
        resp.message(reply) 
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)