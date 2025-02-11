import logging
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

email_conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="HW Systems",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)
fast_mail = FastMail(email_conf)

async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({'sub': email})
        logger.info(f"Token for email {email}: {token_verification}")
        message = MessageSchema(
            subject = "Confirm your email ",
            recipients = [email],
            template_body = {'host': host, 'username': username, 'token': token_verification},
            subtype = MessageType.html
        )
        logger.info(f"Sending email to {email}")
        await fast_mail.send_message(message, template_name="verify_email.html")
        logger.info(f"Email sent successfully to {email}.")
    except ConnectionErrors as err:
        logger.error(f"SMTP connection error: {err}")