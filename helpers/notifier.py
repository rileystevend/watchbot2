import os
import smtplib
from email.message import EmailMessage

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def send_notification(message):
    msg = EmailMessage()
    msg["Subject"] = "🚨 Undervalued Watch Opportunity Detected"
    msg["From"] = EMAIL_USER
    msg["To"] = RECIPIENT_EMAIL
    msg.set_content(message)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("[notifier] Email sent successfully")
    except Exception as e:
        print(f"[notifier] Failed to send email: {e}")
