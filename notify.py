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

# hospital is boolean specifying if message is for hospital (true) or provider (false),  status is package "prep", "transit", or "arrived" update, source is who is sending, source is person who is sending message, quantity and type specify nature of package
    def send_notif(self, hospital, status, source, quantity, supply):
        return self.sms.messages.create(
            from_=self.twilio_number,
            to=self.to_number,
            if hospital:
            if status == prep:
            body="Your order from " + source + " of " + quantity +
            " " + supply + "s" + " has been recieved."
            elif status == transit
            body="Your package from " + source + " of " + quantity +
            " " + supply + "s" + " is on route! Hold tight!"
            else:
            body="Hooray! Your package of " + quantity + " " +
            supply + " from " + source + " has arrived!"
            else:
            if status == prep:
            body="Your order to " + source + " of " + quantity +
            " " + supply + "s" + " is being processed."
            elif status == transit
            body="Your package to " + source + " of " +
            quantity + " " + supply + "s" + " has been shipped"
            else:
            body="Hooray! Your package to " + quantity + " " +
            supply + " from " + source + " was delivered!"
                else: )
