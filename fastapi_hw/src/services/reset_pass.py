import logging

from fastapi_mail import MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.services.email import fast_mail

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_email_pass(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_reset_password_token({'sub': email})
        logger.info(f"Token for email {email}: {token_verification}")
        message = MessageSchema(
            subject = "Password Reset Request - HW Systems ",
            recipients = [email],
            template_body = {'host': host, 'username': username, 'token': token_verification},
            subtype = MessageType.html
        )
        logger.info(f"Sending password reset email to {email}")
        await fast_mail.send_message(message, template_name="reset_password.html")
        logger.info(f"Password reset email sent successfully to {email}.")
    except ConnectionErrors as err:
        logger.error(f"SMTP connection error: {err}")
    except Exception as err:
        logger.error(f"Unexpected error: {err}")
        raise
