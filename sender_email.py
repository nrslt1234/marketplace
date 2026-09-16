import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

def send_email_text(receiver_email: str, product_name: str):
    # данные отправителя (mail.ru)
    sender_email = "ivan_ivanov_ivanovich1234@mail.ru"
    sender_password = os.getenv("EMAILPASSWORD")  # пароль приложения

    # тема и тело письма
    subject = "ДОСТАВКА ВАШЕГО ТОВАРА"
    body = f"✅ ваш товар \"{product_name}\" доставлен"

    # формирование письма
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # подключение к SMTP-серверу mail.ru
        with smtplib.SMTP("smtp.mail.ru", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"✅ ваш товар \"{product_name}\" доставлен")
            return True
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        return False
