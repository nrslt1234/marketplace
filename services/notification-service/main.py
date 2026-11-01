import json
import os
import uuid

import pika
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE = os.getenv("QUEUE", "notifications.created")


class Notification(BaseModel):
    user_id: int
    text: str
    order_id: str | None = None
    email: str | None = None


@app.post("/notifications", status_code=status.HTTP_202_ACCEPTED)
def create_notification(notification: Notification) -> dict:
    event = {
        "event_type": "notification.created",
        "notification_id": str(uuid.uuid4()),
        **notification.model_dump(),
    }
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        try:
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=QUEUE,
                body=json.dumps(event).encode(),
                properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
            )
        finally:
            connection.close()
    except pika.exceptions.AMQPError as exc:
        raise HTTPException(status_code=503, detail="RabbitMQ unavailable") from exc

    return {"notification_id": event["notification_id"], "status": "queued"}