import time

from celery_app import celery


@celery.task
def add_from_tasks(x: int, y: int) -> int:
    print(x + y)
    return x + y