import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

def send_email_html(receiver_email: str, product_information_for_html: list):
    # данные отправителя (mail.ru)
    sender_email = "ivan_ivanov_ivanovich1234@mail.ru"
    sender_password = os.getenv("EMAILPASSWORD")  # пароль приложения

    # тема и тело письма
    subject = "ДОСТАВКА ВАШЕГО ТОВАРА"
    body = f"✅ ваш товар доставлен"

    # формирование письма
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject


    try:
        # with open("templates/smtphtmlscript.html", "r", encoding="utf-8") as file:
        #     html = file.read()
        with open("templates/smtphtmlscript.html", "r", encoding="utf-8") as file:
            template = Template(file.read())

        html = template.render(
            product_information_for_html = product_information_for_html
        )

    except FileNotFoundError:
        print("❌ Ошибка: Файл smtphtmlscript.html не найден ")
        return False


    message.attach(MIMEText(body, "plain", "utf-8"))


    html_part = MIMEText(html, "html", "utf-8")
    message.attach(html_part)

    try:
        # подключение к SMTP-серверу mail.ru
        with smtplib.SMTP("smtp.mail.ru", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            print(f"✅ Письмо с товаром \"{product_name}\" успешно отправлено")
            return True
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        return False