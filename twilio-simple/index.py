
from twilio.rest import TwilioRestClient

def prompt(event, context):
    """Send Message"""
    twilio_sid = "ACd3892af82809c0858ad0bd252b69b4e3"
    twilio_token = "cd21f2f0165303bb48ef84ab87b174ae"
    twilio_number = "+14698045056"

    client = TwilioRestClient(twilio_sid, twilio_token)

    message = client.messages.create(body="Hello from Python",
                                     to="+12147332344",
                                     from_=twilio_number)

    print message.sid
    print event
    print context
