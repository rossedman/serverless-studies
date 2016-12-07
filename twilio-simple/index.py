import os
from twilio.rest import TwilioRestClient

def prompt(event, context):
    """Send Message"""
    twilio_sid = os.environ['TWILIO_SID']
    twilio_token = os.environ['TWILIO_TOKEN']
    client = TwilioRestClient(twilio_sid, twilio_token)
    message = client.messages.create(body="Hello from Python",
                                     to="+12147332344",
                                     from_="+14698045056")

    return {
        'message' : message.sid
    }
