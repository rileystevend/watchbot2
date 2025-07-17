import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger('notifier')

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def send_notification(message):
    try:
        msg = EmailMessage()
        msg["Subject"] = "🚨 Undervalued Watch Opportunity Detected"
        msg["From"] = EMAIL_USER
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content(message)

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info("Email sent successfully")
    except Exception as email_err:
        logger.error(f"Failed to send email: {email_err}")
