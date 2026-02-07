from twilio.rest import Client

from .config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM


_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_whatsapp(to_user: str, text: str) -> str:
    msg = _client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        to=to_user,
        body=text,
    )
    return msg.sid

