import json
import os
import time

import pika

from sender_email import SENDER_EMAIL, send_email

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://app_user:app_pass@rabbitmq:5672/")
QUEUE = os.getenv("QUEUE", "notifications.created")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "")


def handle(channel, method, properties, body):
    try:
        data = json.loads(body)
        email = data.get("email") or NOTIFY_EMAIL or SENDER_EMAIL
        text = data.get("text") or data.get("product_name") or "Новое уведомление"

        ok = send_email(email, "Новое уведомление", text)
        if ok:
            print("Уведомление отправлено:", email, flush=True)
            channel.basic_ack(method.delivery_tag)
        else:
            print("Не удалось отправить письмо:", email, flush=True)
            channel.basic_nack(method.delivery_tag, requeue=False)
    except Exception as exc:
        print("Ошибка обработки сообщения:", exc, flush=True)
        channel.basic_nack(method.delivery_tag, requeue=False)


def run_consumer_rabbit():
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        except pika.exceptions.AMQPError as exc:
            print("RabbitMQ недоступен, повтор через 3 секунды:", exc)
            time.sleep(3)
            continue

        channel = connection.channel()
        channel.queue_declare(queue=QUEUE, durable=True)
        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(queue=QUEUE, on_message_callback=handle)
        print("Консьюмер RabbitMQ запущен, очередь:", QUEUE)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
            return
        except pika.exceptions.AMQPError as exc:
            print("Соединение с RabbitMQ потеряно, переподключаюсь:", exc)
            try:
                connection.close()
            except Exception:
                pass
            time.sleep(3)
