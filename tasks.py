import time

from celery_app import celery
from sender_email import send_email_text


@celery.task
def add_from_tasks(x: int, y: int) -> int:
    print(x + y)
    return x + y

@celery.task
def multiply(x: int, y: int) -> int:
    print(x * y)
    return x * y


@celery.task
def email_send(email: str, product_name: str,) -> str:
    send_email_text(email, product_name)
