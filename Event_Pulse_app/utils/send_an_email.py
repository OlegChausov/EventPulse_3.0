import os

from email.mime.text import MIMEText

import aiosmtplib
from dotenv import load_dotenv

load_dotenv()  # загружает .env

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")



async def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_LOGIN
    msg["To"] = to_email

    await aiosmtplib.send(
        msg,
        hostname=SMTP_SERVER,
        port=SMTP_PORT,
        username=SMTP_LOGIN,
        password=SMTP_PASSWORD,
        use_tls=True,
    )

    return {"status": "ok", "message": f"Письмо отправлено на {to_email}"}
