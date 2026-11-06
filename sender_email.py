import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = "ivan_ivanov_ivanovich1234@mail.ru"


def send_email(receiver_email: str, subject: str, body: str) -> bool:
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    for attempt in range(1, 4):
        try:
            with smtplib.SMTP_SSL("smtp.mail.ru", 465, timeout=20) as server:
                server.login(SENDER_EMAIL, os.getenv("EMAILPASSWORD"))
                server.send_message(msg)
                print(f"✅ Письмо отправлено на {receiver_email}", flush=True)
                return True
        except Exception as e:
            print(f"❌ Попытка {attempt} не удалась: {e}", flush=True)
            time.sleep(2)
    return False


def send_email_text(receiver_email: str, product_name: str) -> bool:
    return send_email(
        receiver_email,
        "ДОСТАВКА ВАШЕГО ТОВАРА",
        f'✅ ваш товар "{product_name}" доставлен',
    )
