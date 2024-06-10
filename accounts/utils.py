import phonenumbers
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def format_phone_number_to_e164(mobile, country_code='SA'):
    """
    Format the given phone number to E.164 format.
    Args:
        mobile (str): The phone number to format.
        country_code (str): The country code to use for formatting. Default is 'SA' for Saudi Arabia.

    Returns:
        str: The formatted phone number in E.164 format.
    """
    parsed_number = phonenumbers.parse(mobile, country_code)
    return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

def send_otp_via_whatsapp(mobile, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    formatted_mobile = format_phone_number_to_e164(mobile)
    try:
        message = client.messages.create(
            body=f'Your OTP is {otp}',
            from_='whatsapp:+14155238886',  # Twilio sandbox number for WhatsApp
            to=f'whatsapp:{formatted_mobile}'
        )
        logger.info(f"WhatsApp Message SID: {message.sid}")
        return message.sid
    except Exception as e:
        logger.error(f"Error sending OTP via WhatsApp: {e}")
        return None
