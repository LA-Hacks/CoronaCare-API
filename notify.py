from twilio.rest import Client


class Notifier:
    def __init__(self, args):
        # Create the twilio client
        try:
            self.sms = Client(args.get('twilio_auth'), args.get('twilio_sid'))
        except:
            raise Exception("Twilio Client Creation Error")

        self.twilio_number = args.get('twilio_number')
        self.to_number = args.get('to_number')

# status is package "prep", "transit", or "arrived" update, source is who is sending, source is person who is sending message, quantity and type specify nature of package
    def send_notif(self, status, source, quantity, supply):
        return self.sms.messages.create(
            from_=self.twilio_number,
            to=self.to_number,
            if status == "prep":
                body="Your order with " + source + " of " + quantity +
            " " + supply + "s" + " has been recieved."
            elif status == "transit":
                body="Your package with " + source + " of " + quantity +
            " " + supply + "s" + " is on route! Hold tight!"
            else:
                body="Hooray! Your package of " + quantity + " " +
            supply + " with " + source + " was delivered!"
        )
